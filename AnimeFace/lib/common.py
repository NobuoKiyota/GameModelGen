"""AnimeFace 共通定数・座標変換・ゲート補助。数値は DESIGN.md §2 と一致させること。"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]      # AnimeFace/
REPO = ROOT.parent
BP_DIR = REPO / "textures" / "human"
OUT = ROOT / "out"

# --- 座標系（DESIGN.md §2） -------------------------------------------------
K = 0.0007          # メートル / ピクセル
IMG_PX = 1024
IMG_M = IMG_PX * K  # 0.7168 m（下絵1枚の一辺）
COL0 = 512.0        # 下絵の中心列  -> 正面 X=0 / 側面 Y=0
ROW0 = 518.5        # 瞳の中心行    -> Z=0
REF_DIST = 0.6      # 下絵を置く距離（モデルの裏側）
CAM_DIST = 2.0

BLUEPRINTS = {
    "front": dict(file="chibi_blueprint_front.png", angle_deg=0),
    "a45": dict(file="chibi_blueprint_45deg.png", angle_deg=45),
    "side": dict(file="chibi_blueprint_side.png", angle_deg=90),
}


def front_px_to_xz(u, v):
    return ((u - COL0) * K, (ROW0 - v) * K)


def side_px_to_yz(u, v):
    """側面下絵は顔が画面右向き。Blender の Left ビュー(-X から見る)で右 = -Y。"""
    return (-(u - COL0) * K, (ROW0 - v) * K)


def z_to_row(z):
    return ROW0 - z / K


def project(p, angle_deg):
    """3D点(x,y,z) を、視点角 angle_deg のオルソカメラの下絵ピクセル(u,v)へ。0=正面, 90=側面。
    画面右ベクトル = (cos a, -sin a, 0)。a=0 で u=512+X/K、a=90 で u=512-Y/K（S01 のカメラ配置と一致）。"""
    import math
    a = math.radians(angle_deg)
    x, y, z = p
    return (COL0 + (x * math.cos(a) - y * math.sin(a)) / K, ROW0 - z / K)


class Gates:
    """合否を集めて表示・JSON保存する。1つでも FAIL なら exit code 1。"""

    def __init__(self, step):
        self.step = step
        self.rows = []

    def check(self, name, ok, detail=""):
        self.rows.append(dict(name=name, ok=bool(ok), detail=str(detail)))
        print(f"[{'PASS' if ok else 'FAIL'}] {name}  {detail}")

    def note(self, name, detail=""):
        """合否に関わらない参考情報（下絵どうしの食い違いなど）。"""
        self.rows.append(dict(name=name, ok=True, detail=str(detail), info=True))
        print(f"[INFO] {name}  {detail}")

    def finish(self):
        OUT.mkdir(parents=True, exist_ok=True)
        path = OUT / f"{self.step}_report.json"
        path.write_text(json.dumps(self.rows, ensure_ascii=False, indent=2), encoding="utf-8")
        failed = [r for r in self.rows if not r["ok"]]
        print(f"== {self.step}: {len(self.rows) - len(failed)}/{len(self.rows)} PASS -> {path}")
        if failed:
            sys.exit(1)
