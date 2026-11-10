"""Backgrounds for videos 3, 4, 5 (same visual system as art.py)."""
import math, os
from art import *

def scene(c1, c2, glowc, seed):
    b = grad(c1, c2); grid(b, glowc); glow(b, (594, 700), 440, glowc, 130); particles(b, glowc, seed=seed)
    return b

WHITE = (255, 255, 255, 255)
def A(c, a=255): return c + (a,)

# ---------- icon primitives (drawn on a Hi layer, centered at cx,cy) ----------
def db(h, cx, cy, s, col):
    w, eh = 220 * s, 60 * s
    for i in range(3):
        y = cy - 150 * s + i * 110 * s
        h.rrect(cx - w / 2, y, cx + w / 2, y + 110 * s, 0, fill=A(col, 230))
        h.ell(cx - w / 2, y + 110 * s - eh / 2, cx + w / 2, y + 110 * s + eh / 2, fill=A(col, 230))
        h.ell(cx - w / 2, y - eh / 2, cx + w / 2, y + eh / 2, fill=WHITE if i == 0 else A(col, 255), outline=A((255, 255, 255), 140), w=3)

def bars(h, x, base, heights, col, bw=90, gap=40):
    for i, ht in enumerate(heights):
        xx = x + i * (bw + gap)
        h.rrect(xx, base - ht, xx + bw, base, 16, fill=A(col, 150 + i * 20 if 150 + i * 20 < 255 else 255))

def magnifier(h, cx, cy, r, col):
    h.ell(cx - r, cy - r, cx + r, cy + r, fill=(255, 255, 255, 40), outline=A(col), w=int(r * 0.16))
    a = math.radians(45)
    h.line([(cx + r * 0.95 * math.cos(a), cy + r * 0.95 * math.sin(a)), (cx + r * 1.9 * math.cos(a), cy + r * 1.9 * math.sin(a))], A(col), int(r * 0.24))

def target(h, cx, cy, r, col):
    for i, k in enumerate([1, 0.7, 0.4]):
        h.ell(cx - r * k, cy - r * k, cx + r * k, cy + r * k, fill=A(col) if i % 2 == 0 else (14, 20, 40, 255))
    h.ell(cx - r * 0.15, cy - r * 0.15, cx + r * 0.15, cy + r * 0.15, fill=WHITE)
    h.line([(cx, cy), (cx + r * 1.1, cy - r * 1.1)], WHITE, 12)
    h.poly([(cx + r * 1.1, cy - r * 1.1), (cx + r * 1.35, cy - r * 1.05), (cx + r * 1.05, cy - r * 1.35)], WHITE)

def bulb(h, cx, cy, r, col):
    h.ell(cx - r, cy - r, cx + r, cy + r, fill=A(col))
    h.rrect(cx - r * 0.45, cy + r * 0.7, cx + r * 0.45, cy + r * 1.35, 14, fill=(230, 235, 245, 255))
    for i in range(2):
        y = cy + r * 0.88 + i * r * 0.2
        h.line([(cx - r * 0.45, y), (cx + r * 0.45, y)], (150, 160, 180, 255), 5)
    for k in range(8):
        a = math.radians(k * 45 - 90)
        if 0 < k < 4 or 4 < k:
            pass
        h.line([(cx + r * 1.25 * math.cos(a), cy + r * 1.25 * math.sin(a)), (cx + r * 1.55 * math.cos(a), cy + r * 1.55 * math.sin(a))], A(col, 200), 10)

