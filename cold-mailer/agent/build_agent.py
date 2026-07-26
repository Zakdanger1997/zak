# -*- coding: utf-8 -*-
"""يبني نظام الوكيل المستقل: workflow رئيسي (AI Agent) + أداتان (sub-workflows)."""
import json, os

OUT = '/home/user/zak/cold-mailer/agent'
os.makedirs(OUT, exist_ok=True)


def node(name, ntype, ver, pos, params, extra=None):
    d = {"parameters": params, "id": name, "name": name, "type": ntype, "typeVersion": ver, "position": pos}
    if extra:
        d.update(extra)
    return d


def add_conn(conns, a, b, ctype="main", idx_out=0, idx_in=0):
    conns.setdefault(a, {})
    conns[a].setdefault(ctype, [])
    while len(conns[a][ctype]) <= idx_out:
        conns[a][ctype].append([])
    conns[a][ctype][idx_out].append({"node": b, "type": ctype, "index": idx_in})


# ==========================================================================
# أداة 1: get_pending_contacts  (sub-workflow)
# ==========================================================================
def build_get_contacts():
    N, C = [], {}
    JS_PARSE = r"""
let raw = $json.query ?? $json;
let p = {};
try { p = (typeof raw === 'string') ? JSON.parse(raw) : raw; } catch (e) { p = {}; }
return [{ json: {
  account: String(p.account || 'account1').trim(),
  region: String(p.region || '').trim(),
  limit: Math.max(1, Math.min(Number(p.limit || 8), 20))
} }];
""".strip()

    JS_FILTER = r"""
const req = $('قراءة الطلب').first().json;
const region = String(req.region || '').toLowerCase();
const limit = req.limit;
const list = $('استخراج القائمة').all().map(i => i.json).filter(r => r && r.email);
const sent = $('استخراج السجل').all().map(i => i.json).filter(r => r && r.email);
const sentSet = new Set(sent.map(r => String(r.email).toLowerCase()));

const out = []; const seen = new Set();
for (const row of list) {
  const email = String(row.email || '').trim().toLowerCase();
  if (!email || !email.includes('@')) continue;
  if (region && String(row.region || '').trim().toLowerCase() !== region) continue;
  if (sentSet.has(email) || seen.has(email)) continue;
  seen.add(email);
  out.push({ email, first_name: row.first_name || '', company: row.company || '',
             title: row.title || '', region: row.region || '', custom1: row.custom1 || '' });
  if (out.length >= limit) break;
}
return [{ json: { account: req.account, region: req.region, count: out.length, contacts: out } }];
""".strip()

    N.append(node("Trigger", "n8n-nodes-base.executeWorkflowTrigger", 1.1, [-1000, 300], {}))
    N.append(node("قراءة الطلب", "n8n-nodes-base.code", 2, [-800, 300], {"jsCode": JS_PARSE}))
    N.append(node("قراءة القائمة", "n8n-nodes-base.readWriteFile", 1, [-600, 300],
                  {"operation": "read", "fileSelector": "/data/mailer/master-list.csv", "options": {}},
                  {"onError": "continueRegularOutput"}))
    N.append(node("استخراج القائمة", "n8n-nodes-base.extractFromFile", 1, [-440, 300],
                  {"operation": "csv", "binaryPropertyName": "data", "options": {}},
                  {"onError": "continueRegularOutput"}))
    N.append(node("قراءة السجل", "n8n-nodes-base.readWriteFile", 1, [-280, 300],
                  {"operation": "read",
                   "fileSelector": "=/data/mailer/{{ $('قراءة الطلب').first().json.account }}/sent-log.csv",
                   "options": {}},
                  {"onError": "continueRegularOutput"}))
    N.append(node("استخراج السجل", "n8n-nodes-base.extractFromFile", 1, [-120, 300],
                  {"operation": "csv", "binaryPropertyName": "data", "options": {}},
                  {"onError": "continueRegularOutput"}))
    N.append(node("تصفية", "n8n-nodes-base.code", 2, [80, 300], {"jsCode": JS_FILTER}))

    add_conn(C, "Trigger", "قراءة الطلب")
    add_conn(C, "قراءة الطلب", "قراءة القائمة")
    add_conn(C, "قراءة القائمة", "استخراج القائمة")
    add_conn(C, "استخراج القائمة", "قراءة السجل")
    add_conn(C, "قراءة السجل", "استخراج السجل")
    add_conn(C, "استخراج السجل", "تصفية")

    return {"name": "TOOL — get_pending_contacts", "nodes": N, "connections": C,
            "settings": {"executionOrder": "v1"}, "pinData": {}, "meta": {"instanceId": "tool-get-contacts"}}


