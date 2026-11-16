"""VERTICAL: tukar video ke 9:16 (1080x1920, 30fps).
Jika video asal landscape/segi empat, latar belakang diisi versi blur video itu sendiri.

Guna:  python3 scripts/vertical.py input/video.mp4 [output/hasil.mp4]
"""
import config as C
from common import AAC_TEMP, X264_TEMP, args_asas, ffmpeg, info, laluan_keluar, log, semak_alat


def proses(inp, out):
    i = info(inp)
    W, H = C.LEBAR, C.TINGGI
    nisbah_asal = i["lebar"] / i["tinggi"]
    nisbah_sasar = W / H

    if abs(nisbah_asal - nisbah_sasar) < 0.01:
        log(f"Video sudah 9:16 ({i['lebar']}x{i['tinggi']}) — ubah saiz sahaja")
        vf = f"scale={W}:{H}:flags=lanczos,setsar=1,fps={C.FPS}"
        args = ["-vf", vf]
    else:
        jenis = "landscape" if nisbah_asal > 1 else ("segi empat" if nisbah_asal == 1 else "potret lain")
        log(f"Video {jenis} ({i['lebar']}x{i['tinggi']}) — letak di tengah + latar blur")
        if C.KABUR_LATAR > 0:
            latar = (f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                     f"scale=iw/4:ih/4,boxblur={max(1, C.KABUR_LATAR // 4)}:2,scale={W}:{H},"
                     f"eq=brightness=-0.08[bg]")
        else:
            latar = f"color=black:s={W}x{H}:r={C.FPS}[bg]"
        fc = (f"[0:v]split=2[a][b];"
              + latar.replace("[0:v]", "[a]") + ";"
              f"[b]scale={W}:{H}:force_original_aspect_ratio=decrease:flags=lanczos[fg];"
              f"[bg][fg]overlay=(W-w)/2:(H-h)/2:shortest=1,setsar=1,fps={C.FPS},format=yuv420p[v]")
        args = ["-filter_complex", fc, "-map", "[v]", "-map", "0:a?"]

    ffmpeg(["-i", inp, *args, *X264_TEMP, *AAC_TEMP, "-movflags", "+faststart", out])
    return out


if __name__ == "__main__":
    semak_alat("ffmpeg", "ffprobe")
    a = args_asas(__doc__).parse_args()
    out = laluan_keluar(a.input, "vertical", a.output)
    proses(a.input, out)
    log(f"Siap: {out}")
