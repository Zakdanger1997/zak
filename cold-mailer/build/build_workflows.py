# -*- coding: utf-8 -*-
"""يولّد 5 ملفات workflow (حساب لكل واحد) لنظام الإيميلات الشخصية."""
import json, os

OUT_DIR = '/home/user/zak/cold-mailer/workflows'
os.makedirs(OUT_DIR, exist_ok=True)

# ---------- برومبت الوكيل ----------
SYSTEM_MESSAGE = (
    "أنت شخص حقيقي يعمل في شركة ويكتب رسالة إيميل قصيرة وشخصية إلى شخص واحد بعينه. "
    "لست مسوّقاً ولا تكتب إعلاناً؛ تكتب كأنك تراسل زميلاً في المجال لأول مرة.\n\n"
    "اللغة: إن كانت منطقة المستلم تركية (İstanbul, Ankara, İzmir, Bursa...) فاكتب بالتركية. "
    "إن كانت عربية (الرياض, جدة, دبي, القاهرة...) فاكتب بالعربية. غير ذلك اكتب بالإنجليزية.\n\n"
    "قواعد صارمة (نبرة شخصية):\n"
    "1. الطول 50–80 كلمة فقط، 3–4 جمل.\n"
    "2. رسمي معتدل: محترم ومهني لكن إنساني وطبيعي، بلا تكلّف ولا مبالغة.\n"
    "3. أول جملة تخصيص حقيقي يذكر شيئاً محدداً عن الشركة أو المنصب أو الملاحظة الخاصة، لا افتتاحية عامة.\n"
    "4. جملة أو جملتان عن الغرض بشكل مباشر بسيط.\n"
    "5. اختم بسؤال واحد قصير يسهل الرد عليه (لا عرض تسويقي).\n"
    "6. أضف بعد السؤال جملة انسحاب إنسانية ناعمة (عربي: «ولو الموضوع ما يناسبك ردّ بكلمة وما أزعجك»؛ وبما يناسب بالتركية/الإنجليزية).\n\n"
    "ممنوعات (لا تستخدمها إطلاقاً): «أتمنى أن يصلك إيميلي وأنت بخير»/'I hope this email finds you well'/'Umarım iyisinizdir'؛ "
    "«أردت التواصل»/'I wanted to reach out'؛ لغة مبيعات («عرض خاص»، «حصري»، «الآن فقط»، 'exclusive')؛ "
    "«علاوة على ذلك»/«في الختام»/'Furthermore'؛ إيموجي ورموز و Markdown وعناوين وشرطات em طويلة.\n\n"
    "لا تكتب توقيعاً؛ سيُضاف تلقائياً.\n\n"
    "المخرجات: أعد JSON فقط بلا أي نص خارجه بهذا الشكل: {\"subject\": \"...\", \"body\": \"...\"}. "
    "subject من 2–4 كلمات شخصي وقصير بلا رموز. body نص الرسالة فقط بلا توقيع."
)

SET = 'إعدادات الإرسال'
AGENT_TEXT = (
    "=اكتب رسالة إيميل حسب التعليمات.\n"
    "الغرض: {{ $('" + SET + "').first().json.offer }}\n"
    "المستلم:\n"
    "- الاسم: {{ $json.first_name }}\n"
    "- الشركة: {{ $json.company }}\n"
    "- المنصب: {{ $json.title }}\n"
    "- المنطقة: {{ $json.region }}\n"
    "- ملاحظة: {{ $json.custom1 }}"
)

# ---------- أكواد Code nodes ----------
JS_FILTER = r"""
const cfg = $('إعدادات الإرسال').first().json;
const list = $('استخراج القائمة').all().map(i => i.json).filter(r => r && r.email);
const sent = $('استخراج السجل').all().map(i => i.json).filter(r => r && r.email);

const regions = String(cfg.my_region || '').split(',').map(s => s.trim().toLowerCase()).filter(Boolean);
const sentSet = new Set(sent.map(r => String(r.email).toLowerCase()));
const today = new Date().toISOString().slice(0, 10);
const sentToday = sent.filter(r => String(r.tarih || '').slice(0, 10) === today).length;
const remaining = Math.max(0, Number(cfg.daily_limit || 40) - sentToday);
if (remaining <= 0) return [];
const batch = Math.min(Number(cfg.batch_size || 8), remaining);

const out = [];
const seen = new Set();
for (const row of list) {
  const email = String(row.email || '').trim().toLowerCase();
  if (!email || !email.includes('@')) continue;
  const region = String(row.region || '').trim().toLowerCase();
  if (regions.length && !regions.includes(region)) continue;
  if (sentSet.has(email) || seen.has(email)) continue;
  seen.add(email);
  out.push({ json: { ...row, email } });
  if (out.length >= batch) break;
}
return out;
""".strip()

