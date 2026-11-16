"""LOGO: letak logo dari assets/ di bucu kanan atas (kecil, sedikit lutsinar).

Guna:  python3 scripts/logo.py input/video.mp4 [output/hasil.mp4] [--logo assets/lain.png]
"""
import shutil
from pathlib import Path

import config as C
from common import ASSETS, X264_TEMP, ffmpeg, gagal, info, laluan_keluar, log, semak_alat


def cari_logo(logo=None):
    if logo:
        p = Path(logo)
        if not p.exists():
            gagal(f"Logo tidak dijumpai: {p}")
        return p
    p = ASSETS / C.LOGO_FAIL
    return p if p.exists() else None


def proses(inp, out, logo=None):
    p = cari_logo(logo)
    if p is None:
        log(f"⚠ Tiada logo di assets/{C.LOGO_FAIL} — langkau logo (salin sahaja)")
        shutil.copyfile(inp, out)
        return out
    W = info(inp)["lebar"]
    lebar = round(C.LOGO_LEBAR * W / 1080)
    m = round(C.LOGO_MARGIN * W / 1080)
    fc = (f"[1:v]scale={lebar}:-1:flags=lanczos,format=rgba,"
          f"colorchannelmixer=aa={C.LOGO_LEGAP}[lg];"
          f"[0:v][lg]overlay=W-w-{m}:{m}:format=auto,format=yuv420p[v]")
    log(f"Letak logo {p.name} ({lebar}px, legap {C.LOGO_LEGAP:.0%})")
    ffmpeg(["-i", inp, "-i", p, "-filter_complex", fc,
            "-map", "[v]", "-map", "0:a?", *X264_TEMP, "-c:a", "copy",
            "-movflags", "+faststart", out])
    return out


if __name__ == "__main__":
    import argparse
    semak_alat("ffmpeg", "ffprobe")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input")
    ap.add_argument("output", nargs="?")
    ap.add_argument("--logo", help="fail logo lain (lalai: assets/logo.png)")
    a = ap.parse_args()
    out = laluan_keluar(a.input, "logo", a.output)
    proses(a.input, out, a.logo)
    log(f"Siap: {out}")