# ==========================================================================
# أداة 2: send_email  (sub-workflow) — يفرض منع التكرار والحد اليومي بنفسه
# ==========================================================================
def build_send_email():
    N, C = [], {}

    # خريطة الحساب -> عنوان المرسِل  (عدّلها)
    JS_PARSE = r"""
let raw = $json.query ?? $json;
let p = {};
try { p = (typeof raw === 'string') ? JSON.parse(raw) : raw; } catch (e) { p = {}; }

const FROM = {
  account1: 'BURAYA_account1_EMAIL',
  account2: 'BURAYA_account2_EMAIL',
  account3: 'BURAYA_account3_EMAIL',
  account4: 'BURAYA_account4_EMAIL',
  account5: 'BURAYA_account5_EMAIL'
};
const DAILY_LIMIT = 40;   // الحد اليومي لكل حساب

const account = String(p.account || 'account1').trim();
return [{ json: {
  account,
  from_email: FROM[account] || '',
  to: String(p.to || '').trim(),
  subject: String(p.subject || 'تواصل').trim(),
  body: String(p.body || '').trim(),
  company: String(p.company || '').trim(),
  region: String(p.region || '').trim(),
  daily_limit: DAILY_LIMIT
} }];
""".strip()

    JS_GATE = r"""
const p = $('قراءة الطلب').first().json;
const sent = $('استخراج السجل').all().map(i => i.json).filter(r => r && r.email);
const to = String(p.to || '').toLowerCase();
const today = new Date().toISOString().slice(0, 10);

const dup = sent.some(r => String(r.email).toLowerCase() === to);
const sentToday = sent.filter(r => String(r.tarih || '').slice(0, 10) === today).length;
const capped = sentToday >= Number(p.daily_limit || 40);
const blocked = dup || capped || !to.includes('@') || !p.from_email;

let reason = 'ok';
if (!to.includes('@')) reason = 'invalid_email';
else if (!p.from_email) reason = 'account_from_email_not_set';
else if (dup) reason = 'skipped_duplicate';
else if (capped) reason = 'cap_reached';

return [{ json: { ...p, blocked, reason } }];
""".strip()

    JS_LOGROW = r"""
const p = $('بوابة الأمان').first().json;
const now = new Date().toISOString().slice(0, 16).replace('T', ' ');
return [{ json: { tarih: now, email: p.to, region: p.region || '', firma: p.company || '',
                  konu: p.subject || '', durum: 'GONDERILDI' } }];
""".strip()

    JS_MERGE = r"""
const old = $('استخراج السجل').all().map(i => i.json).filter(r => r && r.email);
const neu = $input.all().map(i => i.json);
return [...old, ...neu].map(r => ({ json: r }));
""".strip()

    JS_RESULT_OK = r"""
const p = $('بوابة الأمان').first().json;
return [{ json: { status: 'sent', to: p.to, account: p.account } }];
""".strip()

    JS_RESULT_SKIP = r"""
const p = $('بوابة الأمان').first().json;
return [{ json: { status: p.reason, to: p.to, account: p.account } }];
""".strip()

    N.append(node("Trigger", "n8n-nodes-base.executeWorkflowTrigger", 1.1, [-1300, 300], {}))
    N.append(node("قراءة الطلب", "n8n-nodes-base.code", 2, [-1120, 300], {"jsCode": JS_PARSE}))
    N.append(node("قراءة السجل", "n8n-nodes-base.readWriteFile", 1, [-940, 300],
                  {"operation": "read",
                   "fileSelector": "=/data/mailer/{{ $('قراءة الطلب').first().json.account }}/sent-log.csv",
                   "options": {}}, {"onError": "continueRegularOutput"}))
    N.append(node("استخراج السجل", "n8n-nodes-base.extractFromFile", 1, [-780, 300],
                  {"operation": "csv", "binaryPropertyName": "data", "options": {}},
                  {"onError": "continueRegularOutput"}))
    N.append(node("بوابة الأمان", "n8n-nodes-base.code", 2, [-600, 300], {"jsCode": JS_GATE}))
    N.append(node("مسموح؟", "n8n-nodes-base.if", 2.2, [-420, 300], {
        "conditions": {"options": {"caseSensitive": True, "typeValidation": "loose", "version": 2},
                       "conditions": [{"id": "g1", "leftValue": "={{ $json.blocked }}", "rightValue": "",
                                       "operator": {"type": "boolean", "operation": "false", "singleValue": True}}],
                       "combinator": "and"}, "options": {}}))

    # فرع الرفض
    N.append(node("نتيجة التخطي", "n8n-nodes-base.code", 2, [-220, 520], {"jsCode": JS_RESULT_SKIP}))

    # فرع الإرسال: Switch على الحساب -> SMTP لكل حساب
    rules = []
    for i in range(1, 6):
        rules.append({"conditions": {"options": {"caseSensitive": True, "typeValidation": "loose", "version": 2},
                                     "conditions": [{"id": f"s{i}", "leftValue": "={{ $json.account }}",
                                                     "rightValue": f"account{i}",
                                                     "operator": {"type": "string", "operation": "equals"}}],
                                     "combinator": "and"},
                      "renameOutput": True, "outputKey": f"account{i}"})
    N.append(node("اختر الحساب", "n8n-nodes-base.switch", 3.2, [-220, 200],
                  {"rules": {"values": rules}, "options": {}}))

    for i in range(1, 6):
        N.append(node(f"SMTP account{i}", "n8n-nodes-base.emailSend", 2.1, [40, 40 + (i - 1) * 90], {
            "fromEmail": "={{ $json.from_email }}",
            "toEmail": "={{ $json.to }}",
            "subject": "={{ $json.subject }}",
            "emailFormat": "text",
            "text": "={{ $json.body }}",
            "options": {"appendAttribution": False},
        }, {"credentials": {"smtp": {"id": f"smtp-account{i}", "name": f"SMTP account{i}"}}}))

    N.append(node("صف السجل", "n8n-nodes-base.code", 2, [320, 200], {"jsCode": JS_LOGROW}))
    N.append(node("دمج السجل", "n8n-nodes-base.code", 2, [500, 200], {"jsCode": JS_MERGE}))
    N.append(node("تحويل إلى CSV", "n8n-nodes-base.convertToFile", 1.1, [680, 200], {"operation": "csv", "options": {}}))
    N.append(node("حفظ السجل", "n8n-nodes-base.readWriteFile", 1, [860, 200], {
        "operation": "write",
        "fileName": "=/data/mailer/{{ $('بوابة الأمان').first().json.account }}/sent-log.csv",
        "dataPropertyName": "data", "options": {}}))
    N.append(node("نتيجة الإرسال", "n8n-nodes-base.code", 2, [1040, 200], {"jsCode": JS_RESULT_OK}))

    add_conn(C, "Trigger", "قراءة الطلب")
    add_conn(C, "قراءة الطلب", "قراءة السجل")
    add_conn(C, "قراءة السجل", "استخراج السجل")
    add_conn(C, "استخراج السجل", "بوابة الأمان")
    add_conn(C, "بوابة الأمان", "مسموح؟")
    add_conn(C, "مسموح؟", "اختر الحساب", idx_out=0)   # true (blocked=false => allowed)
    add_conn(C, "مسموح؟", "نتيجة التخطي", idx_out=1)   # false
    for i in range(1, 6):
        add_conn(C, "اختر الحساب", f"SMTP account{i}", idx_out=i - 1)
        add_conn(C, f"SMTP account{i}", "صف السجل")
    add_conn(C, "صف السجل", "دمج السجل")
    add_conn(C, "دمج السجل", "تحويل إلى CSV")
    add_conn(C, "تحويل إلى CSV", "حفظ السجل")
    add_conn(C, "حفظ السجل", "نتيجة الإرسال")

    return {"name": "TOOL — send_email", "nodes": N, "connections": C,
            "settings": {"executionOrder": "v1"}, "pinData": {}, "meta": {"instanceId": "tool-send-email"}}