def robot(h, cx, cy, s, col):
    h.line([(cx, cy - 170 * s), (cx, cy - 120 * s)], A(col), int(12 * s))
    h.ell(cx - 22 * s, cy - 200 * s, cx + 22 * s, cy - 156 * s, fill=A(col))
    h.rrect(cx - 170 * s, cy - 120 * s, cx + 170 * s, cy + 110 * s, 60 * s, fill=(240, 244, 255, 255))
    h.rrect(cx - 130 * s, cy - 80 * s, cx + 130 * s, cy + 50 * s, 40 * s, fill=(20, 18, 50, 255))
    for dx in (-60, 60):
        h.ell(cx + dx * s - 24 * s, cy - 40 * s, cx + dx * s + 24 * s, cy + 8 * s, fill=A(col))
    h.rrect(cx - 50 * s, cy + 66 * s, cx + 50 * s, cy + 82 * s, 8 * s, fill=(160, 170, 200, 255))
    h.rrect(cx - 200 * s, cy - 40 * s, cx - 170 * s, cy + 40 * s, 12 * s, fill=A(col))
    h.rrect(cx + 170 * s, cy - 40 * s, cx + 200 * s, cy + 40 * s, 12 * s, fill=A(col))

def bubble(h, x0, y0, x1, y1, fill, tail_left=True, lines=3, linec=(180, 190, 220, 255)):
    h.rrect(x0, y0, x1, y1, 40, fill=fill)
    tx = x0 + 70 if tail_left else x1 - 70
    h.poly([(tx - 25, y1 - 5), (tx + 25, y1 - 5), (tx - 40 if tail_left else tx + 40, y1 + 45)], fill)
    for i in range(lines):
        yy = y0 + 45 + i * 45
        if yy + 16 > y1 - 25: break
        h.rrect(x0 + 40, yy, x1 - 40 - (i % 2) * 70, yy + 16, 8, fill=linec)

def flow(h, cx, cy, col):
    xs = [cx - 330, cx, cx + 330]
    for i, x in enumerate(xs):
        h.rrect(x - 120, cy - 80, x + 120, cy + 80, 30, fill=(240, 246, 255, 255) if i != 1 else A(col))
        h.ell(x - 26, cy - 26, x + 26, cy + 26, fill=A(col) if i != 1 else WHITE)
    for x in xs[:2]:
        h.line([(x + 130, cy), (x + 190, cy)], WHITE, 10)
        h.poly([(x + 210, cy), (x + 186, cy - 18), (x + 186, cy + 18)], WHITE)

def puzzle(h, cx, cy, s, cols):
    for i, (dx, dy) in enumerate([(-1, -1), (1, -1), (-1, 1), (1, 1)]):
        x, y = cx + dx * 105 * s, cy + dy * 105 * s
        off = 10 * s if i == 3 else 0
        h.rrect(x - 95 * s + off, y - 95 * s + off, x + 95 * s + off, y + 95 * s + off, 22 * s, fill=A(cols[i]))
    # knobs
    h.ell(cx - 30 * s, cy - 135 * s, cx + 30 * s, cy - 75 * s, fill=A(cols[0]))
    h.ell(cx - 135 * s, cy - 30 * s, cx - 75 * s, cy + 30 * s, fill=A(cols[0]))
    h.ell(cx + 75 * s, cy - 30 * s, cx + 135 * s, cy + 30 * s, fill=A(cols[1]))

def sliders(h, cx, cy, col):
    h.rrect(cx - 260, cy - 200, cx + 260, cy + 200, 40, fill=(240, 246, 255, 255))
    for i, p in enumerate([0.3, 0.75, 0.5]):
        y = cy - 110 + i * 110
        h.rrect(cx - 200, y - 8, cx + 200, y + 8, 8, fill=(190, 200, 225, 255))
        h.rrect(cx - 200, y - 8, cx - 200 + 400 * p, y + 8, 8, fill=A(col))
        kx = cx - 200 + 400 * p
        h.ell(kx - 30, y - 30, kx + 30, y + 30, fill=WHITE, outline=A(col), w=8)

