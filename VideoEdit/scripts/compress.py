"""COMPRESS: H.264 + AAC, sedia upload (TikTok/Reels/Shorts), saiz bawah 100MB.

Guna:  python3 scripts/compress.py input/video.mp4 [output/hasil.mp4]
"""
import config as C
from common import args_asas, ffmpeg, info, laluan_keluar, log, semak_alat


def proses(inp, out):
    i = info(inp)
    dur = max(i["tempoh"], 1)
    # bitrate maksimum supaya saiz <= SAIZ_MAKS_MB (tolak 3% untuk overhead container)
    jumlah_kbps = C.SAIZ_MAKS_MB * 8 * 1000 * 0.97 / dur
    audio = C.BITRATE_AUDIO if i["ada_audio"] else 0
    vmax = int(min(C.BITRATE_VIDEO_MAKS, jumlah_kbps - audio))
    if vmax < 300:
        log(f"⚠ Video panjang ({dur/60:.1f} min) — kualiti akan rendah supaya muat {C.SAIZ_MAKS_MB}MB")
        vmax = max(vmax, 150)

    audio_args = ["-c:a", "aac", "-b:a", f"{C.BITRATE_AUDIO}k", "-ar", "44100", "-ac", "2"] \
        if i["ada_audio"] else ["-an"]
    asas = ["-c:v", "libx264", "-preset", "medium", "-profile:v", "high", "-level", "4.1",
            "-pix_fmt", "yuv420p", "-r", str(C.FPS), "-g", str(C.FPS * 2)]

    log(f"Compress (CRF {C.CRF}, had {vmax} kbps)...")
    ffmpeg(["-i", inp, *asas, "-crf", str(C.CRF), "-maxrate", f"{vmax}k",
            "-bufsize", f"{vmax * 2}k", *audio_args, "-movflags", "+faststart", out])

    mb = out.stat().st_size / 1e6
    if mb > C.SAIZ_MAKS_MB:
        # Jarang berlaku — ulang dengan 2-pass bitrate tetap untuk jamin saiz
        sasar = int(vmax * 0.92)
        log(f"Saiz {mb:.1f}MB melebihi had — ulang 2-pass pada {sasar} kbps")
        log_pass = str(out.with_suffix(".pass"))
        ffmpeg(["-i", inp, *asas, "-b:v", f"{sasar}k", "-pass", "1", "-passlogfile", log_pass,
                "-an", "-f", "null", "-"])
        ffmpeg(["-i", inp, *asas, "-b:v", f"{sasar}k", "-pass", "2", "-passlogfile", log_pass,
                *audio_args, "-movflags", "+faststart", out])
        for f in out.parent.glob(out.stem + ".pass*"):
            f.unlink()
        mb = out.stat().st_size / 1e6
    log(f"Saiz akhir: {mb:.1f} MB")
    return out


if __name__ == "__main__":
    semak_alat("ffmpeg", "ffprobe")
    a = args_asas(__doc__).parse_args()
    out = laluan_keluar(a.input, "compress", a.output)
    proses(a.input, out)
    log(f"Siap: {out}")
