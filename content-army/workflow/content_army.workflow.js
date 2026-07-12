export const meta = {
  name: 'content-army',
  description: 'جيش وكلاء للتسويق وصناعة المحتوى: بحث متوازٍ ثم استراتيجية ثم إنتاج ثم مراجعة عدائية',
  whenToUse: 'عندما تريد إنتاج حزمة محتوى تسويقي كاملة (لينكدإن + X + ريلز) عن أي موضوع',
  phases: [
    { title: 'بحث', detail: '4 وكلاء بحث متوازيون: ترندات، جمهور، منافسون، كلمات مفتاحية' },
    { title: 'استراتيجية', detail: 'وكيل استراتيجي يجمع البحث في خطة وأفكار محتوى' },
    { title: 'إنتاج', detail: 'كاتب متخصص لكل فكرة × كل منصة' },
    { title: 'مراجعة', detail: 'مراجع عدائي لكل قطعة محتوى: يقيّم ويحسّن' },
  ],
}

// ---------- المدخلات ----------
const brief = {
  topic: (args && args.topic) || 'بناء علامة شخصية قوية على لينكدإن لمحترف يبحث عن فرص عمل',
  audience: (args && args.audience) || 'مسؤولو التوظيف ومدراء الأقسام',
  goal: (args && args.goal) || 'جذب فرص عمل ومقابلات وبناء مصداقية',
  tone: (args && args.tone) || 'احترافي، إنساني، بدون مبالغة',
  language: (args && args.language) || 'العربية',
  ideasCount: Math.min((args && args.ideasCount) || 3, 5),
}

// ---------- المخططات (Schemas) ----------
const RESEARCH = {
  type: 'object',
  properties: {
    summary: { type: 'string', description: 'خلاصة البحث في فقرة' },
    findings: { type: 'array', items: { type: 'string' }, description: '5-10 نتائج محددة وقابلة للاستخدام' },
    sources: { type: 'array', items: { type: 'string' }, description: 'روابط المصادر المستخدمة' },
  },
  required: ['summary', 'findings'],
}

const STRATEGY = {
  type: 'object',
  properties: {
    strategy_summary: { type: 'string', description: 'خلاصة الاستراتيجية في 2-3 فقرات' },
    pillars: { type: 'array', items: { type: 'string' }, description: 'ركائز المحتوى الأساسية' },
    ideas: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          title: { type: 'string' },
          angle: { type: 'string', description: 'الزاوية الفريدة للفكرة' },
          hook: { type: 'string', description: 'الجملة الافتتاحية الخاطفة' },
          why_it_works: { type: 'string' },
        },
        required: ['title', 'angle', 'hook'],
      },
    },
  },
  required: ['strategy_summary', 'ideas'],
}

const PIECE = {
  type: 'object',
  properties: {
    content: { type: 'string', description: 'نص المحتوى كاملاً وجاهزاً للنشر' },
    hashtags: { type: 'array', items: { type: 'string' } },
    cta: { type: 'string', description: 'دعوة الفعل في نهاية المحتوى' },
    posting_tip: { type: 'string', description: 'نصيحة نشر: التوقيت أو التنسيق' },
  },
  required: ['content'],
}

const REVIEW = {
  type: 'object',
  properties: {
    score: { type: 'number', description: 'تقييم من 1 إلى 10' },
    issues: { type: 'array', items: { type: 'string' }, description: 'المشاكل المكتشفة' },
    improved_content: { type: 'string', description: 'النسخة المحسّنة النهائية كاملة' },
  },
  required: ['score', 'improved_content'],
}

const ctx = `الموضوع: ${brief.topic}
الجمهور المستهدف: ${brief.audience}
الهدف: ${brief.goal}
النبرة: ${brief.tone}
اللغة المطلوبة للمخرجات: ${brief.language}`

// ---------- المرحلة 1: البحث المتوازي ----------
phase('بحث')
log('🔎 إطلاق 4 وكلاء بحث بالتوازي...')

const lenses = [
  { key: 'ترندات', prompt: `أنت وكيل بحث ترندات. ${ctx}\n\nابحث في الويب (WebSearch/WebFetch) عن أحدث الترندات والصيغ الناجحة في هذا الموضوع خلال 2025-2026: ما نوع المحتوى الذي يحقق تفاعلاً الآن؟ ما الصيغ (قصص، قوائم، دراسات حالة...) الأكثر نجاحاً؟ أعد نتائج محددة قابلة للتطبيق.` },
  { key: 'جمهور', prompt: `أنت وكيل بحث جمهور. ${ctx}\n\nابحث في الويب وحلل: من هو هذا الجمهور بالضبط؟ ما آلامه واهتماماته وأسئلته المتكررة؟ ما اللغة والمصطلحات التي يستخدمها؟ متى وأين يتفاعل؟ أعد نتائج محددة تساعد كاتباً على مخاطبته مباشرة.` },
  { key: 'منافسون', prompt: `أنت وكيل تحليل منافسين. ${ctx}\n\nابحث في الويب عن أبرز صنّاع المحتوى/الحسابات الناجحة في هذا المجال: ماذا ينشرون؟ ما الذي ينجح لديهم وما الفجوات التي لا يغطيها أحد؟ أعد نتائج محددة عن الفجوات التي يمكن استغلالها للتميز.` },
  { key: 'كلمات-مفتاحية', prompt: `أنت وكيل كلمات مفتاحية وهاشتاغات. ${ctx}\n\nابحث في الويب عن الكلمات المفتاحية وعبارات البحث والهاشتاغات الأنسب لهذا الموضوع على لينكدإن وX وإنستغرام/تيك توك. أعد قوائم محددة مصنفة حسب المنصة ضمن findings.` },
]