# ==========================================================================
# الرئيسي: AI Agent المستقل
# ==========================================================================
def build_agent():
    N, C = [], {}

    SOP = (
        "أنت مساعد تواصل مستقل (autonomous outreach agent). في كل تشغيلة تنفّذ الدورة الآتية بنفسك:\n\n"
        "لكل حساب في الجدول أدناه:\n"
        "1. استدعِ الأداة get_pending_contacts ومرّر لها JSON: {\"account\":\"account1\",\"region\":\"<المنطقة>\",\"limit\":8}\n"
        "   لتحصل على العملاء الذين لم تُرسَل لهم بعد.\n"
        "2. لكل عميل في النتيجة: اكتب رسالة إيميل شخصية قصيرة (القواعد أدناه) ثم استدعِ الأداة send_email\n"
        "   ومرّر لها JSON: {\"account\":\"account1\",\"to\":\"<email>\",\"subject\":\"<subject>\",\"body\":\"<body>\",\"company\":\"<company>\",\"region\":\"<region>\"}\n"
        "3. لا تطلب ولا ترسل لنفس العنوان مرتين. الأدوات تمنع التكرار وتجاوز الحد تلقائياً؛ إن أعادت الأداة\n"
        "   status=skipped_duplicate أو cap_reached فتجاوز هذا العميل وأكمل.\n"
        "4. لا ترسل أكثر من 8 لكل حساب في التشغيلة الواحدة.\n\n"
        "الحسابات والمناطق (عدّلها حسب توزيعك):\n"
        "- account1 → İstanbul\n- account2 → Ankara\n- account3 → İzmir\n- account4 → الرياض\n- account5 → دبي\n\n"
        "الغرض من الرسائل: فتح قناة تواصل والتعارف المهني — الهدف أن يردّ المستلم فنبدأ حواراً قد يثمر تعاوناً.\n\n"
        "قواعد كتابة الإيميل (شخصي لا تسويقي):\n"
        "- اللغة حسب المنطقة: التركية للمناطق التركية، العربية للعربية، الإنجليزية لغيرها.\n"
        "- 50–80 كلمة، 3–4 جمل، رسمي معتدل وإنساني.\n"
        "- أول جملة تخصيص حقيقي عن الشركة/المنصب/الملاحظة.\n"
        "- اختم بسؤال قصير + جملة انسحاب ناعمة («ولو ما يناسبك ردّ بكلمة وما أزعجك»).\n"
        "- ممنوع: العبارات المستهلكة، لغة المبيعات، الإيموجي، Markdown. لا تكتب توقيعاً (يُضاف تلقائياً).\n\n"
        "في نهاية التشغيلة أعد ملخصاً نصياً موجزاً: كم أُرسل لكل حساب وكم تُخطّي ولماذا.\n\n"
        "ملاحظة عن جلب العملاء: إن لم تجد الأداة عملاء جدداً لحساب ما، فذلك يعني أن قائمته انتهت — لا تختلق عناوين، انتقل للحساب التالي."
    )

    N.append(node("جدول التشغيل", "n8n-nodes-base.scheduleTrigger", 1.2, [-700, 300],
                  {"rule": {"interval": [{"field": "cronExpression", "expression": "0 9-16 * * 1-5"}]}}))
    N.append(node("ابدأ الدورة", "n8n-nodes-base.set", 3.4, [-500, 300], {
        "assignments": {"assignments": [
            {"id": "m1", "name": "main_email", "value": "BURAYA_ANA_EMAIL", "type": "string"},
            {"id": "m2", "name": "instruction", "value": "شغّل دورة التواصل الآن لكل الحسابات.", "type": "string"},
        ]}, "includeOtherFields": False, "options": {}}))

    N.append(node("الوكيل", "@n8n/n8n-nodes-langchain.agent", 1.7, [-280, 300], {
        "promptType": "define",
        "text": "={{ $json.instruction }}",
        "options": {"systemMessage": SOP, "maxIterations": 60},
    }))
    N.append(node("نموذج OpenAI", "@n8n/n8n-nodes-langchain.lmChatOpenAi", 1.2, [-360, 520],
                  {"model": {"__rl": True, "mode": "list", "value": "gpt-4o", "cachedResultName": "gpt-4o"},
                   "options": {"temperature": 0.7}},
                  {"credentials": {"openAiApi": {"id": "openai-cred", "name": "OpenAI"}}}))
    N.append(node("ذاكرة", "@n8n/n8n-nodes-langchain.memoryBufferWindow", 1.3, [-200, 520],
                  {"contextWindowLength": 30}))
    N.append(node("get_pending_contacts", "@n8n/n8n-nodes-langchain.toolWorkflow", 2.1, [-40, 520], {
        "name": "get_pending_contacts",
        "description": "احصل على العملاء غير المُرسَل لهم لحساب/منطقة. المدخل نص JSON: {\"account\":\"account1\",\"region\":\"İstanbul\",\"limit\":8}",
        "workflowId": {"__rl": True, "mode": "id", "value": "REPLACE_get_pending_contacts_ID"},
    }))
    N.append(node("send_email", "@n8n/n8n-nodes-langchain.toolWorkflow", 2.1, [120, 520], {
        "name": "send_email",
        "description": "أرسل إيميلاً واحداً (يمنع التكرار والحد تلقائياً). المدخل نص JSON: {\"account\":\"account1\",\"to\":\"x@y.com\",\"subject\":\"..\",\"body\":\"..\",\"company\":\"..\",\"region\":\"..\"}",
        "workflowId": {"__rl": True, "mode": "id", "value": "REPLACE_send_email_ID"},
    }))

    N.append(node("تجهيز التقرير", "n8n-nodes-base.set", 3.4, [-40, 300], {
        "assignments": {"assignments": [
            {"id": "r1", "name": "text", "value": "={{ $json.output }}", "type": "string"},
            {"id": "r2", "name": "subject", "value": "=تقرير دورة التواصل — {{ $now.format('yyyy-LL-dd HH:mm') }}", "type": "string"},
        ]}, "includeOtherFields": False, "options": {}}))
    N.append(node("إرسال التقرير", "n8n-nodes-base.emailSend", 2.1, [180, 300], {
        "fromEmail": "={{ $('ابدأ الدورة').first().json.main_email }}",
        "toEmail": "={{ $('ابدأ الدورة').first().json.main_email }}",
        "subject": "={{ $json.subject }}",
        "emailFormat": "text",
        "text": "={{ $json.text }}",
        "options": {"appendAttribution": False},
    }, {"credentials": {"smtp": {"id": "smtp-account1", "name": "SMTP account1"}}}))

    add_conn(C, "جدول التشغيل", "ابدأ الدورة")
    add_conn(C, "ابدأ الدورة", "الوكيل")
    add_conn(C, "نموذج OpenAI", "الوكيل", ctype="ai_languageModel")
    add_conn(C, "ذاكرة", "الوكيل", ctype="ai_memory")
    add_conn(C, "get_pending_contacts", "الوكيل", ctype="ai_tool")
    add_conn(C, "send_email", "الوكيل", ctype="ai_tool")
    add_conn(C, "الوكيل", "تجهيز التقرير")
    add_conn(C, "تجهيز التقرير", "إرسال التقرير")

    return {"name": "Cold Mailer — AI Agent (autonomous)", "nodes": N, "connections": C,
            "settings": {"executionOrder": "v1"}, "pinData": {}, "meta": {"instanceId": "cold-mailer-agent"}}


def validate(wf):
    names = [n["name"] for n in wf["nodes"]]
    assert len(names) == len(set(names)), f"dup names in {wf['name']}"
    for src, c in wf["connections"].items():
        assert src in names, f"unknown source {src} in {wf['name']}"
        for ctype, branches in c.items():
            for br in branches:
                for t in br:
                    assert t["node"] in names, f"unknown target {t['node']} in {wf['name']}"


builds = [
    ("tool_get_contacts.json", build_get_contacts()),
    ("tool_send_email.json", build_send_email()),
    ("00_autonomous_agent.json", build_agent()),
]
for fname, wf in builds:
    validate(wf)
    with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
        json.dump(wf, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"OK {fname}: {len(wf['nodes'])} nodes")
print("done")
