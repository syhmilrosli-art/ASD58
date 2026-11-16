"""Fungsi kongsi untuk semua script VideoEdit."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
INPUT = ROOT / "input"
OUTPUT = ROOT / "output"
ASSETS = ROOT / "assets"
FONTS = ASSETS / "fonts"
TEMP = ROOT / "temp"
MODELS = ROOT / "models"

VIDEO_EXT = {".mp4", ".mov", ".mkv", ".avi", ".m4v", ".webm", ".mts", ".3gp"}

# Tetapan encode sementara (kualiti tinggi, supaya tak rosak sebelum compress akhir)
X264_TEMP = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-pix_fmt", "yuv420p"]
AAC_TEMP = ["-c:a", "aac", "-b:a", "192k", "-ar", "48000"]


def log(msg):
    print(f"▶ {msg}", flush=True)


def gagal(msg):
    print(f"✖ RALAT: {msg}", file=sys.stderr, flush=True)
    sys.exit(1)


def semak_alat(*nama):
    for n in nama:
        if not shutil.which(n):
            gagal(f"'{n}' tidak dijumpai. Sila install dahulu (lihat PANDUAN.md).")


def lindungi_input(out_path):
    """Pastikan kita TIDAK sekali-kali menulis ke dalam folder input/."""
    out = Path(out_path).resolve()
    if INPUT.resolve() in out.parents or out == INPUT.resolve():
        gagal(f"Tidak dibenarkan tulis ke folder input/: {out}")


def run(cmd, cwd=None):
    if cmd and cmd[0] == "ffmpeg" and cmd[-1] != "-":
        lindungi_input(cmd[-1])
    r = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if r.returncode != 0:
        print(r.stderr[-3000:], file=sys.stderr)
        gagal(f"Arahan gagal: {' '.join(str(c) for c in cmd[:6])} ...")
    return r


def ffmpeg(args, cwd=None):
    return run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *map(str, args)], cwd=cwd)


def probe(path):
    r = run(["ffprobe", "-v", "error", "-print_format", "json",
             "-show_streams", "-show_format", str(path)])
    return json.loads(r.stdout)


def info(path):
    """Pulangkan dict: lebar, tinggi (selepas putaran), tempoh, ada_audio."""
    d = probe(path)
    v = next((s for s in d["streams"] if s["codec_type"] == "video"), None)
    if v is None:
        gagal(f"Tiada video dalam fail: {path}")
    w, h = int(v["width"]), int(v["height"])
    rot = 0
    for sd in v.get("side_data_list", []):
        if "rotation" in sd:
            rot = int(float(sd["rotation"]))
    rot = int(v.get("tags", {}).get("rotate", rot))
    if abs(rot) % 180 == 90:
        w, h = h, w
    dur = float(d["format"].get("duration") or v.get("duration") or 0)
    ada_audio = any(s["codec_type"] == "audio" for s in d["streams"])
    return {"lebar": w, "tinggi": h, "tempoh": dur, "ada_audio": ada_audio}


def laluan_keluar(inp, akhiran, out=None):
    """Jika out tidak diberi: output/<nama>_<akhiran>.mp4"""
    if out:
        p = Path(out)
    else:
        OUTPUT.mkdir(exist_ok=True)
        p = OUTPUT / f"{Path(inp).stem}_{akhiran}.mp4"
    p.parent.mkdir(parents=True, exist_ok=True)
    lindungi_input(p)
    return p


def args_asas(keterangan):
    import argparse
    ap = argparse.ArgumentParser(description=keterangan)
    ap.add_argument("input", help="fail video masuk")
    ap.add_argument("output", nargs="?", help="fail video keluar (pilihan)")
    return ap
