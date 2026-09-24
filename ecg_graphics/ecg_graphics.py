"""ECG 판독 연습실 그래픽의 Python(matplotlib) 이식판.

원본 HTML(canvas/SVG)에서 그리던 세 가지 그래픽을 그대로 재현합니다.

1. 리듬 strip   : 25 mm/s, 10 mm/mV, Lead II 10초 합성 파형 (+캘리퍼)
2. 원리(mechanism): 전도계 도식, hexaxial 벡터 루프와 lead 투영, lead 파형
                    (특정 시점의 정지 화면 또는 GIF/MP4 애니메이션)
3. 전기축(axis)  : Lead I, aVF net 진폭으로 hexaxial 위에 QRS axis 표시

사용 예
    python ecg_graphics.py strip af -o af.png
    python ecg_graphics.py gallery -o gallery.png
    python ecg_graphics.py mech lbbb --t 0.29 -o lbbb.png
    python ecg_graphics.py mech normal --gif normal.gif --speed 0.2
    python ecg_graphics.py axis 6 8 -o axis.png
    python ecg_graphics.py qtc 400 75
    python ecg_graphics.py rate 20 --mode small
"""
from __future__ import annotations

import argparse
import logging
import math
import os
import re
import textwrap
import urllib.request

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.collections import LineCollection  # noqa: E402
from matplotlib.colors import to_rgb  # noqa: E402
from matplotlib.patches import Ellipse, PathPatch, Polygon, Wedge, Circle  # noqa: E402
from matplotlib.path import Path  # noqa: E402
from matplotlib.transforms import Affine2D  # noqa: E402

# --------------------------------------------------------------------------
# 테마 / 폰트
# --------------------------------------------------------------------------
THEMES = {
    "light": dict(
        bg="#F8F8F6", surface="#FFFFFF", ink="#1C2328", muted="#5A656D", line="#E2E0DB",
        accent="#0E6B73", accent_soft="#E2F0F1", good="#1F7A4A", bad="#B3261E",
        paper="#FFF6F4", gminor="#F6D2CD", gmajor="#E39A92", trace="#1B1F2A", caliper="#0E6B73",
        tissue="#F3E9E6", tissue_edge="#C7AFAA", depol="#DD4B3E", path="#B7861C", vec="#0E6B73",
    ),
    "dark": dict(
        bg="#101417", surface="#171C20", ink="#E5E9EB", muted="#9AA5AC", line="#2A3137",
        accent="#5BC0C8", accent_soft="#16383B", good="#6FD39A", bad="#F2877F",
        paper="#1C1517", gminor="#3A2528", gmajor="#6A343B", trace="#FFE8E3", caliper="#5BC0C8",
        tissue="#2A2226", tissue_edge="#5A4546", depol="#FF7A6B", path="#E8BC52", vec="#5BC0C8",
    ),
}


PX = 0.75  # CSS 1px = 0.75pt. 원본의 px 치수를 그대로 옮기기 위한 환산값
FONT_DIR = os.path.join(os.path.expanduser("~"), ".cache", "ecg_graphics", "fonts")
PLEX_URLS = {  # 원본 페이지가 쓰는 IBM Plex Sans KR (SIL OFL)
    "Regular": "https://fonts.gstatic.com/s/ibmplexsanskr/v11/vEFK2-VJISZe3O_rc3ZVYh4aTwNO8tI.ttf",
    "SemiBold": "https://fonts.gstatic.com/s/ibmplexsanskr/v11/vEFN2-VJISZe3O_rc3ZVYh4aTwNOygqbf7Y.ttf",
    "Bold": "https://fonts.gstatic.com/s/ibmplexsanskr/v11/vEFN2-VJISZe3O_rc3ZVYh4aTwNOym6af7Y.ttf",
}


def _ensure_plex() -> None:
    """IBM Plex Sans KR이 없으면 캐시 폴더에 받아 등록한다. 실패하면 조용히 넘어간다."""
    if os.environ.get("ECG_NO_FONT_DOWNLOAD"):
        return
    os.makedirs(FONT_DIR, exist_ok=True)
    for w, url in PLEX_URLS.items():
        f = os.path.join(FONT_DIR, f"IBMPlexSansKR-{w}.ttf")
        if not os.path.exists(f):
            try:
                with urllib.request.urlopen(url, timeout=10) as r, open(f + ".part", "wb") as o:
                    o.write(r.read())
                os.replace(f + ".part", f)
            except Exception:
                return
        font_manager.fontManager.addfont(f)


