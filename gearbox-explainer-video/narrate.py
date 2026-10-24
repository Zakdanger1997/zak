import json, subprocess, re, os, sys
lines = [
"الموتور ده بيلف ألف وأربعمية لفة في الدقيقة. السير اللي قدامك عايز خمسين لفة بس وقوة تشيل طن، فمين بيعمل الحوار ده؟",
"افتكر عجلة السباق، لما تنقل على الترس الصغير قدام والكبير ورا بتطلع الطلعة براحة بس ببطء، ودي بالظبط فكرة الجيربوكس.",
"جوه الجيربوكس ترس صغير بيدوّر واحد أكبر منه، لو الصغير عشرين سنة والكبير ستين فالكبير بيلف أبطأ بتلات مرات بالظبط.",
"وكل ما السرعة تقل القوة تزيد بنفس النسبة، قسمت السرعة على تلاتة يبقى ضربت العزم في نفس الرقم لأن الطاقة مبتضيعش.",
"موتور واحد ونص كيلووات بيطلع عشرة نيوتن متر بس، وبعد جيربوكس بتخفيض تلاتين مرة بيطلع تقريباً تلاتمية نيوتن متر على السير.",
"أسنان الأتراس مش مستقيمة، دي مايلة شوية واسمها حلزونية، كذا سنة بتشتبك في نفس اللحظة فالصوت أهدى والحمل اللي تشيله أعلى.",
"الأتراس دي من صلب متقسي لتمنية وخمسين روكويل وبتعوم في حمام زيت، والزيت ده بيتغير كل ستة آلاف ساعة شغل تقريباً.",
"ناس كتير فاكرة إن الحل موتور أكبر، لأ، الصغير مع جيربوكس بيديك نفس العزم بتمن أرخص وكهرباء أقل بكتير في الآخر.",
"ببساطة الجيربوكس بياخد لفات كتير بقوة صغيرة ويطلعلك دورات قليلة بعزم جبار، وكده موتور قد الإيد بيحرك سير بطول الأوضة.",
]
os.makedirs('audio', exist_ok=True)
proxy = os.environ['HTTPS_PROXY']
def ts(s):
    h,m,rest = s.split(':'); return int(h)*3600+int(m)*60+float(rest)
out = []
for i, text in enumerate(lines, 1):
    mp3 = f'audio/line{i:02d}.mp3'; vtt = f'audio/line{i:02d}.vtt'
    if not (os.path.exists(mp3) and os.path.getsize(mp3) > 1000):
        subprocess.run(['python3','-m','edge_tts',*(['--proxy', proxy] if proxy else []),'--voice','ar-EG-ShakirNeural','--rate','+4%','--text',text,'--write-media',mp3,'--write-subtitles',vtt], check=True, timeout=120)
    dur = float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',mp3]).decode().strip())
    words = []
    cue = None
    for ln in open(vtt, encoding='utf-8'):
        ln = ln.strip()
        m = re.match(r'(\d+:\d+:[\d.]+) --> (\d+:\d+:[\d.]+)', ln)
        if m: cue = (ts(m.group(1)), ts(m.group(2))); continue
        if ln and cue and not ln.startswith('WEBVTT'):
            words.append({'t0': round(cue[0],3), 't1': round(cue[1],3), 'w': ln}); cue = None
    out.append({'n': i, 'text': text, 'dur': round(dur,3), 'words': words})
    print(i, round(dur,2), len(words), 'words')
json.dump(out, open('narration.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('total speech', round(sum(o['dur'] for o in out),1))