JS_BUILD = r"""
const cfg = $('إعدادات الإرسال').first().json;
const rec = $('تصفية وتحضير').item.json;

let sig = '';
try {
  const sigs = $('استخراج التواقيع').all().map(i => i.json);
  const row = sigs.find(s => String(s.account).trim() === String(cfg.my_account).trim());
  sig = row ? String(row.signature) : '';
} catch (e) {}
sig = sig.replace(/\\n/g, '\n');

let raw = String($json.output ?? $json.text ?? '');
const m = raw.match(/\{[\s\S]*\}/);
let p = {};
try { p = JSON.parse(m ? m[0] : raw); } catch (e) { p = { subject: '', body: raw }; }

const subject = (p.subject || '').trim() || 'تواصل';
const body = (p.body || '').trim() + (sig ? '\n\n' + sig : '');

return { json: { email: rec.email, first_name: rec.first_name || '', company: rec.company || '', region: rec.region || '', subject, body } };
""".strip()

JS_LOGROW = r"""
const rec = $('بناء الرسالة').item.json;
const now = new Date().toISOString().slice(0, 16).replace('T', ' ');
return { json: { tarih: now, email: rec.email, region: rec.region || '', firma: rec.company || '', konu: rec.subject || '', durum: 'GONDERILDI' } };
""".strip()

JS_MERGE = r"""
const old = $('استخراج السجل').all().map(i => i.json).filter(r => r && r.email);
const neu = $input.all().map(i => i.json);
return [...old, ...neu].map(r => ({ json: r }));
""".strip()

JS_NOTIFY = r"""
const j = $json;
const from = j.from || (j.headers && j.headers.from) || '';
const subject = j.subject || '(بلا موضوع)';
const snippet = String(j.textPlain || j.text || '').replace(/\s+/g, ' ').slice(0, 300);
const cfg = $('إعدادات الردود').first().json;
const text = '📬 رد جديد على ' + cfg.my_account + '\n\nمن: ' + from + '\nالموضوع: ' + subject + '\n\n' + snippet;
return { json: { text, subject: 'رد جديد على ' + cfg.my_account } };
""".strip()

JS_REPORT = r"""
const cfg = $('إعدادات التقرير').first().json;
const rows = $('استخراج سجل التقرير').all().map(i => i.json).filter(r => r && r.email);
const today = new Date().toISOString().slice(0, 10);
const t = rows.filter(r => String(r.tarih || '').slice(0, 10) === today).length;
const text = 'تقرير ' + cfg.my_account + ' — ' + today + '\n\n'
  + 'أُرسل اليوم: ' + t + '\n'
  + 'إجمالي المُرسَل (كل الوقت): ' + rows.length + '\n'
  + 'المنطقة: ' + cfg.my_region;
return { json: { text, subject: 'تقرير ' + cfg.my_account + ' ' + today } };
""".strip()


def n(name, ntype, ver, pos, params, extra=None):
    node = {"parameters": params, "id": name, "name": name, "type": ntype, "typeVersion": ver, "position": pos}
    if extra:
        node.update(extra)
    return node


def code(name, js, pos, mode_each=False):
    p = {"jsCode": js}
    if mode_each:
        p = {"mode": "runOnceForEachItem", "jsCode": js}
    return n(name, "n8n-nodes-base.code", 2, pos, p)


def sched(name, cron, pos):
    return n(name, "n8n-nodes-base.scheduleTrigger", 1.2, pos,
             {"rule": {"interval": [{"field": "cronExpression", "expression": cron}]}})


def read_file(name, path_expr, pos):
    return n(name, "n8n-nodes-base.readWriteFile", 1, pos,
             {"operation": "read", "fileSelector": path_expr, "options": {}},
             {"onError": "continueRegularOutput"})


def extract(name, pos):
    return n(name, "n8n-nodes-base.extractFromFile", 1, pos,
             {"operation": "csv", "binaryPropertyName": "data", "options": {}},
             {"onError": "continueRegularOutput"})


