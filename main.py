import os
import urllib.request
import subprocess
from src.pipeline import evm_side_by_side_pipeline

# ── Parâmetros ────────────────────────────────────────────────────────────────
# NOVO - Batimento cardíaco
PARAMS = {
    "levels": 3,
    "alpha_levels": [80, 40, 10],   # muito mais amplificação (sinal sutil)
    "freq_low": 0.8,                 # ~48 bpm mínimo
    "freq_high": 2.5,                # ~150 bpm máximo
    "chunk_seconds": 8.0,
}
VIDEO_URL = "https://people.csail.mit.edu/mrub/evm/video/baby2.mp4"
INPUT_DIR = "videos/input"
OUTPUT_DIR = "videos/output"
ORIG_PATH = os.path.join(INPUT_DIR, "baby2_orig.mp4")
OPT_PATH = os.path.join(INPUT_DIR, "baby2_480p_20fps.mp4")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "baby2_evm_sidebyside.mp4")

# ── Download ──────────────────────────────────────────────────────────────────
def download_video():
    if not os.path.exists(ORIG_PATH):
        print("Baixando vídeo...")
        urllib.request.urlretrieve(VIDEO_URL, ORIG_PATH)
        print("Download concluído:", ORIG_PATH)
    else:
        print("Vídeo já existe:", ORIG_PATH)

# ── Transcodificação ──────────────────────────────────────────────────────────
def transcode_video():
    if not os.path.exists(OPT_PATH):
        print("Transcodificando para 480p @ 20fps...")
        subprocess.run([
            "ffmpeg", "-y", "-i", ORIG_PATH,
            "-vf", "scale=-2:480", "-r", "20",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-c:a", "copy", OPT_PATH
        ], check=True)
        print("Transcodificação concluída:", OPT_PATH)
    else:
        print("Arquivo otimizado já existe:", OPT_PATH)
        
# ── Execução ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    download_video()
    transcode_video()
    output = evm_side_by_side_pipeline(OPT_PATH, OUTPUT_PATH, PARAMS)
    print("Output salvo em:", output)