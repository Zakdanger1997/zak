#!/usr/bin/env python3
"""freevid — a free, local AI-video pipeline (narrated picture stories).

    freevid.py narrate  project.json   # text-to-speech per scene + word timings (edge-tts, free)
    freevid.py images   project.json   # one AI image per scene (Pollinations, free, no key)
    freevid.py preview  project.json   # contact sheet of the scene images for review
    freevid.py assemble project.json   # Ken Burns motion + captions + narration -> final.mp4
    freevid.py all      project.json   # everything above, in order

Every stage is idempotent: existing audio/images are reused, delete a file to redo it.
Requires: python3, ffmpeg (with libass), `pip install edge-tts requests pillow`.
"""
import argparse, json, os, re, subprocess, sys, time, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
STYLES = json.load(open(os.path.join(HERE, 'styles.json'), encoding='utf-8'))
SIZES = {'9:16': (1080, 1920), '16:9': (1920, 1080), '1:1': (1080, 1080)}


def log(*a):
    print(*a, file=sys.stderr, flush=True)


def run(cmd, **kw):
    log('$', ' '.join(str(c) for c in cmd)[:300])
    return subprocess.run(cmd, check=True, **kw)


def ffprobe_duration(path):
    out = subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path])
    return float(out.decode().strip())


def load_project(path):
    p = json.load(open(path, encoding='utf-8'))
    p.setdefault('aspect', '9:16'); p.setdefault('fps', 30); p.setdefault('lang', 'en')
    p.setdefault('voice', 'en-US-GuyNeural'); p.setdefault('rate', '+0%')
    p.setdefault('lead', 0.4); p.setdefault('tail', 0.6); p.setdefault('seed', 7)
    p.setdefault('image_provider', 'pollinations'); p.setdefault('image_model', 'flux')
    p.setdefault('caption', {}); c = p['caption']
    c.setdefault('enabled', True); c.setdefault('font', 'Cairo'); c.setdefault('size', 58)
    c.setdefault('max_words', 4); c.setdefault('margin_v', 240)
    p.setdefault('style', 'stickman')
    st = STYLES.get(p['style'], {'prompt': p['style'], 'negative': ''})
    p.setdefault('style_prompt', st['prompt']); p.setdefault('negative', st.get('negative', ''))
    p['_dir'] = os.path.dirname(os.path.abspath(path)) or '.'
    for i, sc in enumerate(p['scenes'], 1):
        sc['n'] = i
    return p


def wd(p, *parts):
    d = os.path.join(p['_dir'], *parts)
    os.makedirs(os.path.dirname(d) if os.path.splitext(d)[1] else d, exist_ok=True)
    return d


# ---------------------------------------------------------------- narrate
def vtt_ts(s):
    s = s.replace(',', '.'); parts = [float(x) for x in s.split(':')]
    return parts[0] * 3600 + parts[1] * 60 + parts[2] if len(parts) == 3 else parts[0] * 60 + parts[1]


def parse_vtt(path):
    words, cue = [], None
    for ln in open(path, encoding='utf-8'):
        ln = ln.strip()
        m = re.search(r'([\d:.,]+)\s*-->\s*([\d:.,]+)', ln)
        if m:
            cue = (vtt_ts(m.group(1)), vtt_ts(m.group(2))); continue
        if ln and cue and not ln.startswith('WEBVTT'):
            ws = ln.split(); span = cue[1] - cue[0]
            for k, w in enumerate(ws):
                words.append({'t0': round(cue[0] + span * k / len(ws), 3), 't1': round(cue[0] + span * (k + 1) / len(ws), 3), 'w': w})
            cue = None
    return words


