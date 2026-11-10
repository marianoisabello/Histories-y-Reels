import subprocess, sys, os, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cfgs
C = cfgs.CFG[os.environ.get('CFG', 'v2')]

W, H, FPS = 1080, 1920, 30
DUR = 30.0
NFR = C['nfr']
PEND = NFR / 30
FONT = '/usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf'

def load(n): return cv2.cvtColor(cv2.imread(f"{C['bg']}/{n}.png"), cv2.COLOR_BGR2RGB)
BG = {n: load(n) for n in C['pres_names'] + C['card_names']}

def ease(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)

def crop(img, z, cy_bias=0.0):
    """z in (0,1]: fraction of the 1188-wide image shown."""
    h0, w0 = img.shape[:2]
    w = w0 * z; h = w * H / W
    x0 = (w0 - w) / 2; y0 = (h0 - h) / 2 + cy_bias
    M = np.array([[W / w, 0, -x0 * W / w], [0, H / h, -y0 * H / h]], np.float32)
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR)

# ---- scenes: (name, start, end, z_from, z_to)
PRES = cfgs.pres_scenes(C, PEND)
CARDS = cfgs.card_scenes(C, PEND, DUR)
XF = 0.3

def scene_img(name, t0, t1, t, card):
    p = (t - t0) / max(t1 - t0, 1e-3)
    if card:
        z = 0.84 + 0.07 * ease(min((t - t0) / 0.6, 1)) + 0.02 * p  # quick settle, then slow drift
        return crop(BG[name], z)
    return crop(BG[name], 0.93 - 0.05 * p)

def bg_at(t, scenes, card):
    for i, (n, t0, t1) in enumerate(scenes):
        if t0 <= t < t1 or i == len(scenes) - 1:
            img = scene_img(n, t0, t1, t, card)
            if i > 0 and t < t0 + XF:
                a = ease((t - t0) / XF)
                pn, p0, p1 = scenes[i - 1]
                prev = scene_img(pn, p0, p1, t, card)
                img = cv2.addWeighted(prev, 1 - a, img, a, 0)
            return img

# ---- presenter frames
def frames(path, fmt, ch):
    proc = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', path, '-f', 'rawvideo', '-pix_fmt', fmt, '-'], stdout=subprocess.PIPE)
    n = W * H * ch
    while True:
        b = proc.stdout.read(n)
        if len(b) < n: return
        yield np.frombuffer(b, np.uint8).reshape(H, W, ch) if ch > 1 else np.frombuffer(b, np.uint8).reshape(H, W)

SC = 0.72
PW, PH = int(W * SC), int(H * SC)
PX, PY = (W - PW) // 2, H - PH

ramp = np.ones(PW, np.float32); r = 110
ramp[:r] = np.linspace(0, 1, r) ** 1.5; ramp[-r:] = ramp[:r][::-1]
EDGE = np.repeat(ramp[None], PH, 0)

