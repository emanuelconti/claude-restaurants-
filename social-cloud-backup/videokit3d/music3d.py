"""Original music for a 3D Reel, written in code (tones only: piano, pad, bass, soft kick, bells).
    python music3d.py <style sp|sin|gms> <seed> <seconds> <beat_seconds> <end_card_start> <out.wav>
Cuts land on bars (4 beats); a bell marks every cut, a full chord the end card."""
import sys, wave
import numpy as np

style, seed, DUR, BEAT, END, out = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), sys.argv[6]
rng = np.random.default_rng(seed)
SR = 44100
N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N)
BAR = BEAT * 4


def hz(m): return 440.0 * 2 ** ((m - 69) / 12)


def put(sig, at, gain=1.0, pan=0.0):
    i = int(at * SR)
    if i >= N or i < 0: return
    sig = sig[: N - i]
    L[i:i + len(sig)] += sig * gain * (1 - pan); R[i:i + len(sig)] += sig * gain * (1 + pan)


def env(n, a=0.004, r=0.08):
    t = np.arange(n) / SR
    e = np.minimum(1, t / a); k = int(r * SR)
    if k < n: e[-k:] *= np.linspace(1, 0, k)
    return t, e


def piano(m, length=1.2, bright=1.0):
    n = int(length * SR); t, e = env(n); f = hz(m); s = np.zeros(n)
    for k, a in enumerate([1.0, 0.5, 0.28, 0.14, 0.08, 0.04], start=1):
        s += a * (bright if k > 2 else 1) * np.sin(2 * np.pi * f * k * t + 0.3 * k) * np.exp(-t * (1.6 + 1.2 * k))
    return (s + 0.25 * np.sin(2 * np.pi * f * 2.001 * t) * np.exp(-t * 4)) * e


def pad(notes, length):
    n = int(length * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for m in notes:
        for d in (-0.08, 0.0, 0.08):
            ff = hz(m) * 2 ** (d / 12); s += np.sin(2 * np.pi * ff * t) + 0.25 * np.sin(2 * np.pi * 2 * ff * t)
    return s * np.minimum(1, t / 0.6) * np.minimum(1, (length - t) / 0.6) / (len(notes) * 3)


def bass(m, length):
    n = int(length * SR); t, e = env(n, 0.01, 0.05); f = hz(m)
    return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t)) * e * np.exp(-t * 1.2)


def kick():
    n = int(0.4 * SR); t = np.arange(n) / SR; f = 42 + 70 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 8)


def tick(m=96):
    n = int(0.06 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * hz(m) * t) * np.exp(-t * 120)


def bell(m, length=2.0):
    n = int(length * SR); t = np.arange(n) / SR; f = hz(m)
    return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * 2.0 * f * t) * np.exp(-t * 3)) * np.exp(-t * 2.2)


PROGS = [[(57, [57, 60, 64]), (53, [53, 57, 60]), (48, [48, 52, 55]), (55, [55, 59, 62])],   # Am F C G
         [(48, [48, 52, 55]), (55, [55, 59, 62]), (57, [57, 60, 64]), (53, [53, 57, 60])],   # C G Am F
         [(50, [50, 53, 57]), (55, [55, 59, 62]), (48, [48, 52, 55]), (57, [57, 60, 64])],   # Dm G C Am
         [(53, [53, 57, 60]), (48, [48, 52, 55]), (55, [55, 59, 62]), (57, [57, 60, 64])]]   # F C G Am
prog = PROGS[seed % len(PROGS)]
shift = int(rng.integers(-2, 3))
prog = [(r + shift, [n + shift for n in ns]) for r, ns in prog]

# hook: a chord stab and a rising figure from the first frame
r0, n0 = prog[0]
put(pad([n + 12 for n in n0], BAR + 0.5) * 0.3, 0.0)
for k, m in enumerate(n0 + [n0[0] + 12]):
    put(piano(m + 12, 1.0) * 0.16, k * BEAT / 2, 1.0, -0.3 + 0.2 * k)
put(kick() * 0.5, 0.0)

t, bar = BAR, 1
while t < END - 0.01:
    root, notes = prog[bar % 4]
    put(pad([n + 12 for n in notes], min(BAR, END - t) + 0.4) * 0.22, t)
    for b in range(4):
        bt = t + b * BEAT
        if bt >= END: break
        if style == 'sp':   # warm latin groove: kick on 1 and 3, tonal ticks on the offbeats
            if b in (0, 2): put(kick() * 0.42, bt)
            put(tick(91) * 0.05, bt + BEAT * 0.75, 1.0, 0.3); put(tick(96) * 0.04, bt + BEAT * 0.5, 1.0, -0.3)
        elif style == 'sin':   # calm, steady
            if b == 0: put(kick() * 0.36, bt)
        else:   # gms: soft heartbeat
            if b in (0, 2): put(kick() * 0.3, bt)
        put(bass(root - 12, BEAT * 0.9) * 0.2, bt)
    arp = [notes[0] + 12, notes[1] + 12, notes[2] + 12, notes[0] + 24]
    for e in range(8):
        et = t + e * BEAT / 2
        if et < END and (style != 'sin' or e % 2 == 0):
            put(piano(arp[(e + bar) % 4], 0.7, 0.8) * (0.07 if style == 'gms' else 0.08), et, 1.0, -0.25 if e % 2 else 0.25)
    put(bell([84, 88, 91, 86][bar % 4] + shift) * 0.06, t, 1.0, 0.2)   # a bell on every cut
    t += BAR; bar += 1

# end card: one full chord that rings out
r1, n1 = prog[0]
put(kick() * 0.5, END)
put(pad([r1, *n1, n1[0] + 12, n1[2] + 12], DUR - END) * 0.45, END)
for k, m in enumerate([n1[0] + 12, n1[1] + 12, n1[2] + 12, n1[0] + 24]):
    put(piano(m, 3.0) * 0.14, END + 0.05 + k * 0.12, 1.0, -0.3 + 0.2 * k)

fo = int(1.2 * SR)
L[-fo:] *= np.linspace(1, 0, fo); R[-fo:] *= np.linspace(1, 0, fo)
peak = max(np.abs(L).max(), np.abs(R).max())
L, R = np.tanh(L / peak * 1.4) / np.tanh(1.4) * 0.9, np.tanh(R / peak * 1.4) / np.tanh(1.4) * 0.9
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.stack([L, R], axis=1) * 32767).astype(np.int16).tobytes())