const research = (await parallel(lenses.map(l => () =>
  agent(l.prompt, { label: 'بحث:' + l.key, phase: 'بحث', schema: RESEARCH })
))).filter(Boolean)

log(`✅ اكتمل البحث: ${research.length}/4 وكلاء أعادوا نتائج`)

// ---------- المرحلة 2: الاستراتيجية ----------
phase('استراتيجية')

const researchDigest = research.map((r, i) =>
  `### تقرير ${lenses[i] ? lenses[i].key : i + 1}\n${r.summary}\n- ${(r.findings || []).join('\n- ')}`
).join('\n\n')

const strategy = await agent(
  `أنت مدير استراتيجية محتوى محترف. ${ctx}\n\nهذه تقارير 4 وكلاء بحث:\n\n${researchDigest}\n\nمهمتك: صُغ استراتيجية محتوى واضحة (strategy_summary + pillars)، ثم اقترح بالضبط ${brief.ideasCount} أفكار محتوى قوية ومتنوعة (ideas) مبنية على فجوات المنافسين وآلام الجمهور. كل فكرة يجب أن تكون قابلة للتنفيذ على أكثر من منصة.`,
  { label: 'استراتيجي', phase: 'استراتيجية', schema: STRATEGY }
)

if (!strategy || !strategy.ideas || !strategy.ideas.length) {
  return { error: 'وكيل الاستراتيجية لم يُعد أفكاراً', research }
}

const ideas = strategy.ideas.slice(0, brief.ideasCount)
log(`🧠 الاستراتيجية جاهزة: ${ideas.length} أفكار → إطلاق الكتّاب...`)

// ---------- المرحلتان 3+4: إنتاج ثم مراجعة (pipeline: كل فكرة تتقدم بشكل مستقل) ----------
const PLATFORMS = [
  { key: 'لينكدإن', spec: 'منشور لينكدإن 150-300 كلمة، سطر افتتاحي خاطف قبل زر "رؤية المزيد"، فقرات قصيرة، ينتهي بسؤال أو دعوة نقاش' },
  { key: 'X-سلسلة', spec: 'سلسلة تغريدات (5-8 تغريدات)، كل تغريدة ≤ 280 حرفاً ومرقمة، التغريدة الأولى hook قوي، الأخيرة CTA' },
  { key: 'ريلز-سكربت', spec: 'سكربت فيديو قصير 30-45 ثانية (ريلز/تيك توك): Hook في أول 3 ثوانٍ، ثم المحتوى مقسماً بالمَشاهد مع نص الشاشة، ثم CTA' },
]

const results = await pipeline(
  ideas,
  (idea, _orig, i) =>
    parallel(PLATFORMS.map(p => () =>
      agent(
        `أنت كاتب محتوى متخصص في منصة ${p.key}. ${ctx}\n\nالفكرة المطلوب تنفيذها:\nالعنوان: ${idea.title}\nالزاوية: ${idea.angle}\nالافتتاحية المقترحة: ${idea.hook}\n\nمواصفات المنصة: ${p.spec}\n\nاكتب المحتوى كاملاً وجاهزاً للنشر بلغة ${brief.language}. لا تشرح، أعد المحتوى نفسه.`,
        { label: `كتابة:فكرة${i + 1}:${p.key}`, phase: 'إنتاج', schema: PIECE }
      ).then(piece => piece && { idea_index: i, idea_title: idea.title, platform: p.key, draft: piece })
    )).then(arr => arr.filter(Boolean)),
  (pieces, idea, i) =>
    parallel(pieces.map(pc => () =>
      agent(
        `أنت مراجع محتوى عدائي وصارم. ${ctx}\n\nراجع هذا المحتوى المكتوب لمنصة ${pc.platform}:\n\n---\n${pc.draft.content}\n---\n\nقيّمه من 10 بصرامة: قوة الـ Hook، الملاءمة للمنصة، الملاءمة للجمهور، خلوّه من الحشو والمبالغة والعبارات المستهلكة. اذكر المشاكل في issues ثم أعد النسخة النهائية المحسّنة كاملة في improved_content (حتى لو كان التحسين طفيفاً أعد النص كاملاً).`,
        { label: `مراجعة:فكرة${i + 1}:${pc.platform}`, phase: 'مراجعة', schema: REVIEW }
      ).then(review => ({ ...pc, review }))
    ))
)

const pieces = results.filter(Boolean).flat().filter(Boolean)
log(`🏁 اكتمل العمل: ${pieces.length} قطعة محتوى مكتوبة ومراجَعة`)

return {
  brief,
  research: research.map((r, i) => ({ lens: lenses[i] ? lenses[i].key : String(i), ...r })),
  strategy_summary: strategy.strategy_summary,
  pillars: strategy.pillars || [],
  ideas,
  pieces,
}