def calendar(h, cx, cy, s, col):
    w, ht = 300 * s, 300 * s
    h.rrect(cx - w / 2, cy - ht / 2, cx + w / 2, cy + ht / 2, 36 * s, fill=(245, 248, 255, 255))
    h.rrect(cx - w / 2, cy - ht / 2, cx + w / 2, cy - ht / 2 + 80 * s, 36 * s, fill=A(col))
    h.rrect(cx - w / 2, cy - ht / 2 + 40 * s, cx + w / 2, cy - ht / 2 + 80 * s, 0, fill=A(col))
    for dx in (-80, 80):
        h.rrect(cx + dx * s - 12 * s, cy - ht / 2 - 30 * s, cx + dx * s + 12 * s, cy - ht / 2 + 30 * s, 10 * s, fill=(60, 60, 90, 255))
    for r_ in range(3):
        for c_ in range(4):
            x = cx - 105 * s + c_ * 70 * s; y = cy - 35 * s + r_ * 60 * s
            fill = A(col) if (r_, c_) == (1, 2) else (200, 208, 230, 255)
            h.rrect(x - 22 * s, y - 18 * s, x + 22 * s, y + 18 * s, 8 * s, fill=fill)
    if True:
        x = cx - 105 * s + 2 * 70 * s; y = cy - 35 * s + 60 * s
        h.line([(x - 12 * s, y), (x - 2 * s, y + 10 * s), (x + 14 * s, y - 10 * s)], WHITE, int(6 * s))

def network(h, cx, cy, r, col, col2):
    pts = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in range(-90, 270, 60)]
    for p in pts:
        h.line([(cx, cy), p], A(col, 150), 6)
    for i in range(len(pts)):
        h.line([pts[i], pts[(i + 1) % len(pts)]], A(col, 90), 4)
    for p in pts:
        h.ell(p[0] - 46, p[1] - 46, p[0] + 46, p[1] + 46, fill=(16, 14, 40, 255), outline=A(col2), w=8)
        h.ell(p[0] - 16, p[1] - 16, p[0] + 16, p[1] + 16, fill=A(col2))

def pres(c1, c2, glowc, seed, draw, label, acc, path):
    b = scene(c1, c2, glowc, seed)
    h = Hi(); draw(h); h.out(b, k=0.74)
    chip(b, label, acc)
    b.convert('RGB').save(path)

def cta_card(title1, title2, sub1, sub2, button, foot, path, acc=(190, 170, 255)):
    b = grad((30, 16, 70), (6, 8, 24)); grid(b, (180, 160, 255), alpha=18)
    glow(b, (594, 900), 520, (130, 90, 255), 160); glow(b, (594, 1300), 300, (0, 210, 255), 100); particles(b, (200, 190, 255), seed=31)
    h = Hi()
    fT = font('InterDisplay-Black.otf', 100); fS = font('InterDisplay-Medium.otf', 52); fB = font('InterDisplay-Bold.otf', 54)
    h.text((W / 2, 640), title1, fT, WHITE)
    h.text((W / 2, 752), title2, fT, A(acc))
    h.text((W / 2, 930), sub1, fS, (225, 230, 245, 255))
    if sub2: h.text((W / 2, 996), sub2, fS, (225, 230, 245, 255))
    h.rrect(214, 1130, 974, 1270, 70, fill=WHITE)
    h.text((W / 2, 1202), button, fB, (40, 20, 100, 255))
    h.text((W / 2, 1360), foot, fB, (200, 205, 230, 255))
    h.out(b, shadow=False)
    b.convert('RGB').save(path)

PURPLE, CYAN, GREEN, CORAL, AMBER = (150, 120, 255), (0, 210, 255), (40, 230, 150), (255, 120, 90), (255, 190, 60)
VIOLET_BG, BLUE_BG, GREEN_BG, WARM_BG = ((22, 14, 58), (6, 10, 30)), ((6, 40, 60), (4, 12, 26)), ((6, 46, 34), (4, 16, 18)), ((44, 14, 22), (14, 8, 20))

