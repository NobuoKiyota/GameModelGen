"""下絵の測定（bpy + numpy）。画像は上原点(v=行)で扱う。しきい値は DESIGN.md §3 と同じ手法。"""
import math

import numpy as np

import common as C
import overlay


def _px(key):
    return overlay._load_top_origin(C.BP_DIR / C.BLUEPRINTS[key]["file"]) * 255


def side_silhouette(v0=400, v1=830):
    """側面下絵: 各行の顔の輪郭（最右の黒画素）の u。{行: u}"""
    px = _px("side")
    dark = (px[..., 0] < 75) & (px[..., 1] < 75) & (px[..., 2] < 75)
    return {v: int(np.where(dark[v, 700:900])[0].max()) + 700 for v in range(v0, v1) if dark[v, 700:900].any()}


def side_nose_tip_row(sil):
    rows = [v for v in range(560, 621) if v in sil]
    m = max(sil[v] for v in rows)
    return float(np.mean([v for v in rows if sil[v] == m])), m


def side_subnasale_row(sil):
    """鼻先の下で輪郭が最も引っ込む行（鼻下）。"""
    rows = [v for v in range(625, 661) if v in sil]
    m = min(sil[v] for v in rows)
    return float(np.mean([v for v in rows if sil[v] == m])), m


def side_lip_row():
    """側面の口の線（r<200 の画素）の行の平均。"""
    px = _px("side")
    m = px[665:690, 785:815, 0] < 200
    vv, _ = np.where(m)
    return float(vv.mean() + 665)


def side_chin_row():
    px = _px("side")
    dark = (px[..., 0] < 75) & (px[..., 1] < 75) & (px[..., 2] < 75)
    rows = [v for v in range(780, 840) if dark[v, 740:790].any()]
    return float(max(rows))


def front_chin_row():
    px = _px("front")
    dark = (px[..., 0] < 75) & (px[..., 1] < 75) & (px[..., 2] < 75)
    return float(max(v for v in range(780, 860) if dark[v, 500:525].any()))


def front_nose_dot():
    """正面の鼻（ピンクの点）の重心 (u, v)。"""
    px = _px("front")
    r, g, b = px[..., 0], px[..., 1], px[..., 2]
    m = (r > 225) & (g > 130) & (g < 175) & (b > 120) & (b < 170)
    m[:590] = False
    m[645:] = False
    m[:, :480] = False
    m[:, 545:] = False
    vv, uu = np.where(m)
    return float(uu.mean()), float(vv.mean())


def side_to_front_row_map(side_rows, front_rows):
    """側面の行→正面の行の区分線形マップ（ランドマークで側面の縦位置を正面に合わせる）。"""
    return lambda v_side: float(np.interp(v_side, side_rows, front_rows))


def front_to_side_row_map(side_rows, front_rows):
    return lambda v_front: float(np.interp(v_front, front_rows, side_rows))


# --- 顎（S05）---------------------------------------------------------------

def _resample(points, n):
    """折れ線を弧長で n 点に等分割。points[0] が t=0、points[-1] が t=1。"""
    p = np.array(points, dtype=float)
    seg = np.linalg.norm(np.diff(p, axis=0), axis=1)
    s = np.concatenate([[0], np.cumsum(seg)])
    ts = np.linspace(0, s[-1], n)
    return [(float(np.interp(t, s, p[:, 0])), float(np.interp(t, s, p[:, 1]))) for t in ts]


def front_jaw_contour(n, v_ear=700, half_line_px=3):
    """正面の顔の輪郭（耳の下→顎先）の中心線を、顎先(t=0)→耳の下(t=1) の n 点 (u, v) で返す。
    耳の下は行ごとの最左の黒画素、下側は列ごとの最下の黒画素。線の太さの半分だけ内側に寄せる。"""
    px = _px("front")
    dark = (px[..., 0] < 75) & (px[..., 1] < 75) & (px[..., 2] < 75)
    pts = [(float(np.where(dark[v, 150:512])[0].min() + 150 + half_line_px), float(v)) for v in range(v_ear, 721, 5)]
    u_start = int(pts[-1][0]) + 3
    pts += [(float(u), float(np.where(dark[690:840, u])[0].max() + 690 - half_line_px)) for u in range(u_start, 513, 3)]
    pts.append((float(C.COL0), pts[-1][1]))          # 顎先は正中線 u=512 に置く
    return _resample(pts[::-1], n)


