import math
import cv2
import numpy as np
from tqdm import trange
from .pyramid import build_laplacian_pyramid, reconstruct_laplacian_pyramid
from .filters import temporal_bandpass_rfft


def evm_side_by_side_pipeline(input_path, output_path, params):
    """
    Pipeline EVM completo. Gera vídeo lado a lado (Original | EVM).
    """
    cap = cv2.VideoCapture(input_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Vídeo: {input_path} — {total_frames} frames, {fps} fps, {W}x{H}")
    chunk_frames = max(4, int(round(params["chunk_seconds"] * fps)))
    hop = chunk_frames
    print(f"chunk_frames={chunk_frames}, hop={hop}")
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_path, fourcc, fps, (W * 2, H))
    

    def read_block(start_idx, n):
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_idx)
        frames = []
        for _ in range(n):
            ret, f = cap.read()
            if not ret:
                break
            f = cv2.cvtColor(f, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
            frames.append(f)
        if len(frames) == 0:
            return None
        return np.stack(frames, axis=0)
    blocks = math.ceil(total_frames / hop)
    pbar = trange(0, blocks, desc="Blocks")
    written = 0
    for bi in pbar:
        start = bi * hop
        block = read_block(start, chunk_frames)
        if block is None:
            break
        T = block.shape[0]
        # Empilha pirâmides por nível
        pyrs_by_level = [[] for _ in range(params["levels"] + 1)]
        for t in range(T):
            pyr = build_laplacian_pyramid(block[t], levels=params["levels"])
            for lvl in range(params["levels"] + 1):
                pyrs_by_level[lvl].append(pyr[lvl])
        for lvl in range(params["levels"] + 1):
            pyrs_by_level[lvl] = np.stack(pyrs_by_level[lvl], axis=0)
        # Filtra e amplifica cada nível de detalhe
        filtered_per_level = []
        for lvl in range(params["levels"]):
            arr = pyrs_by_level[lvl]
            filt = temporal_bandpass_rfft(arr, fps, params["freq_low"], params["freq_high"])
            alpha = (
                params["alpha_levels"][lvl]
                if lvl < len(params["alpha_levels"])
                else params["alpha_levels"][-1]
            )
            filtered_per_level.append(filt * alpha)
        filtered_per_level.append(np.zeros_like(pyrs_by_level[-1]))
        # Reconstrói e escreve frames
        for t in range(T):
            new_pyr = [pyrs_by_level[lvl][t] + filtered_per_level[lvl][t]
                       for lvl in range(params["levels"] + 1)]
            evm_frame = np.clip(reconstruct_laplacian_pyramid(new_pyr), 0.0, 1.0)
            evm_u8 = (evm_frame * 255.0).astype(np.uint8)
            orig_u8 = (block[t] * 255.0).astype(np.uint8)
            side = np.concatenate((orig_u8, evm_u8), axis=1)
            if not np.isfinite(side).all():
                side = np.nan_to_num(side, nan=0, posinf=255, neginf=0).astype(np.uint8)
            writer.write(cv2.cvtColor(side, cv2.COLOR_RGB2BGR))
            written += 1
        pbar.set_postfix({"written_frames": written})
    writer.release()
    cap.release()
    print("Processamento completo. Frames escritos:", written)
    return output_path