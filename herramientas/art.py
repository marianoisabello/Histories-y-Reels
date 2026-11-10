"""Draws the background illustrations (1188x2112, slightly larger than 1080x1920 for slow zoom)."""
import math, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1188, 2112
S = 2  # supersample
F = '/usr/share/fonts/opentype/inter/'
def font(name, size): return ImageFont.truetype(F + name, size)

def grad(c1, c2):
    im = Image.new('RGB', (W, H))
    d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(c1[i] * (1 - t) + c2[i] * t) for i in range(3)))
    return im.convert('RGBA')

def glow(base, xy, r, color, alpha=150):
    lay = Image.new('RGBA', base.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).ellipse([xy[0] - r, xy[1] - r, xy[0] + r, xy[1] + r], fill=color + (alpha,))
    lay = lay.filter(ImageFilter.GaussianBlur(r * 0.6))
    base.alpha_composite(lay)

def grid(base, color, step=72, alpha=22):
    lay = Image.new('RGBA', base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for x in range(0, W, step): d.line([(x, 0), (x, H)], fill=color + (alpha,), width=1)
    for y in range(0, H, step): d.line([(0, y), (W, y)], fill=color + (alpha,), width=1)
    base.alpha_composite(lay)

def particles(base, color, n=70, seed=1):
    rnd = random.Random(seed)
    lay = Image.new('RGBA', base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for _ in range(n):
        x, y, r = rnd.randint(0, W), rnd.randint(0, H), rnd.choice([2, 3, 3, 4, 6])
        d.ellipse([x - r, y - r, x + r, y + r], fill=color + (rnd.randint(60, 180),))
    base.alpha_composite(lay)

class Hi:
    """Supersampled drawing layer."""
    def __init__(self):
        self.im = Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)
    def p(self, *v): return [c * S for c in v]
    def rrect(self, x0, y0, x1, y1, r, fill=None, outline=None, w=0):
        self.d.rounded_rectangle(self.p(x0, y0, x1, y1), r * S, fill=fill, outline=outline, width=w * S)
    def ell(self, x0, y0, x1, y1, fill=None, outline=None, w=0):
        self.d.ellipse(self.p(x0, y0, x1, y1), fill=fill, outline=outline, width=w * S)
    def line(self, pts, fill, w):
        self.d.line([c * S for pt in pts for c in pt], fill=fill, width=w * S, joint='curve')
    def poly(self, pts, fill):
        self.d.polygon([c * S for pt in pts for c in pt], fill=fill)
    def text(self, xy, s, f, fill, anchor='mm'):
        ff = ImageFont.truetype(f.path, f.size * S)
        self.d.text((xy[0] * S, xy[1] * S), s, font=ff, fill=fill, anchor=anchor)
    def out(self, base, shadow=True, k=1.0):
        small = self.im.resize((W, H), Image.LANCZOS)
        if k != 1.0:
            sm = small.resize((int(W * k), int(H * k)), Image.LANCZOS)
            small = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            small.alpha_composite(sm, (int(594 - 594 * k), int(480 - 470 * k)))
        if shadow:
            sh = Image.new('RGBA', small.size, (0, 0, 0, 0))
            sh.putalpha(small.getchannel('A').point(lambda a: a * 0.5))
            sh = sh.filter(ImageFilter.GaussianBlur(18))
            base.alpha_composite(sh, (0, 14))
        base.alpha_composite(small)

def clock(h, cx, cy, r, ring, face, hand, ticks=True, ang=(300, 60)):
    h.ell(cx - r, cy - r, cx + r, cy + r, fill=face, outline=ring, w=int(r * 0.09))
    if ticks:
        for i in range(12):
            a = math.radians(i * 30)
            r1, r2 = r * 0.72, r * (0.84 if i % 3 else 0.88)
            h.line([(cx + r1 * math.sin(a), cy - r1 * math.cos(a)), (cx + r2 * math.sin(a), cy - r2 * math.cos(a))], ring, max(3, int(r * 0.03)))
    for a, L, w in [(ang[0], 0.45, 0.06), (ang[1], 0.65, 0.04)]:
        a = math.radians(a)
        h.line([(cx, cy), (cx + r * L * math.sin(a), cy - r * L * math.cos(a))], hand, int(r * w))
    h.ell(cx - r * 0.07, cy - r * 0.07, cx + r * 0.07, cy + r * 0.07, fill=hand)

def gear(h, cx, cy, r, teeth, fill, hole):
    pts = []
    for i in range(teeth * 4):
        a = 2 * math.pi * i / (teeth * 4)
        rr = r if (i % 4) in (0, 1) else r * 0.8
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    h.poly(pts, fill)
    h.ell(cx - r * 0.35, cy - r * 0.35, cx + r * 0.35, cy + r * 0.35, fill=hole)

def doc(h, x, y, w, ht, paper, line, rot_shift=0):
    h.rrect(x, y, x + w, y + ht, 18, fill=paper)
    for i in range(5):
        yy = y + 50 + i * 42
        h.rrect(x + 36, yy, x + w - 36 - (i % 2) * 60, yy + 14, 7, fill=line)

def chip(base, text, accent, y=330):
    h = Hi()
    f = font('InterDisplay-Bold.otf', 40)
    tw = ImageDraw.Draw(Image.new('L', (1, 1))).textlength(text, font=f)
    x0 = (W - tw) / 2 - 48
    h.rrect(x0, y - 40, W - x0, y + 40, 40, fill=(10, 14, 30, 200), outline=accent + (255,), w=3)
    h.ell(x0 + 22, y - 9, x0 + 40, y + 9, fill=accent + (255,))
    h.text((W / 2 + 12, y + 2), text, f, (255, 255, 255, 255))
    h.out(base, shadow=False)

# ---------------- presenter backgrounds ----------------
def p1():  # repetitive tasks: clock + piles of documents, warm
    b = grad((44, 14, 22), (14, 8, 20)); grid(b, (255, 140, 120)); glow(b, (594, 700), 420, (255, 90, 60), 120)
    particles(b, (255, 170, 140), seed=2)
    h = Hi()
    for i, (x, y) in enumerate([(90, 980), (110, 930), (80, 880), (100, 830)]):
        doc(h, x, y, 230, 300, (255, 236, 228, 255), (230, 150, 140, 255))
    for i, (x, y) in enumerate([(860, 1000), (880, 950), (850, 900)]):
        doc(h, x, y, 230, 300, (255, 236, 228, 255), (230, 150, 140, 255))
    clock(h, 594, 680, 230, (255, 120, 90, 255), (32, 12, 20, 255), (255, 255, 255, 255), ang=(320, 140))
    h.out(b, k=0.74)
    return b

def p2():  # AI: neural network + gears, violet/cyan
    b = grad((22, 14, 58), (6, 10, 30)); grid(b, (140, 160, 255)); glow(b, (594, 640), 460, (120, 80, 255), 140)
    glow(b, (200, 1100), 260, (0, 200, 255), 90); particles(b, (170, 190, 255), seed=3)
    h = Hi()
    layers = [[(250, 470), (250, 680), (250, 890)], [(594, 400), (594, 600), (594, 800), (594, 1000)], [(938, 520), (938, 760), (938, 960)]]
    for a, bb in [(0, 1), (1, 2)]:
        for p in layers[a]:
            for q in layers[bb]:
                h.line([p, q], (150, 170, 255, 110), 3)
    for li, L in enumerate(layers):
        for (x, y) in L:
            col = [(0, 220, 255, 255), (170, 120, 255, 255), (0, 230, 180, 255)][li]
            h.ell(x - 44, y - 44, x + 44, y + 44, fill=(14, 12, 40, 255), outline=col, w=8)
            h.ell(x - 16, y - 16, x + 16, y + 16, fill=col)
    gear(h, 140, 1240, 110, 10, (120, 100, 255, 230), (6, 10, 30, 255))
    gear(h, 1050, 1180, 80, 8, (0, 200, 255, 230), (6, 10, 30, 255))
    h.out(b, k=0.74)
    return b

def p3():  # efficiency: checklist done + fast clock, cyan
    b = grad((6, 40, 60), (4, 12, 26)); grid(b, (120, 230, 255)); glow(b, (594, 700), 440, (0, 190, 230), 130)
    particles(b, (160, 240, 255), seed=4)
    h = Hi()
    # checklist card left
    h.rrect(70, 520, 470, 1060, 36, fill=(240, 252, 255, 255))
    for i in range(4):
        y = 600 + i * 118
        h.rrect(110, y, 170, y + 60, 14, fill=(0, 200, 160, 255))
        h.line([(124, y + 31), (137, y + 45), (158, y + 16)], (255, 255, 255, 255), 8)
        h.rrect(200, y + 18, 430 - (i % 2) * 60, y + 42, 12, fill=(170, 210, 225, 255))
    # stopwatch right
    cx, cy, r = 850, 760, 220
    h.rrect(cx - 34, cy - r - 70, cx + 34, cy - r + 10, 14, fill=(0, 220, 255, 255))
    clock(h, cx, cy, r, (0, 220, 255, 255), (6, 26, 40, 255), (255, 255, 255, 255), ang=(30, 90))
    for i in range(3):  # speed lines
        h.rrect(cx - r - 150 + i * 20, cy - 60 + i * 60, cx - r - 30, cy - 46 + i * 60, 7, fill=(0, 220, 255, 160))
    h.out(b, k=0.74)
    return b

def p4():  # growth: bars + arrow, green
    b = grad((6, 46, 34), (4, 16, 18)); grid(b, (120, 255, 190)); glow(b, (700, 600), 460, (0, 220, 130), 130)
    particles(b, (170, 255, 210), seed=5)
    h = Hi()
    base_y = 1150
    for i, ht in enumerate([180, 300, 430, 600, 780]):
        x = 110 + i * 200
        h.rrect(x, base_y - ht, x + 140, base_y, 22, fill=(40, 230, 150, 120 + i * 30))
    pts = [(120, 1000), (330, 900), (520, 930), (740, 700), (1000, 440)]
    h.line(pts, (255, 255, 255, 255), 18)
    h.poly([(1060, 380), (950, 410), (1035, 495)], (255, 255, 255, 255))
    h.out(b, k=0.74)
    return b

# ---------------- full-screen cards ----------------
def card(bgc, glowc, title, sub, icon, num):
    b = grad(*bgc); grid(b, glowc, alpha=18); glow(b, (594, 820), 470, glowc, 150); particles(b, glowc, seed=10 + num)
    h = Hi()
    # icon plate
    h.rrect(294, 470, 894, 1070, 120, fill=(255, 255, 255, 24), outline=glowc + (255,), w=4)
    icon(h)
    h.out(b)
    h = Hi()
    fT = font('InterDisplay-Black.otf', 100); fS = font('InterDisplay-Medium.otf', 50); fN = font('InterDisplay-Bold.otf', 38)
    h.text((W / 2, 380), f'0{num}', fN, glowc + (255,))
    lines = title.split('\n')
    for i, ln in enumerate(lines):
        h.text((W / 2, 1230 + i * 112), ln, fT, (255, 255, 255, 255))
    y = 1230 + len(lines) * 112 + 30
    for i, ln in enumerate(sub.split('\n')):
        h.text((W / 2, y + i * 66), ln, fS, (220, 228, 245, 255))
    h.out(b, shadow=False)
    return b

def icon_flow(h):
    g = (170, 140, 255, 255)
    gear(h, 520, 700, 150, 10, g, (30, 20, 70, 255))
    gear(h, 720, 880, 100, 8, (0, 220, 255, 255), (30, 20, 70, 255))
    h.ell(470, 650, 570, 750, fill=(255, 255, 255, 255))
    h.text((520, 702), 'IA', font('InterDisplay-Black.otf', 48), (40, 20, 90, 255))

def icon_time(h):
    clock(h, 594, 770, 200, (0, 220, 255, 255), (6, 26, 40, 255), (255, 255, 255, 255), ang=(60, 0))
    h.line([(594 - 230, 770 - 120), (594 - 290, 770 - 120)], (0, 220, 255, 180), 12)
    h.line([(594 - 240, 770), (594 - 320, 770)], (0, 220, 255, 180), 12)
    h.line([(594 - 230, 770 + 120), (594 - 290, 770 + 120)], (0, 220, 255, 180), 12)

def icon_simple(h):
    h.rrect(424, 590, 764, 950, 40, fill=(240, 255, 248, 255))
    for i in range(3):
        y = 640 + i * 100
        h.ell(460, y, 520, y + 60, fill=(0, 200, 140, 255))
        h.line([(474, y + 31), (487, y + 45), (507, y + 16)], (255, 255, 255, 255), 8)
        h.rrect(545, y + 18, 720 - (i % 2) * 50, y + 42, 12, fill=(170, 220, 200, 255))

def cta():
    b = grad((30, 16, 70), (6, 8, 24)); grid(b, (180, 160, 255), alpha=18)
    glow(b, (594, 900), 520, (130, 90, 255), 160); glow(b, (594, 1300), 300, (0, 210, 255), 100); particles(b, (200, 190, 255), seed=30)
    h = Hi()
    fT = font('InterDisplay-Black.otf', 104); fS = font('InterDisplay-Medium.otf', 52); fB = font('InterDisplay-Bold.otf', 54)
    h.text((W / 2, 640), '¿Listo para', fT, (255, 255, 255, 255))
    h.text((W / 2, 756), 'automatizar?', fT, (190, 170, 255, 255))
    h.text((W / 2, 930), 'Te mostramos cómo la IA', fS, (225, 230, 245, 255))
    h.text((W / 2, 996), 'puede ayudar a tu empresa', fS, (225, 230, 245, 255))
    h.rrect(224, 1130, 964, 1270, 70, fill=(255, 255, 255, 255))
    h.text((W / 2, 1202), 'Escribinos por DM', fB, (40, 20, 100, 255))
    h.text((W / 2, 1360), 'o respondé esta historia', fS, (200, 205, 230, 255))
    h.out(b, shadow=False)
    return b

if __name__ == '__main__':
    import os
    os.makedirs('bg', exist_ok=True)
    for name, fn, label, acc in [('p1', p1, 'TAREAS REPETITIVAS', (255, 120, 90)), ('p2', p2, 'AUTOMATIZACIÓN CON IA', (150, 130, 255)),
                                 ('p3', p3, 'MÁS EFICIENCIA', (0, 220, 255)), ('p4', p4, 'HACÉ CRECER TU NEGOCIO', (40, 230, 150))]:
        im = fn(); chip(im, label, acc); im.convert('RGB').save(f'bg/{name}.png')
    card(((24, 14, 62), (6, 8, 26)), (150, 120, 255), 'Automatizá\nprocesos', 'Flujos que trabajan solos,\nlas 24 horas', icon_flow, 1).convert('RGB').save('bg/c1.png')
    card(((4, 36, 58), (4, 10, 24)), (0, 210, 255), 'Optimizá\ntiempos', 'Respuestas y reportes\nen minutos, no en horas', icon_time, 2).convert('RGB').save('bg/c2.png')
    card(((4, 44, 34), (4, 14, 16)), (40, 230, 150), 'Simplificá\ntu día a día', 'Menos carga manual\npara tu equipo', icon_simple, 3).convert('RGB').save('bg/c3.png')
    cta().convert('RGB').save('bg/cta.png')
    print('ok')