def side_jaw_line(n, sil, half_line_px=3):
    """側面の顎のライン（顎先→耳の下）: 影の上端が作る斜めの線（耳の下→(620,777)）と、そこから顎先の角への直線。
    顎先の角 = 輪郭の chin 行の最右画素。"""
    px = _px("side")
    shadow = (px[..., 0] < 236) & (px[..., 0] > 200) & (px[..., 1] < 190) & (px[..., 1] > 140)
    diag = []
    for u in range(500, 621, 20):
        w = np.where(shadow[655:830, u])[0]
        diag.append((float(u), float(w.min() + 655)))
    chin_row = int(side_chin_row()) - 2
    chin = (float(sil[chin_row] - half_line_px), float(chin_row))
    return _resample([chin] + diag[::-1], n)


# --- 頭の側面（S07）---------------------------------------------------------

def side_ear_front_u():
    """側面下絵: 耳の輪郭の最前（u が最大の黒画素）。顔のマスクの後ろの縁の目安。耳の領域 u 370..560, v 470..680。"""
    px = _px("side")
    dark = (px[..., 0] < 75) & (px[..., 1] < 75) & (px[..., 2] < 75)
    reg = dark[470:680, 370:560]
    vv, uu = np.where(reg)
    return int(uu.max()) + 370


def side_neck_front_u(sil=None, rows=range(832, 850)):
    """側面下絵: 首の前の輪郭（顎の下から下へ落ちる線）の u。行 832..849 の、u 540..700 での最右の黒画素の中央値。"""
    px = _px("side")
    dark = (px[..., 0] < 75) & (px[..., 1] < 75) & (px[..., 2] < 75)
    us = [int(np.where(dark[r, 540:700])[0].max()) + 540 for r in rows if dark[r, 540:700].any()]
    return int(np.median(us)), (min(rows), max(rows))


def side_neck_edges(rows):
    """側面下絵: 首の後ろの線と前の線の u を、各行で。{行: (u後ろ, u前)}（輪郭線の中央）。
    黒画素（<75）の、u 330..700 での最左・最右の位置から、線の太さの半分（2px）だけ内側。
    別の方法（背景色との差）でも測れるよう、側面の背景色との差の版も side_neck_edges_bg にある。"""
    px = _px("side")
    dark = (px[..., 0] < 75) & (px[..., 1] < 75) & (px[..., 2] < 75)
    out = {}
    for r in rows:
        us = np.where(dark[r, 330:700])[0] + 330
        if len(us):
            out[r] = (float(us.min()) + 2, float(us.max()) - 2)
    return out


def side_neck_edges_bg(rows, thr=60):
    """同じものを、背景色（左上の画素）との差が thr を超える画素の最左・最右で測る（輪郭線の外縁。中央より 2px 外）。"""
    px = _px("side")
    bg = px[5, 5][:3]
    diff = np.abs(px[..., :3] - bg).sum(axis=2)
    out = {}
    for r in rows:
        us = np.where(diff[r, 330:700] > thr)[0] + 330
        if len(us):
            out[r] = (float(us.min()) + 2, float(us.max()) - 2)
    return out


