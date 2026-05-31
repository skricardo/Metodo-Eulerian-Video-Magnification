import numpy as np
from scipy.fft import rfft, irfft, rfftfreq


def temporal_bandpass_rfft(signal, fps, low, high):
    """
    Aplica filtro passa-banda temporal via FFT.
    signal: (T, h, w, c) float32
    Retorna o sinal filtrado com a mesma forma.
    """
    T = signal.shape[0]
    if T < 3:
        return np.zeros_like(signal)
    freqs = rfftfreq(T, d=1.0 / fps)
    S = rfft(signal, axis=0)
    mask = (freqs >= low) & (freqs <= high)
    if not np.any(mask):
        return np.zeros_like(signal)
    S_filtered = S * mask[:, None, None, None]
    return irfft(S_filtered, n=T, axis=0)


def estimate_dominant_frequency(signal, fps, low, high):
    """
    Estima a frequência dominante na faixa [low, high].
    signal: (T, H, W, 1) float32 (luminância)
    Retorna a frequência dominante em Hz, ou 0.0 se não encontrada.
    """
    T = signal.shape[0]
    if T < 3:
        return 0.0
    freqs = rfftfreq(T, d=1.0 / fps)
    S = rfft(signal, axis=0)
    mag = np.mean(np.abs(S), axis=(1, 2, 3))
    mask = (freqs >= low) & (freqs <= high)
    if not np.any(mask):
        return 0.0
    idx = np.argmax(mag[mask])
    return float(freqs[mask][idx])