def v3():
    o = 'bg3'; os.makedirs(o, exist_ok=True)
    def d1(h):
        db(h, 594, 620, 1.2, CYAN)
        for i, (x, y) in enumerate([(200, 480), (990, 520), (230, 900), (960, 880)]):
            h.rrect(x - 70, y - 85, x + 70, y + 85, 16, fill=(230, 245, 255, 230))
            for j in range(3): h.rrect(x - 45, y - 50 + j * 36, x + 45 - (j % 2) * 25, y - 38 + j * 36, 6, fill=A(CYAN, 200))
    pres(*BLUE_BG, CYAN, 41, d1, 'INFORMACIÓN TODOS LOS DÍAS', CYAN, f'{o}/p1.png')
    def d2(h):
        bars(h, 300, 1000, [200, 320, 260, 420], (120, 130, 160), bw=110, gap=40)
        h.text((594, 560), '?', font('InterDisplay-Black.otf', 380), A(AMBER))
    pres(*WARM_BG, CORAL, 42, d2, '¿APROVECHÁS TUS DATOS?', AMBER, f'{o}/p2.png')
    def d3(h):
        bars(h, 260, 1020, [220, 360, 300, 520, 640], PURPLE, bw=100, gap=36)
        magnifier(h, 720, 560, 150, WHITE[:3])
    pres(*VIOLET_BG, PURPLE, 43, d3, 'ANÁLISIS CON IA', PURPLE, f'{o}/p3.png')
    def d4(h):
        target(h, 594, 680, 230, GREEN)
    pres(*GREEN_BG, GREEN, 44, d4, 'MEJORES DECISIONES', GREEN, f'{o}/p4.png')
    def d5(h):
        bulb(h, 594, 620, 180, AMBER)
    pres(*VIOLET_BG, PURPLE, 45, d5, 'SABER UTILIZARLOS', AMBER, f'{o}/p5.png')
    def ic1(h): db(h, 594, 790, 0.9, PURPLE); magnifier(h, 700, 700, 80, WHITE[:3])
    def ic2(h): bars(h, 400, 960, [120, 200, 160, 280], CYAN, bw=70, gap=30); h.line([(420, 860), (520, 780), (620, 820), (760, 650)], WHITE, 12)
    def ic3(h): target(h, 580, 790, 170, GREEN)
    card(((24, 14, 62), (6, 8, 26)), PURPLE, 'Analizá\ninformación', 'Convertí datos dispersos\nen respuestas claras', ic1, 1).convert('RGB').save(f'{o}/c1.png')
    card(((4, 36, 58), (4, 10, 24)), CYAN, 'Detectá\npatrones', 'Tendencias que a simple\nvista no se ven', ic2, 2).convert('RGB').save(f'{o}/c2.png')
    card(((4, 44, 34), (4, 14, 16)), GREEN, 'Decidí\nmejor', 'Información concreta\npara cada decisión', ic3, 3).convert('RGB').save(f'{o}/c3.png')
    cta_card('¿Tus datos ya', 'trabajan para vos?', 'Descubrí lo que la IA puede', 'hacer con tu información', 'Agendá una demo', 'pampai.com', f'{o}/cta.png')

def v4():
    o = 'bg4'; os.makedirs(o, exist_ok=True)
    def d1(h): robot(h, 594, 680, 1.25, CYAN)
    pres(*VIOLET_BG, PURPLE, 51, d1, 'ASISTENTES INTELIGENTES', CYAN, f'{o}/p1.png')
    def d2(h): network(h, 594, 660, 280, PURPLE, CYAN); robot(h, 594, 690, 0.42, PURPLE)
    pres(*BLUE_BG, CYAN, 52, d2, 'AGENTES DE IA', CYAN, f'{o}/p2.png')
    def d3(h): flow(h, 594, 640, GREEN)
    pres(*GREEN_BG, GREEN, 53, d3, 'PROCESOS Y TAREAS', GREEN, f'{o}/p3.png')
    def d4(h):
        bubble(h, 150, 420, 700, 640, (240, 244, 255, 255))
        bubble(h, 480, 720, 1040, 940, A(PURPLE), tail_left=False, linec=(220, 210, 255, 255))
        gear(h, 1000, 480, 80, 8, A(CYAN), (6, 10, 30, 255))
    pres(*VIOLET_BG, PURPLE, 54, d4, 'MÁS QUE RESPONDER PREGUNTAS', PURPLE, f'{o}/p4.png')
    def ic1(h):
        bubble(h, 390, 600, 740, 760, (240, 244, 255, 255), lines=2)
        bubble(h, 450, 820, 800, 960, A(PURPLE), tail_left=False, lines=2, linec=(220, 210, 255, 255))
    def ic2(h): flow(h, 594, 780, CYAN) if False else [h.rrect(400 + i * 150, 720, 490 + i * 150, 840, 24, fill=A(CYAN) if i == 1 else (240, 246, 255, 255)) for i in range(3)] + [h.line([(495 + i * 150, 780), (545 + i * 150, 780)], WHITE, 8) for i in range(2)]
    def ic3(h): robot(h, 594, 800, 0.85, GREEN)
    card(((24, 14, 62), (6, 8, 26)), PURPLE, 'Interactúan', 'Con clientes, equipos\ny sistemas', ic1, 1).convert('RGB').save(f'{o}/c1.png')
    card(((4, 36, 58), (4, 10, 24)), CYAN, 'Gestionan\nprocesos', 'De punta a punta,\ncon menos tareas manuales', ic2, 2).convert('RGB').save(f'{o}/c2.png')
    card(((4, 44, 34), (4, 14, 16)), GREEN, 'Ejecutan\ntareas', 'Según las necesidades\nde tu negocio', ic3, 3).convert('RGB').save(f'{o}/c3.png')
    cta_card('Sumá agentes', 'de IA a tu empresa', 'Te mostramos cómo', 'funcionan en tu negocio', 'Agendá una demo', 'pampai.com', f'{o}/cta.png')