def comp_presenter(bg, fg, al):
    fg = cv2.resize(fg, (PW, PH), interpolation=cv2.INTER_AREA)
    al = cv2.resize(al, (PW, PH), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    al *= EDGE
    out = bg.astype(np.float32)
    # soft glow/shadow behind the presenter
    sh = np.zeros((H, W), np.float32); sh[PY:, PX:PX + PW] = al
    sh = cv2.GaussianBlur(cv2.resize(sh, (W // 4, H // 4)), (0, 0), 10)
    sh = cv2.resize(sh, (W, H))[..., None]
    out *= (1 - 0.45 * sh)
    reg = out[PY:, PX:PX + PW]
    a = al[..., None]
    out[PY:, PX:PX + PW] = reg * (1 - a) + fg.astype(np.float32) * a
    return out

# ---- subtitles
SEGS = C['segs']
WORDS = []  # (chunk_id, word, t0, t1)
CHUNKS = []  # (t0, t1, words)
for s0, s1, chunks in SEGS:
    allw = [(ci, w) for ci, c in enumerate(chunks) for w in c.split()]
    tot = sum(len(w) + 2 for _, w in allw)
    t = s0; cur = {}
    for ci, w in allw:
        d = (s1 - s0) * (len(w) + 2) / tot
        cur.setdefault(ci, []).append((w, t, t + d)); t += d
    for ci in sorted(cur):
        ws = cur[ci]
        CHUNKS.append([ws[0][1], ws[-1][2], ws])
for i in range(len(CHUNKS) - 1):  # hold each chunk until next one starts if gap is small
    if CHUNKS[i + 1][0] - CHUNKS[i][1] < 0.45: CHUNKS[i][1] = CHUNKS[i + 1][0]
CHUNKS[-1][1] += 0.25

FNT = ImageFont.truetype(FONT, 76)
SUB_CACHE = {}
def sub_img(ci, active):
    key = (ci, active)
    if key in SUB_CACHE: return SUB_CACHE[key]
    ws = [w for w, _, _ in CHUNKS[ci][2]]
    d0 = ImageDraw.Draw(Image.new('L', (1, 1)))
    f = FNT
    if d0.textlength(' '.join(ws), font=f) > 930:
        f = ImageFont.truetype(FONT, int(76 * 930 / d0.textlength(' '.join(ws), font=f)))
    sp = d0.textlength(' ', font=f)
    lens = [d0.textlength(w, font=f) for w in ws]
    tw = sum(lens) + sp * (len(ws) - 1)
    im = Image.new('RGBA', (int(tw) + 80, 150), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = 40
    for i, w in enumerate(ws):
        if i == active:
            d.rounded_rectangle([x - 14, 22, x + lens[i] + 14, 128], 22, fill=(124, 92, 255, 255))
        d.text((x, 75), w, font=f, fill=(255, 255, 255, 255), anchor='lm', stroke_width=0 if i == active else 5, stroke_fill=(10, 10, 20, 255))
        x += lens[i] + sp
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); sh.putalpha(im.getchannel('A').point(lambda a: a * 0.6))
    sh = sh.filter(ImageFilter.GaussianBlur(10))
    full = Image.new('RGBA', im.size, (0, 0, 0, 0)); full.alpha_composite(sh, (0, 6)); full.alpha_composite(im)
    arr = np.asarray(full).astype(np.float32)
    SUB_CACHE[key] = arr
    return arr

SUB_Y = 1440
def draw_sub(out, t):
    for ci, (c0, c1, ws) in enumerate(CHUNKS):
        if c0 <= t < c1:
            act = max([i for i, (_, w0, _) in enumerate(ws) if t >= w0] or [0])
            arr = sub_img(ci, act)
            k = 0.86 + 0.14 * ease((t - c0) / 0.12)
            if k < 1: arr = cv2.resize(arr, None, fx=k, fy=k, interpolation=cv2.INTER_AREA)
            h, w = arr.shape[:2]
            x0, y0 = (W - w) // 2, SUB_Y - h // 2
            reg = out[y0:y0 + h, x0:x0 + w]
            a = arr[..., 3:4] / 255
            out[y0:y0 + h, x0:x0 + w] = reg * (1 - a) + arr[..., :3] * a
            return

def main(dst, only=None):
    fg_it = frames(C['dir'] + '/fgr.mp4', 'rgb24', 3); al_it = frames(C['dir'] + '/alpha.mkv', 'gray', 1)
    enc = None
    if only is None:
        enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                                '-c:v', 'libx264', '-crf', '18', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', dst], stdin=subprocess.PIPE)
    last = None
    N = int(DUR * FPS)
    for i in range(N):
        t = i / FPS
        if i < NFR:
            fg, al = next(fg_it), next(al_it)
            pres = comp_presenter(bg_at(t, PRES, False), fg, al)
            last = pres
        else:
            pres = last
        if t < PEND:
            out = pres.copy()
        else:
            out = bg_at(t, CARDS, True).astype(np.float32)
            a = ease((t - PEND) / 0.4)
            if a < 1:
                z = 1 + 0.08 * a  # presenter frame pushes in while fading out
                M = cv2.getRotationMatrix2D((W / 2, H / 2), 0, z)
                pz = cv2.warpAffine(last, M, (W, H))
                out = pz * (1 - a) + out * a
        draw_sub(out, t)
        if t > DUR - 0.35:  # tiny fade to black at the very end
            out *= max(0, (DUR - t) / 0.35)
        o8 = out.clip(0, 255).astype(np.uint8)
        if only is not None:
            if i in only: Image.fromarray(o8).save(f"fr/{os.environ.get('CFG','v2')}_{i:03d}.jpg", quality=90)
            if i >= max(only): break
        else:
            enc.stdin.write(o8.tobytes())
            if i % 90 == 0: print(i, flush=True)
    if enc: enc.stdin.close(); enc.wait(); print('rc', enc.returncode)

if __name__ == '__main__':
    if len(sys.argv) > 2:
        main(None, set(int(x) for x in sys.argv[2].split(',')))
    else:
        main(sys.argv[1])