def _setup_fonts() -> None:
    logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
    have = {f.name for f in font_manager.fontManager.ttflist}
    if "IBM Plex Sans KR" not in have:
        _ensure_plex()
        have = {f.name for f in font_manager.fontManager.ttflist}
    wanted = ["IBM Plex Sans KR", "Malgun Gothic", "AppleGothic", "Apple SD Gothic Neo",
              "NanumGothic", "Noto Sans CJK KR", "Noto Sans KR", "WenQuanYi Zen Hei"]
    plt.rcParams["font.family"] = [f for f in wanted if f in have] + ["DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["savefig.dpi"] = 192


_setup_fonts()

# --------------------------------------------------------------------------
# 파형 수학
# --------------------------------------------------------------------------
TAU = math.tau
DUR = 10.0  # strip 길이 (초)


def g(t, c, s, a):
    x = (t - c) / s
    return a * np.exp(-0.5 * x * x)


def ag(t, c, sl, sr, a):
    """좌우 폭이 다른 비대칭 가우시안."""
    x = (t - c) / np.where(t < c, sl, sr)
    return a * np.exp(-0.5 * x * x)


def sig(x):
    with np.errstate(over="ignore"):
        return 1.0 / (1.0 + np.exp(-x))


def clamp(v, a, b):
    return np.minimum(b, np.maximum(a, v))


BASE_M = dict(Q=-.08, R=1.1, S=-.25, qrs=.09, rw=.12, T=.32, tl=.06, tr=.04, qtc=.40, st=0, delta=0)
PVC_M = dict(Q=0, R=1.35, S=-.3, qrs=.16, rw=.18, T=-.45, tl=.07, tr=.05)
VT_M = dict(Q=0, R=1.25, S=-.35, qrs=.16, rw=.19, T=-.5, tl=.06, tr=.05, qt=.28)


def M(o=None):
    return {**BASE_M, **(o or {})}


def beat(t, q):
    m, d, t0 = q["m"], q["m"]["qrs"], q["t"]
    v = g(t, t0 + .15 * d, .07 * d, m["Q"]) + g(t, t0 + .45 * d, m["rw"] * d, m["R"]) + g(t, t0 + .78 * d, .1 * d, m["S"])
    if m["delta"]:
        v = v + g(t, t0 + .28 * d, .15 * d, m["delta"])
    qt = m.get("qt") or m["qtc"] * math.sqrt(min(max(q["rr"], .3), 2))
    tp = t0 + qt - .1
    v = v + ag(t, tp, m["tl"], m["tr"], m["T"])
    if m["st"]:
        v = v + m["st"] * sig((t - (t0 + d)) / .006) * sig((tp + .02 - t) / .025)
    return v


def volt(d, t):
    """strip 데이터 d의 시각 t(배열)에서의 전압(mV)."""
    t = np.asarray(t, dtype=float)
    v = d["w"](t) + (d["base"](t) if d.get("base") else 0)
    for p in d["P"]:
        dt = t - p["t"]
        v = v + np.where((dt > -.1) & (dt < .2), g(t, p["t"] + .05, .021, p["amp"]), 0)
    for q in d["Q"]:
        dt = t - q["t"]
        v = v + np.where((dt > -.2) & (dt < .8), beat(t, q), 0)
    return v


class Gen:
    """리듬 생성기에 쓰는 난수 도우미 (JS의 rnd/pick)."""

    def __init__(self, seed=None):
        self.r = np.random.default_rng(seed)

    def rnd(self, a, b):
        return a + self.r.random() * (b - a)

    def pick(self, a):
        return a[int(self.r.integers(len(a)))]

    def chance(self, p):
        return self.r.random() < p


def finalize(s, R):
    a, b, amp = R.rnd(0, TAU), R.rnd(0, TAU), R.rnd(.015, .035)
    s["w"] = lambda t: amp * np.sin(TAU * .22 * t + a) + .008 * np.sin(TAU * .9 * t + b)
    s.setdefault("P", [])
    s.setdefault("Q", [])
    return s


def sinus(R, rate, pr=.16, morph=None, pAmp=.15, jitter=.02, start=None):
    P, Q, rr0 = [], [], 60 / rate
    t = R.rnd(.15, .5) if start is None else start
    while t < DUR:
        rr = rr0 * (1 + R.rnd(-jitter, jitter))
        P.append(dict(t=t, amp=pAmp))
        if t + pr < DUR:
            Q.append(dict(t=t + pr, m=M(morph), rr=rr))
        t += rr
    return finalize(dict(P=P, Q=Q), R)


# --------------------------------------------------------------------------
# 리듬 도감
# --------------------------------------------------------------------------
def _af(R):
    Q, t = [], R.rnd(.2, .5)
    ph = [R.rnd(0, TAU) for _ in range(3)]
    while t < DUR:
        rr = R.rnd(.42, 1.05)
        Q.append(dict(t=t, m=M(dict(T=.24)), rr=rr))
        t += rr
    base = lambda t: (.045 * np.sin(TAU * 6.1 * t + ph[0]) + .03 * np.sin(TAU * 7.3 * t + ph[1])
                      + .025 * np.sin(TAU * 4.9 * t + ph[2]))
    return finalize(dict(Q=Q, base=base), R)


def _flutter(R):
    ratio, fr, off, Q = R.pick([2, 4, 4, 4]), 5, R.rnd(0, .2), []

    def saw(t):
        f = np.mod((t - off) * fr, 1)
        return np.where(f < .8, .14 - .32 * (f / .8), -.18 + .32 * ((f - .8) / .2))

    k = 1
    while True:
        t = off + k / fr + .12
        if t > DUR:
            break
        Q.append(dict(t=t, m=M(dict(T=.16)), rr=ratio / fr))
        k += ratio
    return finalize(dict(Q=Q, base=saw), R)


def _svt(R):
    rr, Q, t = 60 / R.rnd(165, 210), [], R.rnd(.1, .3)
    while t < DUR:
        Q.append(dict(t=t, m=M(dict(T=.2, R=1)), rr=rr))
        t += rr
    return finalize(dict(Q=Q), R)


def _junc(R):
    rr, retro, P, Q = 60 / R.rnd(42, 58), R.chance(.5), [], []
    t = R.rnd(.2, .6)
    while t < DUR:
        Q.append(dict(t=t, m=M(), rr=rr))
        if retro:
            P.append(dict(t=t + .07, amp=-.1))
        t += rr
    return finalize(dict(P=P, Q=Q), R)


def _mob1(R):
    pp, N = 60 / R.rnd(72, 88), R.pick([3, 4])
    prs = [.16, .28] if N == 3 else [.16, .25, .31]
    P, Q, t, i, last = [], [], R.rnd(.15, .4), 0, None
    while t < DUR:
        P.append(dict(t=t, amp=.15))
        k = i % N
        if k < N - 1:
            q = t + prs[k]
            if q < DUR:
                Q.append(dict(t=q, m=M(), rr=q - last if last is not None else pp))
                last = q
        t += pp
        i += 1
    return finalize(dict(P=P, Q=Q), R)


def _mob2(R):
    pp, N = 60 / R.rnd(75, 90), R.pick([3, 4])
    P, Q, t, i, last = [], [], R.rnd(.15, .4), 0, None
    while t < DUR:
        P.append(dict(t=t, amp=.15))
        if i % N != N - 1:
            q = t + .18
            if q < DUR:
                Q.append(dict(t=q, m=M(dict(qrs=.13, rw=.15, R=.95, S=-.35)),
                              rr=q - last if last is not None else pp))
                last = q
        t += pp
        i += 1
    return finalize(dict(P=P, Q=Q), R)


def _chb(R):
    P, Q, pp, rr = [], [], 60 / R.rnd(72, 92), 60 / R.rnd(32, 42)
    t = R.rnd(0, .5)
    while t < DUR:
        P.append(dict(t=t, amp=.15))
        t += pp
    t = R.rnd(.3, 1.2)
    while t < DUR:
        Q.append(dict(t=t, m=M(dict(Q=0, R=1.15, S=-.3, qrs=.15, rw=.18, T=-.35, tl=.07, tr=.05)), rr=rr))
        t += rr
    return finalize(dict(P=P, Q=Q), R)


def _pvc(R):
    rr, every = 60 / R.rnd(66, 82), R.pick([2, 3])
    P, Q, t, i = [], [], R.rnd(.15, .4), 0
    while t < DUR:
        if i % every == every - 1 and Q:
            qt = Q[-1]["t"] + rr * .58
            if qt < DUR:
                Q.append(dict(t=qt, m=M(PVC_M), rr=rr * .58))
        else:
            P.append(dict(t=t, amp=.15))
            if t + .16 < DUR:
                Q.append(dict(t=t + .16, m=M(), rr=rr))
        t += rr
        i += 1
    return finalize(dict(P=P, Q=Q), R)


def _vt(R):
    rr, Q, t = 60 / R.rnd(150, 200), [], R.rnd(.1, .3)
    while t < DUR:
        Q.append(dict(t=t, m=M(VT_M), rr=rr))
        t += rr
    return finalize(dict(Q=Q), R)


def _vf(R):
    a, b, c, e = R.rnd(0, TAU), R.rnd(0, TAU), R.rnd(0, TAU), R.rnd(.2, .4)
    base = lambda t: (.45 + .3 * np.sin(TAU * e * t)) * (
        .6 * np.sin(TAU * 5.1 * t + a) + .4 * np.sin(TAU * 6.7 * t + b) + .3 * np.sin(TAU * 3.8 * t + c))
    return finalize(dict(base=base), R)


GROUPS = {"sinus": "동성 리듬", "svt": "심방성·접합부", "block": "전도 장애", "vent": "심실성", "st": "ST–T·전해질"}

# id: (group, English, 한글, 생성기, rate 설명)
RHYTHMS = {
    "nsr": ("sinus", "Normal sinus rhythm", "정상 동성 리듬",
            lambda R: sinus(R, R.rnd(62, 95)), "60–100 bpm, 규칙적"),
    "brady": ("sinus", "Sinus bradycardia", "동성 서맥",
              lambda R: sinus(R, R.rnd(38, 54)), "< 60 bpm, 규칙적"),
    "tachy": ("sinus", "Sinus tachycardia", "동성 빈맥",
              lambda R: sinus(R, R.rnd(108, 140), morph=dict(T=.26)), "> 100 bpm, 규칙적"),
    "af": ("svt", "Atrial fibrillation", "심방세동", _af, "심실 rate 다양"),
    "flutter": ("svt", "Atrial flutter", "심방조동", _flutter, "심방 ~300/min, 심실은 전도비에 따라"),
    "svt": ("svt", "Paroxysmal SVT (AVNRT)", "발작성 상심실성 빈맥", _svt, "150–250 bpm, 매우 규칙적"),
    "junc": ("svt", "Junctional rhythm", "접합부 리듬", _junc, "40–60 bpm"),
    "avb1": ("block", "First-degree AV block", "1도 방실 차단",
             lambda R: sinus(R, R.rnd(58, 80), pr=R.rnd(.28, .36)), "기저 리듬에 따름"),
    "mob1": ("block", "Mobitz I (Wenckebach)", "2도 방실 차단 1형", _mob1, "심실 rate 약간 느림"),
    "mob2": ("block", "Mobitz II", "2도 방실 차단 2형", _mob2, "심실 rate는 전도비에 따라 느림"),
    "chb": ("block", "Third-degree (complete) AV block", "3도 (완전) 방실 차단", _chb,
            "심방 60–100, 심실 escape 20–40"),
    "wpw": ("block", "Wolff–Parkinson–White pattern", "WPW 패턴 (조기 흥분)",
            lambda R: sinus(R, R.rnd(65, 85), pr=.09, morph=dict(Q=0, qrs=.12, delta=.35, R=1.0)),
            "기저 리듬에 따름"),
    "pvc": ("vent", "Premature ventricular complexes", "심실 조기 수축 (PVC)", _pvc, "기저 리듬에 따름"),
    "vt": ("vent", "Monomorphic ventricular tachycardia", "단형성 심실 빈맥", _vt, "100–250 bpm"),
    "vf": ("vent", "Ventricular fibrillation", "심실세동", _vf, "측정 불가"),
    "stemi": ("st", "ST-elevation (STEMI pattern)", "ST 분절 상승",
              lambda R: sinus(R, R.rnd(70, 95), morph=dict(R=.85, Q=-.14, S=-.04, st=.3, T=.55, tl=.07, tr=.05)),
              "기저 리듬에 따름"),
    "hyperk": ("st", "Hyperkalemia", "고칼륨혈증",
               lambda R: sinus(R, R.rnd(60, 80), pr=.21, pAmp=.06, morph=dict(qrs=.11, R=.9, T=.95, tl=.028, tr=.028)),
               "기저 리듬에 따름"),
    "lqt": ("st", "Prolonged QT interval", "QT 연장",
            lambda R: sinus(R, R.rnd(58, 70), morph=dict(qtc=.56, T=.26, tl=.085, tr=.06)), "기저 리듬에 따름"),
}


def generate(rhythm_id, seed=None):
    return RHYTHMS[rhythm_id][3](Gen(seed))


# --------------------------------------------------------------------------
# 1. 리듬 strip
# --------------------------------------------------------------------------
CAL, H_MM, BASE_MM = 10, 30, 18  # 보정 펄스 폭, strip 높이, 기저선(위에서) mm
W_MM = CAL + DUR * 25


def draw_strip(ax, data, theme="light", calipers=None, label="II", mm_px=5):
    """ax에 mm 좌표계(1 unit = 1 mm)로 ECG 용지와 파형을 그린다.

    mm_px: 1 mm가 차지하는 화면 px (원본 canvas는 5). 선 두께와 글자 크기가 이 비율을 따른다.
    calipers: (t1, t2) 초 단위. 주어지면 캘리퍼와 측정 문구를 반환한다.
    """
    C = THEMES[theme]
    u = mm_px / 5 * PX  # 원본 canvas 1px의 pt 크기
    Y = lambda v: (H_MM - BASE_MM) + np.asarray(v) * 10
    ax.set_facecolor(C["paper"])
    ax.set_xlim(0, W_MM)
    ax.set_ylim(0, H_MM)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_color(C["gmajor"])
        sp.set_linewidth(u)

    minor = [((i, 0), (i, H_MM)) for i in range(int(W_MM) + 1) if i % 5] + \
            [((0, j), (W_MM, j)) for j in range(H_MM + 1) if j % 5]
    major = [((i, 0), (i, H_MM)) for i in range(0, int(W_MM) + 1, 5)] + \
            [((0, j), (W_MM, j)) for j in range(0, H_MM + 1, 5)]
    ax.add_collection(LineCollection(minor, colors=C["gminor"], linewidths=u, zorder=0))
    ax.add_collection(LineCollection(major, colors=C["gmajor"], linewidths=u, zorder=1))
    ax.text(CAL + 1.2, H_MM - 3.2, label, color=C["trace"], fontsize=12 * u, fontweight="semibold", va="baseline")

    # 1 mV 보정 펄스 + 파형
    x = np.arange(CAL, W_MM + 1e-9, .05)
    v = clamp(volt(data, (x - CAL) / 25), -1.15, 1.75)
    xs = np.concatenate([[0, 2, 2, 7, 7], x])
    ys = np.concatenate([Y([0, 0, 1, 1, 0]), Y(v)])
    ax.plot(xs, ys, color=C["trace"], lw=1.6 * u, solid_joinstyle="round", solid_capstyle="round", zorder=3)

    if calipers is None:
        return None
    a, b = sorted(CAL + np.asarray(calipers, dtype=float) * 25)
    cl = dict(color=C["caliper"], lw=1.5 * u, zorder=4)
    for m in (a, b):
        ax.plot([m, m], [0, H_MM], ls=(0, (4 / 1.5, 3 / 1.5)), **cl)
    ax.plot([a, b], [2, 2], **cl)
    ax.plot([a, a, np.nan, b, b], [1.2, 2.8, np.nan, 1.2, 2.8], **cl)
    mm = b - a
    ms = round(mm * 40)
    bpm = round(60000 / ms) if ms > 0 else 0
    return f"간격 {ms} ms, 작은 칸 {mm:.1f}개. 이 간격이 R–R이라면 {bpm} bpm"


def _strip_block(fig, W, H, y, rid, data, theme, calipers, mm_px, margin, meta=True):
    """제목 + strip + 설명 줄을 px 위치 y부터 그리고, 다음 y를 반환."""
    C = THEMES[theme]
    _, en, ko, _, rate = RHYTHMS[rid]
    T = lambda x, yy, s, **kw: fig.text(x / W, 1 - yy / H, s, **kw)
    sw, sh = W_MM * mm_px, H_MM * mm_px
    T(margin, y + 14, en, fontsize=20 * PX, fontweight="bold", color=C["ink"], va="center")
    T(margin + sw, y + 14, ko, fontsize=15.2 * PX, color=C["muted"], va="center", ha="right")
    y += 36
    ax = fig.add_axes([margin / W, 1 - (y + sh) / H, sw / W, sh / H])
    msg = draw_strip(ax, data, theme, calipers, mm_px=mm_px)
    y += sh
    if meta:
        T(margin, y + 14, "Lead II, 25 mm/s, 10 mm/mV, 10초  ·  " + rate, fontsize=12.8 * PX, color=C["muted"], va="center")
        y += 24
    if msg:
        T(margin, y + 12, msg, fontsize=14.7 * PX, color=C["accent"], va="center")
        y += 26
    return y


def plot_strip(rhythm_id="nsr", seed=None, theme="light", calipers=None, mm_px=5):
    """리듬 strip 하나. mm_px=5가 원본 화면 크기 (1 mm = 5 px)."""
    C = THEMES[theme]
    margin = 24
    W = W_MM * mm_px + 2 * margin
    H = 16 + 36 + H_MM * mm_px + 24 + (26 if calipers is not None else 0) + 12
    fig = plt.figure(figsize=(W / 96, H / 96), facecolor=C["bg"])
    _strip_block(fig, W, H, 16, rhythm_id, generate(rhythm_id, seed), theme, calipers, mm_px, margin)
    return fig


def plot_gallery(seed=None, theme="light", ids=None, mm_px=4):
    """리듬 도감 전체(또는 ids)를 세로로 쌓은 Figure."""
    ids = ids or list(RHYTHMS)
    C = THEMES[theme]
    margin, gap = 24, 22
    W = W_MM * mm_px + 2 * margin
    H = 16 + len(ids) * (36 + H_MM * mm_px + 24 + gap)
    fig = plt.figure(figsize=(W / 96, H / 96), facecolor=C["bg"])
    R = np.random.default_rng(seed)
    y = 16
    for rid in ids:
        y = _strip_block(fig, W, H, y, rid, generate(rid, int(R.integers(1 << 31))), theme, None, mm_px, margin) + gap
    return fig


# --------------------------------------------------------------------------
# 2. 원리: 전도계 + 순간 벡터
# --------------------------------------------------------------------------
LEADS = {"I": 0, "II": 60, "III": 120, "aVR": -150, "aVL": -30, "aVF": 90}
V_APEX = [0, 262, 0, 122]


def G(c, s, a, ang, sr=None):
    return dict(type="g", c=c, sl=s, sr=sr or s, a=a, ang=ang)


def PL(s, e, a, ang, edge=.01):
    return dict(type="plat", s=s, e=e, a=a, ang=ang, edge=edge)


def _ph(a, b, k, n, j=None):
    return dict(a=a, b=b, k=k, n=n, j=j)


def normal(d=0.0):
    return dict(
        cyc=.8 + d,
        comps=[G(.10, .021, .17, 55), G(.222 + d, .0055, .25, -110), G(.243 + d, .009, 1.25, 55),
               G(.265 + d, .008, .38, -160), G(.47 + d, .06, .34, 45, .04)],
        paths=dict(intern=[.02, .12], bach=[.03, .09], his=[.165 + d, .21 + d], lbb=[.21 + d, .226 + d],
                   rbb=[.21 + d, .229 + d], lpk=[.226 + d, .255 + d], rpk=[.229 + d, .25 + d]),
        av=[.12, .165 + d], sa=True,
        atria=[.03, .12, .2, .08], sep=[.21 + d, .026, .38 + d, .2, "LR"], vent=[.226 + d, .064, .38 + d, .2, V_APEX],
        blocks=[], zones=[], extra={},
        phases=[
            _ph(0, .05, "SA", "SA node 발화"),
            _ph(.05, .15, "P", "P wave: 심방 탈분극", .10),
            _ph(.15, .215 + d, "PR", "PR segment: AV node 지연"),
            _ph(.215 + d, .232 + d, "q", "Septal depolarization"),
            _ph(.232 + d, .256 + d, "R", "R wave: 심실 자유벽", .243 + d),
            _ph(.256 + d, .29 + d, "S", "S wave: 기저부"),
            _ph(.29 + d, .38 + d, "ST", "ST segment: plateau"),
            _ph(.38 + d, .58 + d, "T", "T wave: 심실 재분극", .47 + d),
            _ph(.58 + d, .8 + d, "TP", "TP segment: 전기적 휴지기"),
        ],
    )


def _keep(s, keys):
    return [p for p in s["phases"] if p["k"] in keys]


def _scenarios():
    SC = {}
    s = normal(0)
    s.update(id="normal", name="정상", leads=["I", "II", "aVR"])
    SC["normal"] = s

    s = normal(.14)
    s.update(id="avb1", name="1도 AV block", leads=["II", "I", "aVR"])
    next(p for p in s["phases"] if p["k"] == "PR")["n"] = "PR segment: 연장된 AV node 지연"
    SC["avb1"] = s

    s = normal(0)
    s.update(id="rbbb", name="RBBB", leads=["I", "II", "aVR"], cyc=.85, blocks=["rbb"],
             comps=[G(.10, .021, .17, 55), G(.222, .0055, .25, -110), G(.243, .009, 1.1, 50),
                    G(.30, .024, .55, 175), G(.49, .06, .3, 40, .04)],
             sep=[.21, .026, .42, .2, "LR"], vent=[.226, .13, .42, .2, [250, 0, 70, 0]])
    del s["paths"]["rbb"], s["paths"]["rpk"]
    s["phases"] = _keep(s, ["SA", "P", "PR", "q"]) + [
        _ph(.232, .265, "LV", "LV 정상 활성", .243), _ph(.265, .35, "RV", "RV 지연 활성", .30),
        _ph(.35, .62, "T", "재분극", .49), _ph(.62, .85, "TP", "TP segment")]
    SC["rbbb"] = s

    s = normal(0)
    s.update(id="lbbb", name="LBBB", leads=["I", "aVL", "aVR"], cyc=.9, blocks=["lbb"],
             comps=[G(.10, .021, .17, 55), G(.235, .012, .5, 10), G(.285, .03, 1.15, -15), G(.322, .017, .8, -30),
                    PL(.36, .5, .15, 165, .015), G(.56, .07, .45, 165, .045)],
             sep=[.215, .035, .45, .2, "RL"], vent=[.225, .14, .45, .2, [70, 0, 250, 0]])
    del s["paths"]["lbb"], s["paths"]["lpk"]
    s["phases"] = _keep(s, ["SA", "P", "PR"]) + [
        _ph(.215, .25, "Sep", "중격: 오른쪽에서 왼쪽으로", .235), _ph(.25, .36, "LV", "LV의 느린 활성", .29),
        _ph(.36, .66, "ST–T", "이차성 ST–T 변화", .56), _ph(.66, .9, "TP", "TP segment")]
    SC["lbbb"] = s

    s = normal(0)
    s.update(id="lafb", name="LAFB", leads=["I", "II", "aVF"], blocks=["afasc"],
             comps=[G(.10, .021, .17, 55), G(.224, .007, .35, 120), G(.247, .011, 1.2, -55), G(.47, .06, .3, 10, .04)],
             extra=dict(afasc=["M166 166 Q200 162 228 138", None]), vent=[.224, .066, .38, .2, [150, 262, 250, 128]])
    s["phases"] = _keep(s, ["SA", "P", "PR"]) + [
        _ph(.215, .236, "초기", "초기 벡터: 아래쪽", .224), _ph(.236, .29, "주벡터", "주 벡터: 왼쪽 위", .247)
    ] + _keep(s, ["ST", "T", "TP"])
    SC["lafb"] = s

    s = normal(0)
    s.update(id="wpw", name="WPW", leads=["II", "aVF", "aVL"],
             comps=[G(.10, .021, .17, 55), G(.168, .016, .45, 100, .012), G(.243, .009, 1.05, 60),
                    G(.265, .008, .3, -160), G(.47, .06, .22, 20, .04)],
             extra=dict(kent=["M226 100 L240 140", [.09, .125]]),
             zones=[dict(shape=[230, 152, 20, 18], kind="pre", t=[.125, .2], lbl="조기 흥분", lx=206, ly=186)])
    s["phases"] = _keep(s, ["SA"]) + [
        _ph(.05, .13, "P", "P wave와 Kent 전도", .10), _ph(.13, .215, "δ", "Delta wave: 조기 흥분", .168),
        _ph(.215, .29, "Fusion", "Fusion QRS", .243), _ph(.29, .58, "ST–T", "이차성 재분극 변화", .47),
        _ph(.58, .8, "TP", "위험성")]
    SC["wpw"] = s

    s = normal(0)
    s.update(id="pvc", name="PVC", leads=["I", "II", "aVR"], cyc=.9, sa=False, paths={}, av=None, atria=None,
             comps=[G(.27, .035, 1.1, 165), G(.315, .025, .5, 130), G(.56, .07, .5, -20, .05)],
             sep=[.25, .05, .45, .22, "LR"], vent=[.2, .16, .45, .22, "radial"],
             zones=[dict(shape=[232, 196, 7, 7], kind="focus", t=[.18, .22], lbl="ectopic focus", lx=170, ly=226)])
    s["phases"] = [_ph(0, .18, "휴지", "다음 sinus 박동 이전"), _ph(.18, .21, "Focus", "Ectopic focus 발화", .195),
                   _ph(.21, .36, "QRS", "세포 간 전도: wide QRS", .27), _ph(.36, .66, "T", "Discordant T wave", .56),
                   _ph(.66, .9, "Pause", "Compensatory pause")]
    SC["pvc"] = s

    s = normal(0)
    s.update(id="stemi", name="Inferior STEMI", leads=["II", "III", "aVL"],
             comps=normal(0)["comps"][:4] + [PL(.285, .44, .28, 100, .012), G(.46, .055, .45, 80, .04)],
             zones=[dict(shape=[172, 250, 40, 11], kind="injury", lbl="손상 부위 (inferior wall)", lx=112, ly=282)])
    s["phases"] = _keep(s, ["SA", "P", "PR", "q", "R", "S"]) + [
        _ph(.29, .38, "ST", "Injury current: ST elevation", .34), _ph(.38, .58, "T", "Hyperacute T wave", .46)
    ] + _keep(s, ["TP"])
    SC["stemi"] = s
    return SC


SCENARIOS = _scenarios()


def vec(sc, t):
    """시각 t(스칼라 또는 배열)의 frontal plane 순간 벡터 (x, y). y는 아래쪽이 +."""
    t = np.asarray(t, dtype=float)
    x = np.zeros_like(t)
    y = np.zeros_like(t)
    for k in sc["comps"]:
        if k["type"] == "plat":
            m = k["a"] * sig((t - k["s"]) / k["edge"]) * sig((k["e"] - t) / k["edge"])
        else:
            m = ag(t, k["c"], k["sl"], k["sr"], k["a"])
        r = math.radians(k["ang"])
        x = x + m * math.cos(r)
        y = y + m * math.sin(r)
    return x, y


def proj(v, lead_deg):
    r = math.radians(lead_deg)
    return v[0] * math.cos(r) + v[1] * math.sin(r)


def sm(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def cur_phase(sc, t):
    return next((p for p in sc["phases"] if p["a"] <= t < p["b"]), sc["phases"][-1])


# ---- SVG 경로 도우미 (M, L, Q, Z만 사용) ----
def _svg_tokens(d):
    return re.findall(r"[MLQZ]|-?\d*\.?\d+", d)


def svg_to_mpl(d):
    tok, verts, codes, i, cmd = _svg_tokens(d), [], [], 0, None
    while i < len(tok):
        if tok[i] in "MLQZ":
            cmd = tok[i]
            i += 1
            if cmd == "Z":
                verts.append(verts[0] if verts else (0, 0))
                codes.append(Path.CLOSEPOLY)
                continue
        n = 4 if cmd == "Q" else 2
        nums = [float(x) for x in tok[i:i + n]]
        i += n
        if cmd == "M":
            verts.append(nums)
            codes.append(Path.MOVETO)
            cmd = "L"
        elif cmd == "L":
            verts.append(nums)
            codes.append(Path.LINETO)
        else:
            verts += [nums[:2], nums[2:]]
            codes += [Path.CURVE3, Path.CURVE3]
    return Path(verts, codes)


def svg_polyline(d, n=60):
    """전도로 경로를 촘촘한 점열과 누적 길이로 변환."""
    pts = []
    for seg_verts, code in _iter_segments(svg_to_mpl(d)):
        if code == Path.MOVETO:
            pts.append(seg_verts)
        elif code == Path.LINETO:
            p0 = np.array(pts[-1])
            for u in np.linspace(0, 1, n)[1:]:
                pts.append(tuple(p0 + (np.array(seg_verts) - p0) * u))
        else:  # CURVE3: (ctrl, end)
            p0, c, e = np.array(pts[-1]), np.array(seg_verts[0]), np.array(seg_verts[1])
            for u in np.linspace(0, 1, n)[1:]:
                pts.append(tuple((1 - u) ** 2 * p0 + 2 * (1 - u) * u * c + u * u * e))
    pts = np.array(pts)
    L = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(pts, axis=0).T))])
    return pts, L


