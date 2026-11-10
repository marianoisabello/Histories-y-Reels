def pres_scenes(C, pend):
    st = C['pres_starts']; names = C['pres_names']
    return [(n, st[i], st[i + 1] if i + 1 < len(st) else pend + 0.4) for i, n in enumerate(names)]

def card_scenes(C, pend, dur, cta_len=4.5):
    cards = C['card_names'][:-1]
    each = (dur - pend - cta_len) / len(cards)
    out = [(n, pend + i * each, pend + (i + 1) * each) for i, n in enumerate(cards)]
    out.append(('cta', pend + len(cards) * each, dur + 0.5))
    return out

CFG = {
    'v3': dict(dir='v3', bg='bg3', nfr=466,
               pres_names=['p1', 'p2', 'p3', 'p4', 'p5'], pres_starts=[0, 2.35, 4.45, 7.7, 10.95],
               card_names=['c1', 'c2', 'c3', 'cta'],
               segs=[(0.35, 2.25, ['Tu empresa genera', 'información todos los días,']),
                     (2.45, 4.25, ['pero ¿estás aprovechando', 'esos datos?']),
                     (4.6, 7.6, ['La inteligencia artificial', 'permite analizar información,']),
                     (7.75, 10.85, ['detectar patrones', 'y obtener herramientas', 'para tomar mejores decisiones.']),
                     (11.05, 13.3, ['No se trata solamente', 'de tener datos,']),
                     (13.55, 15.25, ['se trata de saber', 'utilizarlos.'])]),
    'v4': dict(dir='v4', bg='bg4', nfr=525,
               pres_names=['p1', 'p2', 'p3', 'p4'], pres_starts=[0, 5.2, 8.9, 13.0],
               card_names=['c1', 'c2', 'c3', 'cta'],
               segs=[(0.1, 3.05, ['¿Y si tu empresa', 'pudiera contar con', 'asistentes inteligentes']),
                     (3.2, 4.7, ['para realizar', 'diferentes tareas?']),
                     (5.7, 8.8, ['Los agentes de', 'inteligencia artificial', 'pueden interactuar,']),
                     (8.95, 12.75, ['gestionar procesos', 'y ejecutar tareas', 'según las necesidades', 'de cada negocio.']),
                     (13.3, 16.8, ['La inteligencia artificial', 'va mucho más allá', 'de responder preguntas.'])]),
    'v5': dict(dir='v5', bg='bg5', nfr=571,
               pres_names=['p1', 'p2', 'p3', 'p4'], pres_starts=[0, 2.3, 6.15, 11.3],
               card_names=['c1', 'c2', 'cta'],
               segs=[(0.3, 2.2, ['Cada empresa tiene', 'desafíos diferentes,']),
                     (2.35, 5.95, ['por eso las soluciones', 'tecnológicas también', 'deberían adaptarse', 'a cada negocio.']),
                     (6.35, 10.85, ['En Pampai, te ayudamos', 'a descubrir cómo', 'incorporar inteligencia', 'artificial a tus procesos.']),
                     (11.7, 13.9, ['¿Querés conocer', 'las posibilidades', 'para tu empresa?']),
                     (14.3, 18.55, ['Conocé nuestras soluciones', 'y agendá una demo', 'en pampai.com.'])]),
}