def iris_ellipse(view, seed, skip=(15, 165), out_png=None, box=None):
    """下絵の黒目（虹彩）の外側の輪郭線に、軸に平行な楕円を当てはめる。返り値: (cx, cy, a, b, 点の数)（画素、下絵の上原点）。
    seed（瞳の中心付近）から放射状に 5° ごとに進み、強膜（白）・肌・淡い影に出る直前の、最後の黒い画素（輪郭線）の中央を輪郭点にする。
    上側（skip の角度 = 上向きを 90° として）は、まつ毛・まぶたの黒と続くので使わない。"""
    px = _px(view)[..., :3]
    H, W = px.shape[:2]
    su, sv = float(seed[0]), float(seed[1])
    mx, mn = px.max(axis=2), px.min(axis=2)
    val = px.mean(axis=2)
    black = val < 75
    outside = ((val > 225) & ((mx - mn) < 22)) | ((mx - mn) > 34) | ((val > 165) & (px[..., 2] > px[..., 0] + 6))
    pts = []
    for deg in range(0, 360, 5):
        if skip[0] <= deg <= skip[1]:
            continue
        t = math.radians(deg)
        dx, dy = math.cos(t), -math.sin(t)          # 上向きが +（画像は v が下向き）
        last_black = None
        run_start = None
        r = 4.0
        while r < 150:
            x, y = su + dx * r, sv + dy * r
            xi, yi = int(round(x)), int(round(y))
            if not (0 <= xi < W and 0 <= yi < H):
                break
            if outside[yi, xi] and last_black is not None and r - last_black[1] < 8:
                break
            if black[yi, xi]:
                if run_start is None:
                    run_start = r
                last_black = ((run_start + r) / 2, r)
            else:
                run_start = None
            r += 0.5
        if last_black is not None and r < 150:
            rr = last_black[0]
            pts.append((su + dx * rr, sv + dy * rr, deg))
    P = np.array([(x, y) for x, y, _ in pts])
    if len(P) < 8:
        return None

    def fit(Q):
        A = np.stack([Q[:, 0] ** 2, Q[:, 1] ** 2, Q[:, 0], Q[:, 1]], axis=1)
        coef, *_ = np.linalg.lstsq(A, np.ones(len(Q)), rcond=None)
        ca, cb, cc, cd = coef
        cx, cy = -cc / (2 * ca), -cd / (2 * cb)
        k = 1 + ca * cx ** 2 + cb * cy ** 2
        return cx, cy, math.sqrt(k / ca), math.sqrt(k / cb)

    keep = np.ones(len(P), dtype=bool)
    for _ in range(4):                               # 外れ値（まつ毛の黒）を除いて、当てはめ直す
        cx, cy, a_, b_ = fit(P[keep])
        res = np.abs(np.sqrt(((P[:, 0] - cx) / a_) ** 2 + ((P[:, 1] - cy) / b_) ** 2) - 1.0) * min(a_, b_)
        keep = res < 2.5
        if keep.sum() < 8:
            break
    P = P[keep]
    pts = [q for q, k_ in zip(pts, keep) if k_]
    if out_png is not None:
        import bpy
        x0, y0, x1, y1 = box if box else (int(su - 130), int(sv - 110), int(su + 130), int(sv + 110))
        arr = np.ones((y1 - y0, x1 - x0, 4), dtype=np.float32)
        arr[..., :3] = px[y0:y1, x0:x1] / 255.0
        for x, y, _ in pts:
            xi, yi = int(round(x)) - x0, int(round(y)) - y0
            if 0 <= xi < x1 - x0 and 0 <= yi < y1 - y0:
                arr[max(yi - 1, 0):yi + 2, max(xi - 1, 0):xi + 2, :3] = (1, 0, 0)
        for t in np.linspace(0, 2 * math.pi, 240):
            xi, yi = int(round(cx + a_ * math.cos(t))) - x0, int(round(cy + b_ * math.sin(t))) - y0
            if 0 <= xi < x1 - x0 and 0 <= yi < y1 - y0:
                arr[yi, xi, :3] = (0, 0.8, 0)
        arr = np.repeat(np.repeat(arr, 3, axis=0), 3, axis=1)
        img = bpy.data.images.new("iris_tmp", arr.shape[1], arr.shape[0], alpha=False)
        img.pixels.foreach_set(arr[::-1].ravel())
        img.filepath_raw = str(out_png)
        img.file_format = "PNG"
        img.save()
        bpy.data.images.remove(img)
    return float(cx), float(cy), float(a_), float(b_), len(P)


