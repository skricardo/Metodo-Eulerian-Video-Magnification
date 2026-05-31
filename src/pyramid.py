import cv2
import numpy as np


def build_laplacian_pyramid(frame, levels=3):
    """
    Constrói a pirâmide Laplaciana de um frame.
    frame: float32 RGB [0, 1]
    Retorna lista de camadas de detalhe + base residual.
    """
    pyr = []
    current = frame.copy()
    for _ in range(levels):
        down = cv2.pyrDown((current * 255).astype(np.uint8)).astype(np.float32) / 255.0
        up = cv2.pyrUp(
            (down * 255).astype(np.uint8),
            dstsize=(current.shape[1], current.shape[0])
        ).astype(np.float32) / 255.0
        lap = current - up
        pyr.append(lap)
        current = down
    pyr.append(current)  # base residual
    return pyr


def reconstruct_laplacian_pyramid(pyr):
    """
    Reconstrói o frame a partir da pirâmide Laplaciana.
    """
    current = pyr[-1]
    for level in reversed(pyr[:-1]):
        up = cv2.pyrUp(
            (current * 255).astype(np.uint8),
            dstsize=(level.shape[1], level.shape[0])
        ).astype(np.float32) / 255.0
        current = up + level
    return current