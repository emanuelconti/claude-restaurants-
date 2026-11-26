"""Soundtrack for the 72 s video, written as music, not effects: no noise
anywhere (the owner, 26 November: the whooshes and hats sounded strange).
Only tones: an electric-piano timbre, a warm pad, a round sub bass, a soft
kick and a short tonal tick, all in A minor (Am - F - C - G), 112 BPM.

Structure, matched to scene2.html:
  0.0 - 4.6   hook: one deep pulse and one piano stab on every cut, rising
  4.6 - 8.2   breath: pad alone, two sparse piano notes
  8.2 - 12.8  logo: a full chord, the groove fades in
  12.8 - 66.6 the story: kick, bass, piano arpeggio, pad; a bell on each
              number, a small lift every eight bars
  66.6 - 72   outro: the groove stops, a last chord rings out
"""
import wave
import numpy as np

SR = 44100
DUR = 48.0
N = int(SR * DUR)
L = np.zeros(N)
R = np.zeros(N)
BPM = 112
BEAT = 60 / BPM
BAR = BEAT * 4


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def put(sig, at, gain=1.0, pan=0.0):
    i = int(at * SR)
    if i >= N or i < 0:
        return
    sig = sig[: N - i]
    L[i : i + len(sig)] += sig * gain * (1 - pan)
    R[i : i + len(sig)] += sig * gain * (1 + pan)


def piano(m, length=1.2, bright=1.0):
    n = int(length * SR)
    t = np.arange(n) / SR
    f = hz(m)
    s = np.zeros(n)
    for k, a in enumerate([1.0, 0.5, 0.28, 0.14, 0.08, 0.04], start=1):
        s += a * (bright if k > 2 else 1) * np.sin(2 * np.pi * f * k * t + 0.3 * k) * np.exp(-t * (1.6 + 1.2 * k))
    s += 0.25 * np.sin(2 * np.pi * f * 2.001 * t) * np.exp(-t * 4)  # bell-ish shimmer
    att = np.minimum(1, t / 0.004)
    rel = np.ones(n)
    r = int(0.08 * SR)
    rel[-r:] = np.linspace(1, 0, r)
    return s * att * rel


def pad(notes, length):
    n = int(length * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for m in notes:
        f = hz(m)
        for d in (-0.08, 0.0, 0.08):
            ff = f * 2 ** (d / 12)
            s += np.sin(2 * np.pi * ff * t) + 0.25 * np.sin(2 * np.pi * 2 * ff * t)
    e = np.minimum(1, t / 0.9) * np.minimum(1, (length - t) / 0.9)
    return s * e / (len(notes) * 3)


def bass(m, length):
    n = int(length * SR)
    t = np.arange(n) / SR
    f = hz(m)
    s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t)
    e = np.minimum(1, t / 0.01) * np.exp(-t * 1.2)
    rel = np.ones(n)
    r = int(0.05 * SR)
    rel[-r:] = np.linspace(1, 0, r)
    return s * e * rel


def kick():
    n = int(0.4 * SR)
    t = np.arange(n) / SR
    f = 42 + 70 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 8)


def tick():
    n = int(0.03 * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * 3200 * t) * np.exp(-t * 220)


def pulse():
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    f = 36 + 60 * np.exp(-t * 14)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4.5)


def bell(m, length=2.0):
    n = int(length * SR)
    t = np.arange(n) / SR
    f = hz(m)
    return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * 2.0 * f * t) * np.exp(-t * 3)) * np.exp(-t * 2.2)


CHORDS = [(57, [57, 60, 64]), (53, [53, 57, 60]), (48, [48, 52, 55]), (55, [55, 59, 62])]  # Am F C G

# ---- 0-6: the city from above: a low pulse, a pad, piano notes falling like lights
put(pad([45, 52, 57, 60], 6.4) * 0.3, 0.0)
for i, m in enumerate([76, 72, 69, 64]):
    put(piano(m, 1.6) * 0.14, 0.6 + i * 1.1, 1.0, -0.3 + i * 0.2)
put(pulse() * 0.55, 0.0)
put(pulse() * 0.45, 4.6)

# ---- the groove: 6.0 - 33.6 s
start, end = 6.0, 33.6
t = start; bar_i = 0
while t < end - 0.01:
    root, notes = CHORDS[(bar_i // 2) % 4]
    if bar_i % 2 == 0:
        put(pad([n + 12 for n in notes], min(BAR * 2, end - t) + 0.4) * 0.22, t)
    full = t > 11.0
    for b in range(4):
        bt = t + b * BEAT
        if bt >= end: break
        if full or b % 2 == 0: put(kick() * (0.42 if full else 0.3), bt)
        if full: put(tick() * 0.05, bt + BEAT / 2, 1.0, 0.35)
        put(bass(root - 12, BEAT * 0.95) * 0.22, bt)
    arp = [notes[0] + 12, notes[1] + 12, notes[2] + 12, notes[0] + 24, notes[2] + 12, notes[1] + 12, notes[2] + 12, notes[1] + 24]
    for e, m in enumerate(arp):
        et = t + e * BEAT / 2
        if et < end and (t > 23.5 or e % 2 == 0):
            put(piano(m, 0.7, 0.8) * 0.085, et, 1.0, -0.25 if e % 2 else 0.25)
    t += BAR; bar_i += 1

# the link beams, the entries, the levels, the chain reaction
for i, m in enumerate([79, 83, 86]): put(bell(m) * 0.07, 8.4 + i * 0.35, 1.0, -0.3 + i * 0.3)
for i, m in enumerate([76, 79, 84]): put(bell(m) * 0.08, 14.4 + i * 1.2)
for i, m in enumerate([72, 76, 79]): put(bell(m) * 0.08, 18.6 + i * 1.0)
for i in range(12): put(bell([72, 76, 79, 84, 88][i % 5]) * 0.035, 23.6 + i * 0.55, 1.0, -0.5 + (i % 5) * 0.25)

# ---- 33.6: the orb and the logo, then the proof, then the end
put(pulse() * 0.7, 33.6)
put(pad([48, 55, 60, 64, 67], 6.0) * 0.42, 33.6)
for m in (60, 64, 67, 72): put(piano(m, 3.0) * 0.14, 33.65)
put(pad([53, 57, 60, 65], 5.6) * 0.3, 39.4)
for i, m in enumerate([72, 77, 81]): put(piano(m, 1.2) * 0.12, 39.4 + i * 0.35)
put(pulse() * 0.6, 45.2)
put(pad([45, 57, 60, 64, 69], 2.9) * 0.42, 45.2)
for i, m in enumerate([69, 72, 76, 81]): put(piano(m, 2.6) * 0.14, 45.3 + i * 0.16, 1.0, -0.3 + i * 0.2)

# ---- master: gentle fades, soft limiter -----------------------------------------------------------
fade = np.ones(N)
fo = int(1.6 * SR)
fade[-fo:] = np.linspace(1, 0, fo)
L *= fade
R *= fade
peak = max(np.abs(L).max(), np.abs(R).max())
L, R = L / peak, R / peak
L = np.tanh(L * 1.4) / np.tanh(1.4) * 0.9
R = np.tanh(R * 1.4) / np.tanh(1.4) * 0.9
pcm = (np.stack([L, R], axis=1) * 32767).astype(np.int16)
with wave.open("/var/tmp/video/sound3.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("sound3.wav", DUR, "s")