# --- 頭の断面（S07b: 額）-----------------------------------------------------

def head_ellipse_table(v0=120, v1=470, win=7):
    """正面の顔の輪郭の半幅 a と、側面の顔の前の輪郭の前後 b（-Y 方向の大きさ）を、行ごとに測って移動平均で滑らかにする。
    耳は v≈484 以降なので、v1 までを使う（額・側頭部の高さ）。戻り値: {行: (a[m], b[m])}"""
    f, s = _px("front"), _px("side")
    fd = (f[..., 0] < 75) & (f[..., 1] < 75) & (f[..., 2] < 75)
    sd = (s[..., 0] < 75) & (s[..., 1] < 75) & (s[..., 2] < 75)
    rows = list(range(v0, v1))
    a = np.array([(C.COL0 - (np.where(fd[v, 100:512])[0].min() + 100)) * C.K for v in rows])
    b = np.array([((np.where(sd[v, 150:900])[0].max() + 150) - C.COL0) * C.K for v in rows])
    ker = np.ones(win) / win
    a_s = np.convolve(np.pad(a, win // 2, mode="edge"), ker, mode="valid")
    b_s = np.convolve(np.pad(b, win // 2, mode="edge"), ker, mode="valid")
    return {v: (float(a_s[k]), float(b_s[k])) for k, v in enumerate(rows)}


def head_ellipse_at(table, z):
    """高さ z[m] での頭の断面の楕円の半径 (a, b)。"""
    v = C.ROW0 - z / C.K
    rows = sorted(table)
    a = float(np.interp(v, rows, [table[r][0] for r in rows]))
    b = float(np.interp(v, rows, [table[r][1] for r in rows]))
    return a, b


def side_back_u(v):
    """側面下絵: 行 v の頭の後ろの輪郭（最左の黒画素）の u。耳は u>377 なので、u 150..370 の範囲で探す。"""
    px = _px("side")
    dark = (px[..., 0] < 75) & (px[..., 1] < 75) & (px[..., 2] < 75)
    w = np.where(dark[v, 150:520])[0]
    return int(w.min()) + 150 if len(w) else None


def head_ellipsoid_fit(table):
    """頭の断面の楕円（a(Z), b(Z)）の測定表から、楕円体 (X/a0)²+(Y/b0)²+((Z-Zc)/c)²=1 を当てはめる。
    a(Z)² = a0²(1-((Z-Zc)/c)²) は Z の2次式なので、a²・b² を np.polyfit（2次）で求める。丸い頭なので a と b を同じ楕円体にまとめる（平均）。"""
    rows = sorted(table)
    zs = np.array([(C.ROW0 - v) * C.K for v in rows])
    a2 = np.array([table[v][0] ** 2 for v in rows])
    b2 = np.array([table[v][1] ** 2 for v in rows])
    p, q, r = np.polyfit(zs, (a2 + b2) / 2, 2)
    zc = -q / (2 * p)
    a0sq = p * zc ** 2 + q * zc + r
    c = math.sqrt(-a0sq / p)
    return math.sqrt(a0sq), zc, c


def head_outlines(v0=106, v1=700, win=5):
    """頭の外形を行ごとに測る。{行: (A, Bf, Bb)}（単位 m）。
    A  = 断面の半幅（正面の輪郭。耳のある v>470 は後ろの輪郭で代用＝丸い頭）
    Bf = 側面の顔の前の輪郭（Y の絶対値）、Bb = 側面の頭の後ろの輪郭（Y）。移動平均で滑らかにする。"""
    f, s = _px("front"), _px("side")
    fd = (f[..., 0] < 75) & (f[..., 1] < 75) & (f[..., 2] < 75)
    sd = (s[..., 0] < 75) & (s[..., 1] < 75) & (s[..., 2] < 75)
    rows = list(range(v0, v1))
    bb = np.array([(C.COL0 - (np.where(sd[v, 150:520])[0].min() + 150)) * C.K for v in rows])         # 後ろの輪郭（Y は正）
    bf = np.array([((np.where(sd[v, 380:900])[0].max() + 380) - C.COL0) * C.K if v <= 470 else float("nan") for v in rows])
    a = np.array([(C.COL0 - (np.where(fd[v, 100:512])[0].min() + 100)) * C.K if v <= 470 else float("nan") for v in rows])
    a = np.where(np.isnan(a), bb, a)
    bf = np.where(np.isnan(bf), bb, bf)                     # 耳より下は前の輪郭が測れない（顔の輪郭になる）ので、丸い頭として後ろの輪郭で代用
    ker = np.ones(win) / win

    def smooth(x):
        x = np.array(x, dtype=float)
        ok = ~np.isnan(x)
        y = np.where(ok, x, 0.0)
        num = np.convolve(np.pad(y, win // 2, mode="edge"), ker, mode="valid")
        den = np.convolve(np.pad(ok.astype(float), win // 2, mode="edge"), ker, mode="valid")
        return np.where(den > 0, num / np.maximum(den, 1e-9), float("nan"))

    A, Bf, Bb = smooth(a), smooth(bf), smooth(bb)
    return {v: (float(A[k]), float(Bf[k]), float(Bb[k])) for k, v in enumerate(rows)}


class HeadSurface:
    """測定した頭の外形（A(Z)=半幅、Bf(Z)=前の輪郭、Bb(Z)=後ろの輪郭）による頭の表面。
    表面: (X/A(Z))² + (Y/B(Z))² = 1（Y<0 なら Bf、Y>0 なら Bb）。頭頂（下絵の最上端）より上は外側。
    頭の中心からの光線で任意の点を表面へ投影する（頭頂の真上への光線は、頭頂の高さで表面に届いたとみなす）。"""

    def __init__(self, center_z=0.086):
        outl = head_outlines()
        self.rows = np.array(sorted(outl), dtype=float)
        self.a = np.array([outl[int(r)][0] for r in self.rows])
        self.bf = np.array([outl[int(r)][1] for r in self.rows])
        self.bb = np.array([outl[int(r)][2] for r in self.rows])
        self.center = np.array([0.0, 0.0, center_z])
        self.ztop = (C.ROW0 - 104) * C.K

    def A(self, z):
        return np.maximum(np.interp(C.ROW0 - np.asarray(z) / C.K, self.rows, self.a), 1e-3)

    def B(self, z, y):
        v = C.ROW0 - np.asarray(z) / C.K
        return np.maximum(np.where(np.asarray(y) < 0, np.interp(v, self.rows, self.bf), np.interp(v, self.rows, self.bb)), 1e-3)

    def g_many(self, P):
        P = np.asarray(P, dtype=float)
        g = (P[..., 0] / self.A(P[..., 2])) ** 2 + (P[..., 1] / self.B(P[..., 2], P[..., 1])) ** 2 - 1.0
        return np.where(P[..., 2] > self.ztop, 1.0 + (P[..., 2] - self.ztop) * 10, g)

    def g(self, p):
        return float(self.g_many(np.array(p, dtype=float)))

    def project_many(self, P):
        """(N,3) の点を、頭の中心からの光線で表面へ。二分法（60回）。"""
        P = np.asarray(P, dtype=float)
        d = P - self.center
        lo = np.full(len(P), 0.15)
        hi = np.full(len(P), 2.5)
        for _ in range(60):
            mid = (lo + hi) / 2
            pos = self.g_many(self.center + d * mid[:, None]) > 0
            hi = np.where(pos, mid, hi)
            lo = np.where(pos, lo, mid)
        return self.center + d * ((lo + hi) / 2)[:, None]

    def project(self, p):
        return self.project_many(np.array([p], dtype=float))[0]