def narrate(p):
    proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
    for sc in p['scenes']:
        mp3 = wd(p, 'audio', f"scene{sc['n']:02d}.mp3"); vtt = mp3[:-4] + '.vtt'
        if not (os.path.exists(mp3) and os.path.getsize(mp3) > 1000):
            cmd = [sys.executable, '-m', 'edge_tts', '--voice', p['voice'], '--rate', p['rate'], '--text', sc['text'], '--write-media', mp3, '--write-subtitles', vtt]
            if proxy:
                cmd += ['--proxy', proxy]
            run(cmd, timeout=180)
        sc['audio'] = mp3; sc['speech'] = round(ffprobe_duration(mp3), 3)
        sc['words'] = parse_vtt(vtt) if os.path.exists(vtt) else []
        log(f"scene {sc['n']}: {sc['speech']}s, {len(sc['words'])} words")
    build_timeline(p)


def build_timeline(p):
    t = 0.0
    for sc in p['scenes']:
        sc['dur'] = round(sc['speech'] + p['lead'] + p['tail'], 3)
        sc['start'] = round(t, 3); sc['voice_at'] = round(t + p['lead'], 3)
        t += sc['dur']
    p['total'] = round(t, 3)
    json.dump({k: v for k, v in p.items() if not k.startswith('_')}, open(wd(p, 'timeline.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    log('timeline total', p['total'], 's')


# ---------------------------------------------------------------- images
def pollinations(prompt, w, h, seed, model, out):
    import requests
    url = 'https://image.pollinations.ai/prompt/' + urllib.parse.quote(prompt, safe='')
    params = {'width': w, 'height': h, 'seed': seed, 'model': model, 'nologo': 'true', 'enhance': 'false'}
    tok = os.environ.get('POLLINATIONS_TOKEN')
    if tok:
        params['token'] = tok
    for attempt in range(4):
        try:
            r = requests.get(url, params=params, timeout=180, headers={'User-Agent': 'freevid/1.0'})
            if r.status_code == 200 and r.headers.get('content-type', '').startswith('image') and len(r.content) > 5000:
                open(out, 'wb').write(r.content); return True
            log('  image attempt', attempt + 1, 'status', r.status_code)
        except Exception as e:  # network hiccup: retry
            log('  image attempt', attempt + 1, 'error', e)
        time.sleep(3 + attempt * 4)
    return False


def placeholder(text, w, h, out):
    from PIL import Image, ImageDraw
    im = Image.new('RGB', (w, h), '#efe6d2'); d = ImageDraw.Draw(im)
    for x in range(0, w, 60):
        d.line([(x, 0), (x, h)], fill='#e3d8c2')
    for y in range(0, h, 60):
        d.line([(0, y), (w, y)], fill='#e3d8c2')
    d.rectangle([w * 0.2, h * 0.4, w * 0.8, h * 0.6], outline='#2a2420', width=6)
    im.save(out, quality=90)


def images(p):
    w, h = SIZES[p['aspect']]
    for sc in p['scenes']:
        out = wd(p, 'images', f"scene{sc['n']:02d}.jpg")
        sc['image_file'] = out
        if os.path.exists(out) and os.path.getsize(out) > 5000:
            continue
        prompt = f"{p['style_prompt']}. {sc['image']}. {p['negative']}".strip()
        seed = p['seed'] * 100 + sc['n'] + int(sc.get('reseed', 0))
        ok = p['image_provider'] == 'pollinations' and pollinations(prompt, w, h, seed, p['image_model'], out)
        if not ok:
            log(f"scene {sc['n']}: using placeholder image")
            placeholder(sc.get('title', ''), w, h, out)
        log(f"scene {sc['n']}: image ready")


def preview(p):
    from PIL import Image, ImageDraw
    w, h = SIZES[p['aspect']]
    tiles = []
    for sc in p['scenes']:
        f = wd(p, 'images', f"scene{sc['n']:02d}.jpg")
        im = Image.open(f).convert('RGB') if os.path.exists(f) else Image.new('RGB', (w, h), '#999')
        im.thumbnail((300, 540)); tiles.append(im)
    cols = min(5, len(tiles)); rows = (len(tiles) + cols - 1) // cols
    tw = max(t.width for t in tiles) + 10; th = max(t.height for t in tiles) + 34
    sheet = Image.new('RGB', (cols * tw, rows * th), 'white'); d = ImageDraw.Draw(sheet)
    for k, t in enumerate(tiles):
        x, y = (k % cols) * tw + 5, (k // cols) * th + 5
        sheet.paste(t, (x, y)); d.text((x, y + t.height + 6), f"scene {k + 1}", fill='black')
    out = wd(p, 'preview.jpg'); sheet.save(out, quality=85); log('preview ->', out)


# ---------------------------------------------------------------- assemble
def ass_time(s):
    cs = int(round(s * 100)); return f"{cs // 360000}:{(cs // 6000) % 60:02d}:{(cs // 100) % 60:02d}.{cs % 100:02d}"


def write_ass(p):
    w, h = SIZES[p['aspect']]; c = p['caption']
    size = c['size'] if p['aspect'] == '9:16' else int(c['size'] * 0.8)
    tsize = int(size * 1.35)
    lines = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {w}", f"PlayResY: {h}", "WrapStyle: 2", "", "[V4+ Styles]",
             "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
             f"Style: Cap,{c['font']},{size},&H00201F1E,&H00FFFFFF,&H00FBF8F1,&H80FBF8F1,-1,0,0,0,100,100,0,0,3,14,0,2,80,80,{c['margin_v']},1",
             f"Style: Title,{c['font']},{tsize},&H00FBF8F1,&H00FFFFFF,&H00201F1E,&H60201F1E,-1,0,0,0,100,100,0,0,1,4,2,8,60,60,110,1",
             "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    for sc in p['scenes']:
        if sc.get('title'):
            lines.append(f"Dialogue: 0,{ass_time(sc['start'] + 0.1)},{ass_time(sc['start'] + sc['dur'] - 0.05)},Title,,0,0,0,,{sc['title']}")
        if not c['enabled'] or not sc.get('words'):
            continue
        groups, cur = [], []
        for wobj in sc['words']:
            cur.append(wobj)
            if len(cur) >= c['max_words'] or re.search(r'[.،؟,?!:;]$', wobj['w']):
                groups.append(cur); cur = []
        if cur:
            (groups[-1].extend(cur) if groups and len(cur) == 1 else groups.append(cur))
        for gi, g in enumerate(groups):
            t0 = sc['voice_at'] + g[0]['t0']
            t1 = sc['voice_at'] + (groups[gi + 1][0]['t0'] if gi + 1 < len(groups) else g[-1]['t1'] + 0.4)
            t1 = min(t1, sc['start'] + sc['dur'])
            txt = ' '.join(x['w'] for x in g).replace('{', '(').replace('}', ')')
            lines.append(f"Dialogue: 1,{ass_time(t0)},{ass_time(t1)},Cap,,0,0,0,,{txt}")
    out = wd(p, 'captions.ass'); open(out, 'w', encoding='utf-8').write('\n'.join(lines) + '\n'); return out


MOTIONS = ['in', 'out', 'left', 'right', 'up', 'down']


def kenburns(p, sc, out):
    w, h = SIZES[p['aspect']]; fps = p['fps']; n = int(round(sc['dur'] * fps))
    motion = sc.get('motion', 'auto')
    if motion == 'auto':
        motion = MOTIONS[(sc['n'] - 1) % len(MOTIONS)]
    z = 1.14
    if motion == 'in':
        zoom, x, y = f"1+{z - 1}*on/{n}", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif motion == 'out':
        zoom, x, y = f"{z}-{z - 1}*on/{n}", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif motion == 'left':
        zoom, x, y = f"{z}", f"(iw-iw/zoom)*on/{n}", "ih/2-(ih/zoom/2)"
    elif motion == 'right':
        zoom, x, y = f"{z}", f"(iw-iw/zoom)*(1-on/{n})", "ih/2-(ih/zoom/2)"
    elif motion == 'up':
        zoom, x, y = f"{z}", "iw/2-(iw/zoom/2)", f"(ih-ih/zoom)*on/{n}"
    else:
        zoom, x, y = f"{z}", "iw/2-(iw/zoom/2)", f"(ih-ih/zoom)*(1-on/{n})"
    # upscale first so zoompan moves on whole pixels (prevents jitter)
    vf = (f"scale={w * 2}:{h * 2}:force_original_aspect_ratio=increase,crop={w * 2}:{h * 2},"
          f"zoompan=z='{zoom}':x='{x}':y='{y}':d=1:s={w}x{h}:fps={fps},format=yuv420p")
    run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-loop', '1', '-framerate', str(fps), '-t', f"{sc['dur']:.3f}", '-i', sc['image_file'],
         '-vf', vf, '-frames:v', str(n), '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-an', out])


def assemble(p):
    if 'total' not in p:
        tl = json.load(open(wd(p, 'timeline.json'), encoding='utf-8'))
        for sc, tsc in zip(p['scenes'], tl['scenes']):
            sc.update({k: tsc[k] for k in ('audio', 'speech', 'words', 'dur', 'start', 'voice_at')})
        p['total'] = tl['total']
    w, h = SIZES[p['aspect']]
    clips = []
    for sc in p['scenes']:
        sc.setdefault('image_file', wd(p, 'images', f"scene{sc['n']:02d}.jpg"))
        clip = wd(p, 'clips', f"scene{sc['n']:02d}.mp4")
        if not os.path.exists(clip):
            kenburns(p, sc, clip)
        clips.append(clip)
    lst = wd(p, 'clips', 'list.txt')
    open(lst, 'w').write(''.join(f"file '{os.path.abspath(c)}'\n" for c in clips))
    silent = wd(p, 'clips', 'video_silent.mp4')
    run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', silent])
    # audio: narration lines at their offsets (+ optional music bed)
    inputs, filt, labels = [], [], []
    for i, sc in enumerate(p['scenes']):
        inputs += ['-i', sc['audio']]; ms = int(round(sc['voice_at'] * 1000))
        filt.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=mono,adelay={ms}|{ms}[a{i}]"); labels.append(f"[a{i}]")
    n = len(p['scenes'])
    mix = f"{''.join(labels)}amix=inputs={n}:normalize=0:dropout_transition=0,apad=whole_dur={p['total']},atrim=0:{p['total']},loudnorm=I=-16:TP=-1.5:LRA=11[voice]"
    filt.append(mix)
    if p.get('music') and os.path.exists(os.path.join(p['_dir'], p['music'])):
        inputs += ['-stream_loop', '-1', '-i', os.path.join(p['_dir'], p['music'])]
        gain = p.get('music_gain', -20)
        filt.append(f"[{n}:a]aresample=48000,atrim=0:{p['total']},volume={gain}dB[bed]")
        filt.append("[voice][bed]amix=inputs=2:normalize=0:dropout_transition=0[out]")
    else:
        filt.append("[voice]acopy[out]")
    voice = wd(p, 'clips', 'audio.wav')
    run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error'] + inputs + ['-filter_complex', ';'.join(filt), '-map', '[out]', '-ar', '48000', '-ac', '2', voice])
    ass = write_ass(p)
    fontsdir = os.path.join(HERE, 'fonts')
    final = wd(p, 'final.mp4')
    vf = f"subtitles='{ass}':fontsdir='{fontsdir}'"
    run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-i', silent, '-i', voice, '-vf', vf, '-c:v', 'libx264', '-preset', 'medium', '-crf', '19',
         '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', final])
    log('final ->', final, f"({ffprobe_duration(final):.1f}s)")
    return final


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('command', choices=['narrate', 'images', 'preview', 'assemble', 'all'])
    ap.add_argument('project')
    a = ap.parse_args()
    p = load_project(a.project)
    if a.command in ('narrate', 'all'):
        narrate(p)
    if a.command in ('images', 'all'):
        images(p)
    if a.command in ('preview', 'all'):
        preview(p)
    if a.command in ('assemble', 'all'):
        assemble(p)


if __name__ == '__main__':
    main()