def _iter_segments(path):
    v, c, i = path.vertices, path.codes, 0
    while i < len(v):
        if c[i] == Path.CURVE3:
            yield (tuple(v[i]), tuple(v[i + 1])), Path.CURVE3
            i += 2
        else:
            yield tuple(v[i]), c[i]
            i += 1


def _partial(pts, L, frac):
    """경로 앞에서부터 frac 비율만큼의 점열과 끝점."""
    s = L[-1] * frac
    k = np.searchsorted(L, s)
    if k == 0:
        return pts[:1], pts[0]
    u = (s - L[k - 1]) / (L[k] - L[k - 1]) if L[k] > L[k - 1] else 0
    end = pts[k - 1] + (pts[k] - pts[k - 1]) * u
    return np.vstack([pts[:k], end]), end


GEO = dict(intern="M84 66 Q112 100 150 124", bach="M88 62 Q140 44 196 66", his="M150 124 L160 150",
           lbb="M160 150 Q176 190 196 238", rbb="M160 150 Q146 196 124 232",
           lpk="M196 238 Q236 214 236 160", rpk="M124 232 Q80 206 76 156")
RV_D = "M68 142 Q58 205 118 242 Q152 262 186 258 L146 126 L102 126 Q72 126 68 142 Z"
LV_D = "M160 126 L206 126 Q236 128 244 156 Q252 220 214 258 Q206 264 198 252 Z"
SEP_PTS = [(146, 126), (160, 126), (198, 252), (186, 258)]
HEART_BOX = (48, 260, 34, 290)  # viewBox x0, x1, y0, y1


