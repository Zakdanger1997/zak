# TikTok Shop Setup Checklist

A step-by-step guide to opening a **TikTok Shop (Seller account)** so the clips produced by the `clip-cutter` skill can become shoppable videos.

> **Important:** A TikTok Shop is a **separate account** from your creator/personal account, and it cannot be created by Claude or any connected MCP tool. It is a manual onboarding at TikTok's Seller Center that requires identity, business, and bank verification. This checklist walks you through it; the `clip-cutter` skill handles producing and publishing the clips once your Shop is live.

> **Regions & rules change.** TikTok Shop is not available in every country, and requirements/fees differ by region and update often. Treat this as a map, and confirm the current specifics for your country at `seller.tiktok.com` before relying on any detail.

## Know which account you need

| Account | Purpose | Where |
|---|---|---|
| Creator / personal | Posting videos (what `clip-cutter` publishes to) | TikTok app |
| **TikTok Shop – Seller** | Selling products, checkout, orders, shoppable clips | `seller.tiktok.com` |
| Business account | Ads, promotion, analytics | TikTok app → Settings → Account |

You want the **Seller account** for a store.

## Before you apply — gather these

- [ ] **Confirm your country is supported** for TikTok Shop.
- [ ] **Decide seller type:** registered business vs. individual seller (availability varies by region).
- [ ] **Business documents** (if a business): business license / company registration number, tax info.
- [ ] **Government-issued ID** for the account holder (for identity verification).
- [ ] **Proof of address** (may be required for individual sellers).
- [ ] **Bank account details** for payouts (name must match the account holder).
- [ ] **Phone number + email** not already tied to another TikTok Shop.
- [ ] **Product info ready:** titles, descriptions, prices, and clear product images.

## Application steps

1. [ ] Go to **`seller.tiktok.com`** and sign up (you can register with your existing TikTok login or a new email).
2. [ ] Select your **region** and **seller type** (business or individual).
3. [ ] Complete **identity verification** — upload your ID and business docs.
4. [ ] Wait for **review/approval** (commonly ~1–3 business days; varies).
5. [ ] Once approved, complete your **shop profile** and **tax/payout setup**.
6. [ ] **Add products** to your catalog (or connect an existing catalog/commerce platform if supported in your region).
7. [ ] **Set up shipping/fulfillment** options and returns policy.

## Link the Shop to your content account

8. [ ] In Seller Center / the TikTok app, **link your TikTok Shop to the creator account** that `clip-cutter` publishes to. Product tagging only works when the posting account is linked to the Shop.
9. [ ] Confirm the **yellow cart / product showcase** appears on your profile.

## Make your clips shoppable

Now the `clip-cutter` pipeline and the Shop work together:

10. [ ] Use `clip-cutter` to **cut and publish** clips to the linked TikTok account (draft or live).
11. [ ] In the **TikTok app**, open each posted clip and **attach the product tag / product link** (this step is manual — the publishing tools do not tag products).
12. [ ] Disclose commercial/branded content honestly when required.

### Tips for clips that sell

- **Hook in the first 3 seconds** — problem, bold claim, or pattern interrupt.
- **Show the product in use**, not just talking about it.
- **One product, one clear CTA** per clip ("tap the cart", "link in bio").
- Match caption tone to your `brand-voice`.
- Test several hooks; keep the winners (use `virality_predictor` in `clip-cutter` to rank before posting).

## What this checklist does NOT do

- It does not create the Shop for you — that's a manual signup requiring verification.
- Connected tools publish videos but **do not** create Shops or tag products; those steps happen in TikTok's Seller Center / app.
