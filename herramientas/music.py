"""Synthesizes a soft corporate pad + pluck bed (30 s, 48 kHz stereo) and mixes the presenter's voice."""
import numpy as np, wave, subprocess, os, cfgs
C = cfgs.CFG[os.environ["CFG"]]
SR = 48000; DUR = 30.0; N = int(SR * DUR)
t = np.arange(N) / SR
BPM = 100; beat = 60 / BPM
def midi(m): return 440 * 2 ** ((m - 69) / 12)
chords = [[57, 60, 64, 69], [53, 57, 60, 65], [48, 52, 55, 60], [55, 59, 62, 67]]  # Am F C G
bar = beat * 4
mus = np.zeros((N, 2))
rng = np.random.default_rng(0)
for b in range(int(DUR / bar) + 1):
    c = chords[b % 4]; s0 = int(b * bar * SR); s1 = min(N, int((b + 1) * bar * SR) + SR // 2)
    if s0 >= N: break
    tt = np.arange(s1 - s0) / SR
    env = np.minimum(tt / 0.6, 1) * np.exp(-np.maximum(tt - bar, 0) * 4)
    for k, m in enumerate(c):
        f = midi(m)
        for det, ch in [(-0.12, 0), (0.12, 1)]:
            ff = f * 2 ** (det / 12 / 10)
            v = (np.sin(2 * np.pi * ff * tt) + 0.3 * np.sin(4 * np.pi * ff * tt) + 0.12 * np.sin(6 * np.pi * ff * tt)) * env * 0.05
            mus[s0:s1, ch] += v
    # bass
    fb = midi(c[0] - 12)
    mus[s0:s1] += (np.sin(2 * np.pi * fb * tt) * env * 0.09)[:, None]
    # plucks on 8ths (arpeggio)
    for i in range(8):
        p0 = s0 + int(i * beat / 2 * SR); p1 = min(N, p0 + int(0.5 * SR))
        if p0 >= N: break
        pt = np.arange(p1 - p0) / SR
        f = midi(c[[0, 2, 1, 3, 2, 1, 3, 2][i]] + 12)
        v = np.sin(2 * np.pi * f * pt) * np.exp(-pt * 9) * 0.05
        pan = 0.5 + 0.3 * np.sin(i)
        mus[p0:p1, 0] += v * (1 - pan) * 2; mus[p0:p1, 1] += v * pan * 2
    # soft kick on beats + hat offbeats
    for i in range(4):
        k0 = s0 + int(i * beat * SR); k1 = min(N, k0 + int(0.25 * SR))
        if k0 >= N: break
        kt = np.arange(k1 - k0) / SR
        mus[k0:k1] += (np.sin(2 * np.pi * (50 + 80 * np.exp(-kt * 30)) * kt) * np.exp(-kt * 14) * 0.16)[:, None]
        h0 = k0 + int(beat / 2 * SR); h1 = min(N, h0 + int(0.05 * SR))
        if h0 < N:
            n = rng.standard_normal(h1 - h0); n = np.diff(n, prepend=0)
            mus[h0:h1] += (n * np.exp(-np.arange(h1 - h0) / SR * 70) * 0.012)[:, None]
# whooshes at transitions
PEND = C['nfr'] / 30
for tw in [s for _, s, _ in cfgs.pres_scenes(C, PEND)][1:] + [s for _, s, _ in cfgs.card_scenes(C, PEND, DUR)]:
    w0 = int((tw - 0.35) * SR); w1 = int((tw + 0.25) * SR); L = w1 - w0
    n = rng.standard_normal(L); n = np.convolve(n, np.ones(12) / 12, 'same')
    e = np.sin(np.linspace(0, np.pi, L)) ** 2
    mus[w0:w1] += (n * e * 0.10)[:, None]
# music level: low under voice, up after
lvl = np.where(t < PEND, 0.38, 0.85)
lvl = np.convolve(lvl, np.ones(SR // 2) / (SR // 2), 'same'); lvl[-SR // 4:] = lvl[-SR // 4 - 1]
mus *= lvl[:, None]
fade = np.minimum(1, (DUR - t) / 1.2); fade = np.clip(fade, 0, 1); mus *= fade[:, None]
mus *= np.minimum(1, t / 0.3)[:, None]
# voice
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', C['dir'] + '/src.mov', '-af', 'highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,loudnorm=I=-15:TP=-1.5',
                      '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], capture_output=True).stdout
v = np.frombuffer(raw, np.int16).astype(float) / 32768
mix = mus.copy(); mix[:len(v)] += v[:N, None] * 0.95
mix /= max(1.0, np.abs(mix).max() / 0.95)
with wave.open(C['dir'] + '/mix.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print('ok', len(v) / SR)