def _ellipse_path(cx, cy, rx, ry):
    return Path.unit_circle().transformed(Affine2D().scale(rx, ry).translate(cx, cy))


def _grad_alpha(u, prog):
    """SVG 그라디언트(setGrad) 재현: 진행도 prog에 따라 u<off1은 불투명, off2 이후 투명."""
    p = prog * 1.1 - .1
    o1, o2 = min(max(p, 0), 1), min(max(p + .1, 0), 1)
    if o2 <= o1:
        return (u <= o1).astype(float)
    return np.clip((o2 - u) / (o2 - o1), 0, 1)


def _linear_u(X, Y, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    return ((X - x1) * dx + (Y - y1) * dy) / (dx * dx + dy * dy)


_HX, _HY = np.meshgrid(np.arange(HEART_BOX[0], HEART_BOX[1], .4), np.arange(HEART_BOX[2], HEART_BOX[3], .4))


def _overlay(ax, C, alpha, clip, z):
    img = np.zeros(alpha.shape + (4,))
    img[..., :3] = to_rgb(C["depol"])
    img[..., 3] = alpha
    im = ax.imshow(img, extent=HEART_BOX, origin="lower", interpolation="bilinear", zorder=z, aspect="auto")
    im.set_clip_path(clip, ax.transData)


def _svg_arrow(ax, x0, y0, x1, y1, color, k, sw=4, z=13):
    """SVG의 marker-end(arrH: viewBox 10, refX 6, markerWidth 3.2) 화살표를 그대로 재현.
    k = 1 SVG 단위당 pt, sw = stroke-width(SVG 단위)."""
    d = np.array([x1 - x0, y1 - y0], dtype=float)
    n = np.hypot(*d)
    if n < 1e-9:
        return
    d /= n
    m = 3.2 * sw  # marker 한 변 길이
    tip = np.array([x1, y1]) + d * m * .4
    base = tip - d * m
    nv = np.array([-d[1], d[0]]) * m / 2
    ax.plot([x0, x1], [y0, y1], color=color, lw=sw * k, solid_capstyle="round", zorder=z)
    ax.add_patch(Polygon([tip, base + nv, base - nv], closed=True, fc=color, ec="none", zorder=z))


def draw_heart(ax, sc, t, C, k=1.0):
    """전도계 도식. SVG viewBox 좌표를 그대로 사용 (y 아래로 증가). k = 1 SVG 단위의 pt 크기."""
    x0, x1, y0, y1 = HEART_BOX
    ax.set_xlim(x0, x1)
    ax.set_ylim(y1, y0)
    ax.set_aspect("equal")
    ax.axis("off")
    rep = lambda w: 1 - sm((t - w[2]) / w[3]) if w else 0
    dep = lambda w: min(max((t - w[0]) / w[1], 0), 1) if w else 0
    tissue = dict(fc=C["tissue"], ec=C["tissue_edge"], lw=1.5 * k)

    # 심방
    atria = Path.make_compound_path(_ellipse_path(100, 92, 42, 36), _ellipse_path(190, 82, 40, 30))
    ax.add_patch(PathPatch(atria, zorder=1, **tissue))
    if sc["atria"]:
        a = _grad_alpha(_linear_u(_HX, _HY, 62, 0, 230, 0), dep(sc["atria"])) * rep(sc["atria"])
        _overlay(ax, C, a, atria, 2)
    # 심실
    rv, lv = svg_to_mpl(RV_D), svg_to_mpl(LV_D)
    ax.add_patch(PathPatch(rv, zorder=3, **tissue))
    ax.add_patch(PathPatch(lv, zorder=3, **tissue))
    vg = sc["vent"][4]
    if vg == "radial":
        u = np.hypot(_HX - 232, _HY - 196) / 190
    else:
        u = _linear_u(_HX, _HY, *vg)
    _overlay(ax, C, _grad_alpha(u, dep(sc["vent"])) * rep(sc["vent"]), Path.make_compound_path(rv, lv), 4)
    # 중격
    sep = Path(SEP_PTS + [SEP_PTS[0]], [Path.MOVETO] + [Path.LINETO] * 3 + [Path.CLOSEPOLY])
    ax.add_patch(PathPatch(sep, zorder=5, **tissue))
    sx = (200, 142) if sc["sep"][4] == "LR" else (140, 200)
    _overlay(ax, C, _grad_alpha(_linear_u(_HX, _HY, sx[0], 0, sx[1], 0), dep(sc["sep"])) * rep(sc["sep"]), sep, 6)

    # 특수 영역 (조기 흥분, ectopic focus, 손상 부위)
    for z in sc["zones"]:
        cx, cy, rx, ry = z["shape"]
        if z["kind"] == "injury":
            plt.rcParams["hatch.linewidth"] = 2 * k * .5
            ax.add_patch(Ellipse((cx, cy), 2 * rx, 2 * ry, fc=(*to_rgb(C["bad"]), .15), ec=C["bad"],
                                 hatch="///", lw=1.5 * k, zorder=7))
        elif z["kind"] == "pre":
            t0, t1 = z["t"]
            op = (.15 + .85 * sm((t - t0) / (t1 - t0))) * (rep(sc["vent"]) if t > t0 else .15) + (.15 if t <= t0 else 0)
            ax.add_patch(Ellipse((cx, cy), 2 * rx, 2 * ry, fc=(*to_rgb(C["depol"]), min(op, 1)), ec=C["bad"],
                                 lw=1.5 * k, ls=(0, (2, 4 / 3)), zorder=7))
        else:
            t0, t1 = z["t"]
            r = 7 + 6 * math.sin((t - t0) / (t1 - t0) * math.pi) if t0 < t < t1 else 7
            ax.add_patch(Ellipse((cx, cy), 2 * r, 2 * r, fc=C["bad"], ec=C["ink"], lw=2 * k, zorder=7))
        ax.text(z["lx"], z["ly"], z["lbl"], color=C["bad"], fontsize=12 * k, fontweight="semibold", zorder=12)

    # 전도로
    fade = 1 - sm((t - .3 - (sc["cyc"] - .8)) / .06)
    allp = {kk: [d, sc["paths"].get(kk)] for kk, d in GEO.items()}
    allp.update(sc["extra"])
    for key, (d, win) in allp.items():
        pts, L = svg_polyline(d)
        ax.plot(pts[:, 0], pts[:, 1], color=C["path"], lw=2.2 * k, alpha=.35, solid_capstyle="round", zorder=8)
        pr, show_dot = None, False
        if key in sc["blocks"]:
            src = sc["paths"].get("lbb") if key == "afasc" else sc["paths"].get("his")
            q = _partial(pts, L, .3)[1]
            ax.plot([q[0] - 7, q[0] + 7, np.nan, q[0] + 7, q[0] - 7], [q[1] - 7, q[1] + 7, np.nan, q[1] - 7, q[1] + 7],
                    color=C["bad"], lw=4 * k, solid_capstyle="round", zorder=10)
            if src:
                st = src[1]
                pr = min(max((t - st) / .03, 0), .3)
                show_dot = st < t < st + .03
        elif win:
            pr = min(max((t - win[0]) / (win[1] - win[0]), 0), 1)
            show_dot = 0 < pr < 1 and t < win[1]
        if pr:
            seg, end = _partial(pts, L, pr)
            ax.plot(seg[:, 0], seg[:, 1], color=C["path"], lw=3.4 * k, alpha=fade, solid_capstyle="round",
                    solid_joinstyle="round", zorder=9)
            if show_dot:
                ax.add_patch(Circle(end, 5, fc=C["depol"], ec=C["surface"], lw=1.5 * k, zorder=11))

    sa_r = 6 + 5 * math.sin(t / .035 * math.pi) if sc["sa"] and t < .035 else 6
    ax.add_patch(Circle((84, 64), sa_r, fc=C["path"], ec="none", zorder=10))
    ax.add_patch(Circle((150, 124), 6, fc=C["path"], ec="none", zorder=10))
    if sc["av"] and sc["av"][0] <= t < sc["av"][1]:
        ax.add_patch(Circle((150, 124), 5 + 2 * math.sin((t - sc["av"][0]) * 140), fc=C["depol"],
                            ec=C["surface"], lw=1.5 * k, zorder=11))

    vx, vy = vec(sc, t)
    if math.hypot(vx, vy) > .03:
        _svg_arrow(ax, 165, 182, 165 + vx * 72, 182 + vy * 72, C["vec"], k)
    for txt, x, y, strong in [("SA", 58, 54, 1), ("AV", 118, 120, 1), ("RA", 84, 100, 0), ("LA", 196, 88, 0),
                              ("RV", 92, 190, 0), ("LV", 214, 200, 0), ("His", 166, 146, 0)]:
        ax.text(x, y, txt, fontsize=14 * k, color=C["ink"] if strong else C["muted"],
                fontweight="semibold" if strong else "normal", zorder=12)


def draw_vector_panel(ax, sc, t, sel, C, k=1.0, S=72, CC=120):
    """Hexaxial 위의 벡터 루프, 현재 벡터, 선택 lead 투영. k = 1 SVG 단위의 pt 크기."""
    ax.set_xlim(0, 240)
    ax.set_ylim(240, 0)
    ax.set_aspect("equal")
    ax.axis("off")
    for n, d in LEADS.items():
        r, on = math.radians(d), n in sel
        c, s = math.cos(r), math.sin(r)
        ax.plot([CC - 92 * c, CC + 92 * c], [CC - 92 * s, CC + 92 * s], color=C["accent"] if on else C["line"],
                lw=(1.6 if on else 1) * k, alpha=.8 if on else 1, zorder=1)
        ax.text(CC + 106 * c, CC + 106 * s, n, ha="center", va="center", fontsize=12 * k,
                color=C["ink"] if on else C["muted"], fontweight="semibold" if on else "normal")
        if on:
            ax.text(CC + 80 * c, CC + 80 * s - 6, "+", ha="center", va="baseline", fontsize=10 * k, color=C["muted"])
    tt = np.arange(0, sc["cyc"] + 1e-9, .001)
    lx, ly = vec(sc, tt)
    ax.plot(CC + lx * S, CC + ly * S, color=C["muted"], lw=1.2 * k, alpha=.55, zorder=2, solid_joinstyle="round")
    v = vec(sc, t)
    if math.hypot(*v) > .01:
        tx, ty = CC + v[0] * S, CC + v[1] * S
        for n in sel:
            L = math.radians(LEADS[n])
            pv = proj(v, LEADS[n])
            px, py = CC + pv * S * math.cos(L), CC + pv * S * math.sin(L)
            ax.plot([tx, px], [ty, py], color=C["muted"], lw=k, ls=(0, (3, 3)), zorder=3)
            ax.add_patch(Circle((px, py), 3.5, fc=C["accent"], ec="none", zorder=4))
        _svg_arrow(ax, CC, CC, tx, ty, C["vec"], k, z=5)
    ax.add_patch(Circle((CC, CC), 3, fc=C["ink"], ec="none", zorder=6))


def draw_lead_traces(ax, sc, t, sel, C, W=744, RH=70, PAD=34):
    """선택 lead의 한 심주기 파형 (원본 canvas와 같은 px 좌표). 현재 시점까지 진하게, 이후는 흐리게."""
    H = RH * len(sel)
    X = lambda tt: PAD + np.asarray(tt) / sc["cyc"] * (W - PAD - 6)
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.set_facecolor(C["paper"])
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_color(C["gmajor"])
        s.set_linewidth(PX)
    nk = round(sc["cyc"] / .04)
    for kk in range(nk + 1):
        ax.axvline(round(float(X(kk * .04))) + .5, color=C["gmajor"] if kk % 5 == 0 else C["gminor"], lw=PX, zorder=0)
    p = cur_phase(sc, t)
    ax.axvspan(X(p["a"]), X(p["b"]), color=C["accent_soft"], alpha=.6, lw=0, zorder=1)
    tt = np.arange(0, sc["cyc"] + 1e-9, .001)
    vx, vy = vec(sc, tt)
    for i, n in enumerate(sel):
        y0, scl, L = i * RH + RH * .56, 24, LEADS[n]
        ax.plot([PAD, W], [round(y0) + .5] * 2, color=C["gmajor"], alpha=.5, lw=PX, zorder=1)
        ax.text(6, y0 + 4, n, color=C["ink"], fontsize=12 * PX, fontweight="semibold", va="baseline")
        y = y0 - clamp(proj((vx, vy), L), -1.25, 1.4) * scl
        rest = tt >= t - .001
        ax.plot(X(tt[rest]), y[rest], color=C["trace"], lw=1.8 * PX, alpha=.22, zorder=2, solid_joinstyle="round")
        done = tt <= t + 1e-9
        ax.plot(X(tt[done]), y[done], color=C["trace"], lw=1.8 * PX, zorder=3, solid_joinstyle="round")
        yc = y0 - float(clamp(proj(vec(sc, t), L), -1.25, 1.4)) * scl
        ax.add_patch(Circle((float(X(t)), yc), 3.5, fc=C["accent"], ec="none", zorder=5))
    ax.axvline(X(t), color=C["accent"], lw=1.5 * PX, zorder=4)


def readout(sc, t, sel):
    v = vec(sc, t)
    mag = math.hypot(*v)
    ms = round(t * 1000)
    if mag <= .03:
        return f"t = {ms} ms, 순간 벡터 ≈ 0 (기저선)"
    ang = round(math.degrees(math.atan2(v[1], v[0])))
    parts = []
    for n in sel:
        p = proj(v, LEADS[n])
        parts.append(f"{n} {'양성' if p > .03 else '음성' if p < -.03 else '≈0'}")
    return f"t = {ms} ms, 벡터 {'+' if ang > 0 else ''}{ang}°, 크기 {mag:.2f} mV. " + ", ".join(parts)


# 원본 페이지 레이아웃(px): 본문 폭 744, mech-grid 1.1fr : 1fr, gap 10
_MW, _GAP, _TOP = 744, 10, 64
_HW = (_MW - _GAP) * 1.1 / 2.1
_VW = _MW - _GAP - _HW
_HH = _HW * 256 / 212


def _mech_layout(n_leads, theme, margin=24):
    C = THEMES[theme]
    trace_y = _TOP + _HH + 40
    H = trace_y + 70 * n_leads + 48
    W = _MW + 2 * margin
    fig = plt.figure(figsize=(W / 96, H / 96), facecolor=C["bg"])
    box = lambda x, y, w, h: fig.add_axes([x / W, 1 - (y + h) / H, w / W, h / H])
    axes = (box(margin, _TOP, _HW, _HH), box(margin + _HW + _GAP, _TOP, _VW, _VW),
            box(margin, trace_y, _MW, 70 * n_leads))
    fig._ecg_px = (W, H, margin, trace_y, n_leads)
    return fig, axes, C


def _render_mech(fig, axes, C, sc, t, sel):
    ah, av, at = axes
    W, H, mg, trace_y, n = fig._ecg_px
    for a in axes:
        a.clear()
    for txt in list(fig.texts):
        txt.remove()
    draw_heart(ah, sc, t, C, _HW / 212 * PX)
    draw_vector_panel(av, sc, t, sel, C, _VW / 240 * PX)
    draw_lead_traces(at, sc, t, sel, C)
    p = cur_phase(sc, t)
    T = lambda x, y, s, **kw: fig.text(x / W, 1 - y / H, s, **kw)
    T(mg, 22, f"{sc['name']}  ·  {p['n']}", fontsize=20 * PX, fontweight="bold", color=C["ink"], va="center")
    cap = dict(fontsize=12.8 * PX, color=C["muted"], ha="center", va="top")
    T(mg + _HW / 2, _TOP + _HH + 4, "전도계와 순간 벡터", **cap)
    T(mg + _HW + _GAP + _VW / 2, _TOP + _VW + 4, "벡터 루프와 lead 투영", **cap)
    T(mg, trace_y + 70 * n + 22, readout(sc, t, sel), fontsize=14 * PX, color=C["muted"], va="center")


def plot_mechanism(scenario="normal", t=None, leads=None, theme="light"):
    """원리 탭의 한 장면. t가 없으면 R파 정점(또는 가장 큰 벡터 시점)."""
    sc = SCENARIOS[scenario]
    sel = leads or sc["leads"]
    if t is None:
        tt = np.arange(0, sc["cyc"], .001)
        t = float(tt[np.argmax(np.hypot(*vec(sc, tt)))])
    fig, axes, C = _mech_layout(len(sel), theme)
    _render_mech(fig, axes, C, sc, t, sel)
    return fig


def animate_mechanism(scenario="normal", out="mech.gif", speed=.2, fps=20, leads=None, theme="light", dpi=120):
    """한 심주기를 speed 배속으로 재생하는 애니메이션을 저장 (gif 또는 mp4)."""
    from matplotlib.animation import FuncAnimation, PillowWriter

    sc = SCENARIOS[scenario]
    sel = leads or sc["leads"]
    n = max(2, round(sc["cyc"] / speed * fps))
    times = np.arange(n) / n * sc["cyc"]
    fig, axes, C = _mech_layout(len(sel), theme)
    anim = FuncAnimation(fig, lambda i: _render_mech(fig, axes, C, sc, times[i], sel), frames=n)
    if out.lower().endswith(".gif"):
        anim.save(out, writer=PillowWriter(fps=fps), dpi=dpi, savefig_kwargs=dict(facecolor=C["bg"]))
    else:  # mp4 등은 ffmpeg 필요
        anim.save(out, fps=fps, dpi=dpi, savefig_kwargs=dict(facecolor=C["bg"]))
    plt.close(fig)
    return out


# --------------------------------------------------------------------------
# 3. 전기축 / 계산기
# --------------------------------------------------------------------------
AXIS_HINT = {
    "정상 축": "−30° ~ +90° 범위입니다.",
    "Left axis deviation": "LAFB, LVH, inferior MI, WPW를 생각합니다.",
    "Right axis deviation": "LPFB, RVH, lateral MI, acute PE, 소아나 마른 체형의 정상 변이를 생각합니다.",
    "Extreme (northwest) axis": "VT, lead reversal, 심한 RVH를 생각합니다.",
}


def qrs_axis(lead_i, avf):
    """(각도, 분류) 반환. 둘 다 0이면 (None, 'Indeterminate')."""
    if lead_i == 0 and avf == 0:
        return None, "Indeterminate"
    th = math.degrees(math.atan2(avf, lead_i))
    cls = ("정상 축" if -30 <= th <= 90 else "Left axis deviation" if -90 <= th < -30
           else "Right axis deviation" if 90 < th <= 180 else "Extreme (northwest) axis")
    return th, cls


def plot_axis(lead_i=6, avf=8, theme="light"):
    """전기축 hexaxial (원본 SVG 220px 크기) + 결과 문구."""
    C = THEMES[theme]
    W, H, sv = 640, 268, 220
    k = sv / 240 * PX
    fig = plt.figure(figsize=(W / 96, H / 96), facecolor=C["bg"])
    ax = fig.add_axes([24 / W, 1 - (24 + sv) / H, sv / W, sv / H])
    ax.set_xlim(0, 240)
    ax.set_ylim(240, 0)
    ax.set_aspect("equal")
    ax.axis("off")
    # 정상 범위 (−30° ~ +90°). y가 아래로 증가하므로 각도 그대로 사용
    ax.add_patch(Wedge((120, 120), 88, -30, 90, fc=C["accent_soft"], ec="none"))
    ax.add_patch(Circle((120, 120), 88, fc="none", ec=C["line"], lw=k))
    pt = lambda deg, r: (120 + r * math.cos(math.radians(deg)), 120 + r * math.sin(math.radians(deg)))
    for n, d in [("I", 0), ("II", 60), ("III", 120), ("aVF", 90), ("aVL", -30), ("aVR", -150)]:
        (a, b), (c, e), (lx, ly) = pt(d, 88), pt(d + 180, 88), pt(d, 104)
        ax.plot([c, a], [e, b], color=C["line"], ls=(0, (3, 3)), lw=k)
        ax.text(lx, ly, f"{n} {'+' if d > 0 else ''}{d}°", fontsize=11 * k, color=C["muted"], ha="center", va="center")
    th, cls = qrs_axis(lead_i, avf)
    T = lambda x, y, s_, **kw: fig.text(x / W, 1 - y / H, s_, **kw)
    x0 = 24 + sv + 28
    T(x0, 44, f"Lead I = {lead_i:g} mm, aVF = {avf:g} mm", fontsize=13.6 * PX, color=C["muted"], va="center")
    if th is None:
        T(x0, 100, "두 lead 모두 isoelectric이면\n축을 정할 수 없습니다\n(indeterminate axis).", fontsize=16.8 * PX,
          color=C["ink"], va="top", linespacing=1.6)
    else:
        ax_, ay_ = pt(th, 80)
        ax.plot([120, ax_], [120, ay_], color=C["accent"], lw=3 * k, solid_capstyle="round")
        ax.add_patch(Circle((ax_, ay_), 5, fc=C["accent"], ec="none"))
        T(x0, 96, f"{'+' if th > 0 else ''}{round(th)}°", fontsize=25.6 * PX * 1.4, fontweight="bold",
          color=C["accent"], va="center")
        T(x0, 138, f"{cls}.", fontsize=16.8 * PX, fontweight="semibold", color=C["ink"], va="top")
        T(x0, 166, textwrap.fill(AXIS_HINT[cls], 26), fontsize=15 * PX, color=C["ink"], va="top", linespacing=1.6)
    ax.add_patch(Circle((120, 120), 3, fc=C["ink"], ec="none", zorder=5))
    return fig


def heart_rate(value, mode="small"):
    """small: 1500÷작은 칸, large: 300÷큰 칸, six: 6초 QRS × 10."""
    bpm = 1500 / value if mode == "small" else 300 / value if mode == "large" else value * 10
    cls = "서맥" if bpm < 60 else "빈맥" if bpm > 100 else "정상 범위"
    return dict(bpm=round(bpm), cls=cls, rr_ms=round(60000 / bpm))


def qtc(qt_ms, hr, sex="m"):
    rr = 60 / hr
    f = dict(Bazett=qt_ms / math.sqrt(rr), Fridericia=qt_ms / rr ** (1 / 3),
             Framingham=qt_ms + 154 * (1 - rr), Hodges=qt_ms + 1.75 * (hr - 60))
    q, lim = f["Fridericia"], 450 if sex == "m" else 460
    msg = ("QTc > 500 ms: Torsades de pointes 고위험." if q > 500 else f"QTc 연장 (기준 {lim} ms 초과)." if q > lim
           else "QTc < 350 ms: short QT 가능성." if q < 350 else "정상 범위입니다.")
    if hr > 100:
        msg += " 빈맥에서는 Bazett이 과대평가하므로 Fridericia 값을 기준으로 봤습니다."
    return {k: round(v) for k, v in f.items()}, msg


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def main(argv=None):
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--theme", choices=THEMES, default="light")
    common.add_argument("--dpi", type=int, default=192, help="PNG 해상도 (192 = 원본 화면의 2배)")
    ap = argparse.ArgumentParser(description="ECG 판독 연습실 그래픽 (matplotlib)")
    sp = ap.add_subparsers(dest="cmd", required=True)
    _add = sp.add_parser
    sp.add_parser = lambda *a, **k: _add(*a, parents=[common], **k)

    s = sp.add_parser("strip", help="리듬 strip 한 개")
    s.add_argument("rhythm", choices=RHYTHMS)
    s.add_argument("--seed", type=int)
    s.add_argument("--calipers", type=float, nargs=2, metavar=("T1", "T2"), help="캘리퍼 시점(초)")
    s.add_argument("-o", "--out", default="strip.png")

    s = sp.add_parser("gallery", help="전체 리듬 도감")
    s.add_argument("--seed", type=int)
    s.add_argument("-o", "--out", default="gallery.png")

    s = sp.add_parser("mech", help="원리: 전도계 + 벡터")
    s.add_argument("scenario", choices=SCENARIOS)
    s.add_argument("--t", type=float, help="시점(초). 생략하면 최대 벡터 시점")
    s.add_argument("--leads", nargs="+", choices=LEADS)
    s.add_argument("--gif", help="애니메이션 저장 경로 (.gif 또는 .mp4)")
    s.add_argument("--speed", type=float, default=.2)
    s.add_argument("--fps", type=int, default=20)
    s.add_argument("-o", "--out", default="mech.png")

    s = sp.add_parser("axis", help="QRS 전기축")
    s.add_argument("lead_i", type=float)
    s.add_argument("avf", type=float)
    s.add_argument("-o", "--out", default="axis.png")

    s = sp.add_parser("qtc", help="QTc 계산")
    s.add_argument("qt", type=float)
    s.add_argument("hr", type=float)
    s.add_argument("--sex", choices=["m", "f"], default="m")

    s = sp.add_parser("rate", help="심박수 계산")
    s.add_argument("value", type=float)
    s.add_argument("--mode", choices=["small", "large", "six"], default="small")

    a = ap.parse_args(argv)
    fig = None
    if a.cmd == "strip":
        fig = plot_strip(a.rhythm, a.seed, a.theme, a.calipers)
    elif a.cmd == "gallery":
        fig = plot_gallery(a.seed, a.theme)
    elif a.cmd == "mech":
        if a.gif:
            print(animate_mechanism(a.scenario, a.gif, a.speed, a.fps, a.leads, a.theme, min(a.dpi, 144)))
            return
        fig = plot_mechanism(a.scenario, a.t, a.leads, a.theme)
    elif a.cmd == "axis":
        fig = plot_axis(a.lead_i, a.avf, a.theme)
    elif a.cmd == "qtc":
        vals, msg = qtc(a.qt, a.hr, a.sex)
        for k, v in vals.items():
            print(f"{k:<11}{v} ms")
        print(msg)
    elif a.cmd == "rate":
        r = heart_rate(a.value, a.mode)
        print(f"{r['bpm']} bpm, {r['cls']}. R–R ≈ {r['rr_ms']} ms")
    if fig is not None:
        fig.savefig(a.out, dpi=a.dpi, facecolor=fig.get_facecolor())
        print(a.out)


if __name__ == "__main__":
    main()
