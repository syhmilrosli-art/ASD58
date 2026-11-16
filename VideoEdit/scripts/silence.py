"""SILENCE: buang bahagian senyap / jeda panjang guna auto-editor.

Guna:  python3 scripts/silence.py input/video.mp4 [output/hasil.mp4]
"""
import shutil
import subprocess

import config as C
from common import TEMP, args_asas, gagal, info, laluan_keluar, lindungi_input, log, semak_alat


def proses(inp, out):
    lindungi_input(out)
    i = info(inp)
    if not i["ada_audio"]:
        log("Tiada audio — langkau buang senyap (salin sahaja)")
        shutil.copyfile(inp, out)
        return out
    TEMP.mkdir(exist_ok=True)
    cmd = ["auto-editor", str(inp),
           "--edit", f"audio:threshold={C.AMBANG_SENYAP}",
           "--margin", C.MARGIN_SENYAP,
           "-c:v", "libx264", "-b:v", "12M", "-c:a", "aac", "-b:a", "192k",
           "--no-open", "--progress", "none", "--temp-dir", str(TEMP / "auto-editor"),
           "-o", str(out)]
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    shutil.rmtree(TEMP / "auto-editor", ignore_errors=True)
    if r.returncode != 0:
        print(r.stdout[-3000:])
        gagal("auto-editor gagal")
    baru = info(out)["tempoh"]
    log(f"Tempoh: {i['tempoh']:.1f}s → {baru:.1f}s (buang {i['tempoh'] - baru:.1f}s senyap)")
    return out


if __name__ == "__main__":
    semak_alat("ffmpeg", "ffprobe", "auto-editor")
    a = args_asas(__doc__).parse_args()
    out = laluan_keluar(a.input, "silence", a.output)
    proses(a.input, out)
    log(f"Siap: {out}")