def v5():
    o = 'bg5'; os.makedirs(o, exist_ok=True)
    def d1(h): puzzle(h, 594, 660, 1.15, [PURPLE, CYAN, GREEN, CORAL])
    pres(*VIOLET_BG, PURPLE, 61, d1, 'CADA EMPRESA ES ÚNICA', PURPLE, f'{o}/p1.png')
    def d2(h): sliders(h, 594, 660, CYAN)
    pres(*BLUE_BG, CYAN, 62, d2, 'SOLUCIONES A MEDIDA', CYAN, f'{o}/p2.png')
    def d3(h):
        network(h, 594, 660, 270, GREEN, GREEN)
        h.ell(594 - 110, 660 - 110, 594 + 110, 660 + 110, fill=WHITE)
        h.text((594, 664), 'IA', font('InterDisplay-Black.otf', 110), (20, 60, 50, 255))
    pres(*GREEN_BG, GREEN, 63, d3, 'PAMPAI · IA EN TUS PROCESOS', GREEN, f'{o}/p3.png')
    def d4(h): calendar(h, 594, 680, 1.4, PURPLE)
    pres(*VIOLET_BG, PURPLE, 64, d4, 'AGENDÁ UNA DEMO', PURPLE, f'{o}/p4.png')
    def ic1(h): sliders(h, 594, 790, PURPLE) if False else [h.rrect(434, 650 + i * 100, 754, 666 + i * 100, 8, fill=(190, 200, 225, 255)) for i in range(3)] + [h.ell(434 + p * 320 - 28, 630 + i * 100, 434 + p * 320 + 28, 686 + i * 100, fill=WHITE, outline=A(PURPLE), w=8) for i, p in enumerate([0.3, 0.75, 0.5])]
    def ic2(h): flow(h, 594, 780, GREEN) if False else [h.rrect(400 + i * 150, 720, 490 + i * 150, 840, 24, fill=A(CYAN) if i == 1 else (240, 246, 255, 255)) for i in range(3)] + [h.line([(495 + i * 150, 780), (545 + i * 150, 780)], WHITE, 8) for i in range(2)]
    card(((24, 14, 62), (6, 8, 26)), PURPLE, 'Soluciones\na medida', 'Adaptadas a los desafíos\nde tu negocio', ic1, 1).convert('RGB').save(f'{o}/c1.png')
    card(((4, 36, 58), (4, 10, 24)), CYAN, 'IA en tus\nprocesos', 'Te ayudamos a\nincorporarla paso a paso', ic2, 2).convert('RGB').save(f'{o}/c2.png')
    cta_card('Conocé nuestras', 'soluciones', '¿Querés conocer las', 'posibilidades para tu empresa?', 'Agendá una demo', 'pampai.com', f'{o}/cta.png')

if __name__ == '__main__':
    v3(); v4(); v5(); print('ok')