def build_account(idx, region_placeholder):
    acc = f"account{idx}"
    smtp_cred = {"smtp": {"id": f"smtp-{acc}", "name": f"SMTP {acc}"}}
    imap_cred = {"imap": {"id": f"imap-{acc}", "name": f"IMAP {acc}"}}
    openai_cred = {"openAiApi": {"id": "openai-cred", "name": "OpenAI"}}

    nodes = []
    C = nodes.append

    # ===== SEND BRANCH =====
    C(sched("جدول الإرسال", "0 9-16 * * 1-5", [-1100, 200]))
    C(n(SET, "n8n-nodes-base.set", 3.4, [-900, 200], {
        "assignments": {"assignments": [
            {"id": "a1", "name": "my_account", "value": acc, "type": "string"},
            {"id": "a2", "name": "my_region", "value": region_placeholder, "type": "string"},
            {"id": "a3", "name": "from_email", "value": f"BURAYA_{acc}_EMAIL", "type": "string"},
            {"id": "a4", "name": "daily_limit", "value": 40, "type": "number"},
            {"id": "a5", "name": "batch_size", "value": 8, "type": "number"},
            {"id": "a6", "name": "master_path", "value": "/data/mailer/master-list.csv", "type": "string"},
            {"id": "a7", "name": "sig_path", "value": "/data/mailer/signatures.csv", "type": "string"},
            {"id": "a8", "name": "log_path", "value": f"/data/mailer/{acc}/sent-log.csv", "type": "string"},
            {"id": "a9", "name": "offer", "value": "فتح قناة تواصل والتعارف المهني: الهدف أن يردّ المستلم فنبدأ حواراً قد يثمر تعاوناً مستقبلاً.", "type": "string"},
        ]}, "includeOtherFields": False, "options": {}}))
    C(read_file("قراءة القائمة", "={{ $json.master_path }}", [-700, 200]))
    C(extract("استخراج القائمة", [-540, 200]))
    C(read_file("قراءة التواقيع", "={{ $('إعدادات الإرسال').first().json.sig_path }}", [-380, 200]))
    C(extract("استخراج التواقيع", [-220, 200]))
    C(read_file("قراءة السجل", "={{ $('إعدادات الإرسال').first().json.log_path }}", [-60, 200]))
    C(extract("استخراج السجل", [100, 200]))
    C(code("تصفية وتحضير", JS_FILTER, [260, 200]))
    C(n("كاتب الإيميل", "@n8n/n8n-nodes-langchain.agent", 1.7, [460, 200],
        {"promptType": "define", "text": AGENT_TEXT, "options": {"systemMessage": SYSTEM_MESSAGE}}))
    C(n("نموذج OpenAI", "@n8n/n8n-nodes-langchain.lmChatOpenAi", 1.2, [420, 400],
        {"model": {"__rl": True, "mode": "list", "value": "gpt-4o-mini", "cachedResultName": "gpt-4o-mini"}, "options": {}},
        {"credentials": openai_cred}))
    C(code("بناء الرسالة", JS_BUILD, [680, 200], mode_each=True))
    C(n("إرسال الإيميل", "n8n-nodes-base.emailSend", 2.1, [880, 200], {
        "fromEmail": "={{ $('إعدادات الإرسال').first().json.from_email }}",
        "toEmail": "={{ $json.email }}",
        "subject": "={{ $json.subject }}",
        "emailFormat": "text",
        "text": "={{ $json.body }}",
        "options": {"appendAttribution": False},
    }, {"credentials": smtp_cred}))
    C(code("صف السجل", JS_LOGROW, [1080, 200], mode_each=True))
    C(code("دمج السجل", JS_MERGE, [1280, 200]))
    C(n("تحويل إلى CSV", "n8n-nodes-base.convertToFile", 1.1, [1480, 200],
        {"operation": "csv", "options": {}}))
    C(n("حفظ السجل", "n8n-nodes-base.readWriteFile", 1, [1680, 200],
        {"operation": "write", "fileName": "={{ $('إعدادات الإرسال').first().json.log_path }}",
         "dataPropertyName": "data", "options": {}}))

    # ===== REPLY BRANCH =====
    C(n("استقبال الردود", "n8n-nodes-base.emailReadImap", 2, [-900, 640],
        {"mailbox": "INBOX", "postProcessAction": "read", "format": "simple", "options": {}},
        {"credentials": imap_cred}))
    C(n("إعدادات الردود", "n8n-nodes-base.set", 3.4, [-700, 640], {
        "assignments": {"assignments": [
            {"id": "b1", "name": "my_account", "value": acc, "type": "string"},
            {"id": "b2", "name": "main_email", "value": "BURAYA_ANA_EMAIL", "type": "string"},
            {"id": "b3", "name": "from_email", "value": f"BURAYA_{acc}_EMAIL", "type": "string"},
        ]}, "includeOtherFields": True, "options": {}}))
    C(code("تجهيز الإشعار", JS_NOTIFY, [-500, 640]))
    C(n("إشعار برد", "n8n-nodes-base.emailSend", 2.1, [-300, 640], {
        "fromEmail": "={{ $('إعدادات الردود').first().json.from_email }}",
        "toEmail": "={{ $('إعدادات الردود').first().json.main_email }}",
        "subject": "={{ $json.subject }}",
        "emailFormat": "text",
        "text": "={{ $json.text }}",
        "options": {"appendAttribution": False},
    }, {"credentials": smtp_cred}))

    # ===== REPORT BRANCH =====
    C(sched("جدول التقرير", "0 17 * * 1-5", [-900, 900]))
    C(n("إعدادات التقرير", "n8n-nodes-base.set", 3.4, [-700, 900], {
        "assignments": {"assignments": [
            {"id": "c1", "name": "my_account", "value": acc, "type": "string"},
            {"id": "c2", "name": "my_region", "value": region_placeholder, "type": "string"},
            {"id": "c3", "name": "main_email", "value": "BURAYA_ANA_EMAIL", "type": "string"},
            {"id": "c4", "name": "from_email", "value": f"BURAYA_{acc}_EMAIL", "type": "string"},
            {"id": "c5", "name": "log_path", "value": f"/data/mailer/{acc}/sent-log.csv", "type": "string"},
        ]}, "includeOtherFields": False, "options": {}}))
    C(read_file("قراءة سجل التقرير", "={{ $('إعدادات التقرير').first().json.log_path }}", [-500, 900]))
    C(extract("استخراج سجل التقرير", [-340, 900]))
    C(code("تجهيز التقرير", JS_REPORT, [-140, 900]))
    C(n("إرسال التقرير", "n8n-nodes-base.emailSend", 2.1, [60, 900], {
        "fromEmail": "={{ $('إعدادات التقرير').first().json.from_email }}",
        "toEmail": "={{ $('إعدادات التقرير').first().json.main_email }}",
        "subject": "={{ $json.subject }}",
        "emailFormat": "text",
        "text": "={{ $json.text }}",
        "options": {"appendAttribution": False},
    }, {"credentials": smtp_cred}))

    def link(a, b, idx_out=0):
        return (a, b, idx_out)

    conns = {}
    def add(a, b):
        conns.setdefault(a, {"main": [[]]})
        conns[a]["main"][0].append({"node": b, "type": "main", "index": 0})

    # send chain
    add("جدول الإرسال", SET)
    add(SET, "قراءة القائمة")
    add("قراءة القائمة", "استخراج القائمة")
    add("استخراج القائمة", "قراءة التواقيع")
    add("قراءة التواقيع", "استخراج التواقيع")
    add("استخراج التواقيع", "قراءة السجل")
    add("قراءة السجل", "استخراج السجل")
    add("استخراج السجل", "تصفية وتحضير")
    add("تصفية وتحضير", "كاتب الإيميل")
    add("كاتب الإيميل", "بناء الرسالة")
    add("بناء الرسالة", "إرسال الإيميل")
    add("إرسال الإيميل", "صف السجل")
    add("صف السجل", "دمج السجل")
    add("دمج السجل", "تحويل إلى CSV")
    add("تحويل إلى CSV", "حفظ السجل")
    # model -> agent (ai connection)
    conns["نموذج OpenAI"] = {"ai_languageModel": [[{"node": "كاتب الإيميل", "type": "ai_languageModel", "index": 0}]]}
    # reply chain
    add("استقبال الردود", "إعدادات الردود")
    add("إعدادات الردود", "تجهيز الإشعار")
    add("تجهيز الإشعار", "إشعار برد")
    # report chain
    add("جدول التقرير", "إعدادات التقرير")
    add("إعدادات التقرير", "قراءة سجل التقرير")
    add("قراءة سجل التقرير", "استخراج سجل التقرير")
    add("استخراج سجل التقرير", "تجهيز التقرير")
    add("تجهيز التقرير", "إرسال التقرير")

    wf = {
        "name": f"Cold Mailer — {acc}",
        "nodes": nodes,
        "connections": conns,
        "settings": {"executionOrder": "v1"},
        "pinData": {},
        "meta": {"instanceId": f"cold-mailer-{acc}"},
    }
    return wf


REGIONS = ["REGION1", "REGION2", "REGION3", "REGION4", "REGION5"]
names = set()
for i in range(1, 6):
    wf = build_account(i, REGIONS[i - 1])
    # validation
    nn = [x["name"] for x in wf["nodes"]]
    assert len(nn) == len(set(nn)), f"dup node names in account{i}"
    for src, c in wf["connections"].items():
        assert src in nn, f"unknown source {src} in account{i}"
        for ctype, branches in c.items():
            for br in branches:
                for t in br:
                    assert t["node"] in nn, f"unknown target {t['node']} in account{i}"
    path = os.path.join(OUT_DIR, f"{i:02d}_cold_mailer_account{i}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(wf, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"OK account{i}: {len(nn)} nodes -> {os.path.basename(path)}")

print("done")
