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
DUR = 72.0
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

# ---- hook: six cuts, a pulse and a rising stab on each ------------------------------
stabs = [64, 67, 71]
for i in range(3):
    at = i * 1.1
    put(pulse() * 0.55, at)
    for m in (stabs[i] - 12, stabs[i] - 5, stabs[i]):
        put(piano(m, 0.6) * 0.16, at, 1.0, -0.2 + i * 0.08)
# the wall: a held minor chord
put(pad([45, 57, 60, 64], 1.6) * 0.32, 3.3)
put(pulse() * 0.6, 3.3)

# ---- breath: "Ads can't fill it" / "Your customers can" -------------------------------------
put(pad([45, 52, 57, 60], 2.0) * 0.28, 4.6)
put(piano(69, 1.6) * 0.18, 4.7)
put(pulse() * 0.5, 6.3)
put(pad([53, 57, 60, 65], 2.4) * 0.32, 6.3)
for i, m in enumerate([72, 76, 79]):
    put(piano(m, 1.5) * 0.15, 6.3 + i * 0.12, 1.0, -0.2 + i * 0.2)

# ---- logo: a full C chord, the groove begins ---------------------------------------------
put(pulse() * 0.7, 8.2)
put(pad([48, 55, 60, 64, 67], 4.8) * 0.4, 8.2)
for m in (60, 64, 67, 72):
    put(piano(m, 3.0) * 0.14, 8.25)

# ---- the story, 12.8 - 66.6 s: 4 chords, two bars each ---------------------------------------
start = 12.8
end = 66.6
t = start
bar_i = 0
while t < end - 0.01:
    root, notes = CHORDS[(bar_i // 2) % 4]
    length = min(BAR, end - t)
    if bar_i % 2 == 0:
        put(pad([n + 12 for n in notes], min(BAR * 2, end - t) + 0.4) * 0.22, t)
    for b in range(4):
        bt = t + b * BEAT
        if bt >= end:
            break
        put(kick() * 0.42, bt)
        put(tick() * 0.05, bt + BEAT / 2, 1.0, 0.35)
        put(bass(root - 12, BEAT * 0.95) * 0.22, bt)
    # piano arpeggio in eighths: root, 3rd, 5th, octave, 5th, 3rd...
    arp = [notes[0] + 12, notes[1] + 12, notes[2] + 12, notes[0] + 24, notes[2] + 12, notes[1] + 12, notes[2] + 12, notes[1] + 24]
    for e, m in enumerate(arp):
        et = t + e * BEAT / 2
        if et < end:
            put(piano(m, 0.7, 0.8) * 0.085, et, 1.0, -0.25 if e % 2 else 0.25)
    t += BAR
    bar_i += 1

# bells on the numbered moments
for at, m in [(13.6, 76), (16.4, 79), (16.7, 84), (21.0, 76), (22.95, 88), (28.8, 76), (32.0, 79), (32.1, 84), (32.2, 88),
              (35.8, 76), (36.8, 84), (37.25, 86), (37.7, 88), (42.0, 76), (44.4, 72), (44.95, 76), (45.5, 79), (46.05, 84),
              (48.6, 76), (54.8, 76), (56.6, 79), (56.85, 81), (57.1, 84), (57.35, 86), (57.6, 88), (57.85, 91), (60.8, 76), (64.2, 88)]:
    put(bell(m) * 0.06, at, 1.0, 0.15)

# ---- outro ------------------------------------------------------------------------------------
put(pulse() * 0.6, 66.6)
put(pad([45, 57, 60, 64, 69], 5.4) * 0.42, 66.6)
for i, m in enumerate([69, 72, 76, 81]):
    put(piano(m, 4.0) * 0.14, 66.7 + i * 0.16, 1.0, -0.3 + i * 0.2)

# ---- master: gentle fades, soft limiter -----------------------------------------------------------
fade = np.ones(N)
fo = int(3.0 * SR)
fade[-fo:] = np.linspace(1, 0, fo)
L *= fade
R *= fade
peak = max(np.abs(L).max(), np.abs(R).max())
L, R = L / peak, R / peak
L = np.tanh(L * 1.4) / np.tanh(1.4) * 0.9
R = np.tanh(R * 1.4) / np.tanh(1.4) * 0.9
pcm = (np.stack([L, R], axis=1) * 32767).astype(np.int16)
with wave.open("/var/tmp/video/sound2.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("sound2.wav", DUR, "s")
