#!/usr/bin/env python3
"""
I-MAK pricing engine.

Builds an itemized quote for an I-MAK unit from the structured price data in
pricing/data/imak_pricing.db:

    base unit (gearbox+motor, foot or flange)
  + brake            (EMF, matched by torque + mounting variant)
  + option adders    (%-based from catalogue notes, see config.json)
  ---------------------------------------------------------------
  = list subtotal
  -> margin           (discount off list  OR  cost + markup)
  -> payment term     (surcharge % for deferred payment)
  -> VAT              (optional)
  = customer total    (in TL / EUR / USD)

Usage:
    python pricer.py search "İRM 82"                 # find matching units
    python pricer.py quote --type "İRM 82" --currency TL --mount foot \\
                           --brake --term 30d --customer DEALER_A
"""
import argparse, json, os, re, sqlite3, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
DB   = os.path.join(ROOT, "..", "data", "imak_pricing.db")
CFG  = os.path.join(ROOT, "config.json")


def load_config(path=CFG):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def connect(db=DB):
    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row
    return con


def _f(x):
    """Parse a price string to float; returns None for non-numeric ('Standart','-','')."""
    if x is None:
        return None
    s = str(x).strip()
    if not s or s in ("-", "Standart", "Standard"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


# ----------------------------------------------------------------------------- search
def search_units(con, term, currency="TL", limit=25):
    q = ("SELECT series, power_kw, output_rpm, type_full, gearbox, motor, "
         "price_foot, price_flange FROM imak_geared_motors "
         "WHERE currency=? AND type_full LIKE ? LIMIT ?")
    return con.execute(q, (currency, f"%{term}%", limit)).fetchall()


def find_unit(con, type_full, currency="TL"):
    """Exact-ish match on type_full (first exact, else first LIKE)."""
    row = con.execute(
        "SELECT * FROM imak_geared_motors WHERE currency=? AND type_full=? LIMIT 1",
        (currency, type_full)).fetchone()
    if row:
        return row
    rows = search_units(con, type_full, currency, limit=1)
    return rows[0] if rows else None


# ----------------------------------------------------------------------------- brakes
def _torque_hi(s):
    m = re.findall(r"\d+", s or "")
    return int(m[-1]) if m else 0


def find_brake(con, required_torque_nm, currency="TL", variant=None, family="YBF"):
    """Smallest brake whose torque range covers required_torque_nm."""
    rows = con.execute(
        "SELECT code, torque_nm, price_variant, currency, price FROM emf_brakes "
        "WHERE code LIKE ? AND currency=?", (f"{family}%", currency)).fetchall()
    cand = []
    for r in rows:
        hi = _torque_hi(r["torque_nm"])
        if hi >= (required_torque_nm or 0) and _f(r["price"]) is not None:
            if variant is None or variant.upper() in (r["price_variant"] or "").upper():
                cand.append((hi, r))
    if not cand:
        return None
    cand.sort(key=lambda t: t[0])
    return cand[0][1]


# ----------------------------------------------------------------------------- quote
def build_quote(con, cfg, *, type_full, currency="TL", mount="foot",
                options=None, brake=False, brake_torque=None,
                term="cash", customer="LIST", with_vat=False):
    options = options or []
    unit = find_unit(con, type_full, currency)
    if not unit:
        raise ValueError(f"No unit found for '{type_full}' in {currency}")

    base = _f(unit["price_foot"] if mount == "foot" else unit["price_flange"])
    if base is None:
        raise ValueError(f"Unit '{unit['type_full']}' has no {mount} price "
                         f"(value: {unit['price_foot'] if mount=='foot' else unit['price_flange']})")

    motor_price = 0.0  # geared-motor base already includes the motor
    lines = [{"item": f"{unit['type_full']} ({mount})", "qty": 1, "amount": base}]

    # brake
    if brake:
        tq = brake_torque or _torque_hi(unit["output_rpm"]) or 100
        var = cfg.get("brake_default_variant")
        b = find_brake(con, tq, currency if currency != "USD" else "TL", var)
        if b:
            lines.append({"item": f"Brake {b['code']} [{b['price_variant']}] tq~{tq}Nm",
                          "qty": 1, "amount": _f(b["price"]) or 0.0})
        else:
            lines.append({"item": f"Brake (no match for ~{tq}Nm in {currency})",
                          "qty": 1, "amount": 0.0})

    # option adders (% of a referenced base)
    rules = cfg.get("option_rules", {})
    bases = {"unit": base, "flange": _f(unit["price_flange"]) or base,
             "motor": motor_price or base, "brake": lines[1]["amount"] if brake and len(lines) > 1 else 0.0}
    for opt in options:
        rule = rules.get(opt)
        if not rule:
            lines.append({"item": f"[unknown option '{opt}']", "qty": 1, "amount": 0.0})
            continue
        if "pct" in rule:
            amt = bases.get(rule.get("base", "unit"), base) * rule["pct"] / 100.0
            lines.append({"item": f"{opt} (+{rule['pct']}% of {rule.get('base','unit')})",
                          "qty": 1, "amount": amt})
        elif "flat_per_litre" in rule:
            per = rule["flat_per_litre"].get(currency, 0.0)
            lines.append({"item": f"{opt} ({per} {currency}/L, qty 1L assumed)",
                          "qty": 1, "amount": per})

    list_subtotal = sum(l["amount"] for l in lines)

    # margin
    tier = cfg.get("customer_tiers", {}).get(customer) or cfg["margin"]
    mode = tier.get("mode", cfg["margin"]["mode"])
    if mode == "discount":
        rate = tier.get("discount_pct", 0.0)
        after_margin = list_subtotal * (1 - rate / 100.0)
        margin_line = f"discount -{rate}%"
    else:
        rate = tier.get("markup_pct", 0.0)
        after_margin = list_subtotal * (1 + rate / 100.0)
        margin_line = f"markup +{rate}%"

    # payment term surcharge
    term_rate = cfg.get("payment_terms", {}).get(currency, {}).get(term, 0.0)
    after_term = after_margin * (1 + term_rate / 100.0)

    # VAT
    vat_rate = cfg.get("vat_pct", 0.0) if with_vat else 0.0
    total = after_term * (1 + vat_rate / 100.0)

    return {
        "unit": unit["type_full"], "currency": currency, "mount": mount,
        "lines": lines, "list_subtotal": list_subtotal,
        "margin": margin_line, "after_margin": after_margin,
        "term": f"{term} (+{term_rate}%)", "after_term": after_term,
        "vat": f"+{vat_rate}%" if with_vat else "excluded", "total": total,
    }


def fmt(q):
    cur = q["currency"]
    out = [f"\nQUOTE — {q['unit']}  [{q['mount']}]  ({cur})", "-" * 58]
    for l in q["lines"]:
        out.append(f"  {l['item'][:44]:<44} {l['amount']:>12,.2f}")
    out += ["-" * 58,
            f"  {'List subtotal':<44} {q['list_subtotal']:>12,.2f}",
            f"  {'After ' + q['margin']:<44} {q['after_margin']:>12,.2f}",
            f"  {'After term ' + q['term']:<44} {q['after_term']:>12,.2f}",
            f"  {'VAT ' + q['vat']:<44} {'':>12}",
            "=" * 58,
            f"  {'TOTAL':<44} {q['total']:>12,.2f} {cur}"]
    return "\n".join(out)


# ----------------------------------------------------------------------------- CLI
def main(argv=None):
    ap = argparse.ArgumentParser(description="I-MAK pricing engine")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search"); s.add_argument("term"); s.add_argument("--currency", default="TL")

    p = sub.add_parser("quote")
    p.add_argument("--type", required=True)
    p.add_argument("--currency", default="TL")
    p.add_argument("--mount", default="foot", choices=["foot", "flange"])
    p.add_argument("--brake", action="store_true")
    p.add_argument("--brake-torque", type=int, default=None)
    p.add_argument("--option", action="append", default=[], dest="options")
    p.add_argument("--term", default="cash")
    p.add_argument("--customer", default="LIST")
    p.add_argument("--vat", action="store_true")

    a = ap.parse_args(argv)
    cfg = load_config(); con = connect()
    if a.cmd == "search":
        rows = search_units(con, a.term, a.currency)
        if not rows:
            print("no matches"); return
        for r in rows:
            print(f"  {r['type_full']:<32} {r['power_kw']}kW  out {r['output_rpm']}  "
                  f"foot={r['price_foot']} flange={r['price_flange']} {a.currency}")
    else:
        q = build_quote(con, cfg, type_full=a.type, currency=a.currency, mount=a.mount,
                        options=a.options, brake=a.brake, brake_torque=a.brake_torque,
                        term=a.term, customer=a.customer, with_vat=a.vat)
        print(fmt(q))


if __name__ == "__main__":
    main()
