"""Deterministic, fully offline automatic mix renderer.

The engine deliberately uses explainable DSP rather than a cloud model. It reads WAV
stems, assigns safe role-aware targets, applies conservative gain/EQ/compression,
and writes a stereo WAV plus a JSON decision log.
"""
from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterable, Tuple

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt


@dataclass
class AutoMixConfig:
    target_peak_dbfs: float = -6.0
    mix_peak_dbfs: float = -1.0
    compressor_threshold_dbfs: float = -18.0
    compressor_ratio: float = 2.0
    compressor_attack_ms: float = 12.0
    compressor_release_ms: float = 120.0
    max_gain_db: float = 12.0
    max_cut_db: float = -12.0
    sample_rate_tolerance: int = 0


ROLE_TARGETS = {
    "Kick": -18.0, "Snare": -20.0, "Drums": -19.0, "Bass": -20.0,
    "Lead Vocal": -17.0, "Backing Vocal": -22.0, "Guitar": -23.0,
    "Piano": -24.0, "Synth": -24.0, "FX": -28.0, "Other": -24.0,
}


def _db(x: float, floor: float = 1e-12) -> float:
    return 20.0 * math.log10(max(abs(float(x)), floor))


def _rms_db(x: np.ndarray) -> float:
    return _db(np.sqrt(np.mean(np.square(x.astype(np.float64))) + 1e-15))


def _peak_db(x: np.ndarray) -> float:
    return _db(np.max(np.abs(x)) + 1e-15)


def _gain(x: np.ndarray, db: float) -> np.ndarray:
    return x * (10.0 ** (db / 20.0))


def _highpass(x: np.ndarray, sr: int, hz: float) -> np.ndarray:
    if hz <= 0 or hz >= sr / 2:
        return x
    sos = butter(2, hz, btype="highpass", fs=sr, output="sos")
    return sosfilt(sos, x, axis=0)


def _lowpass(x: np.ndarray, sr: int, hz: float) -> np.ndarray:
    if hz <= 0 or hz >= sr / 2:
        return x
    sos = butter(2, hz, btype="lowpass", fs=sr, output="sos")
    return sosfilt(sos, x, axis=0)


def _compress(x: np.ndarray, sr: int, threshold_db: float, ratio: float,
              attack_ms: float, release_ms: float) -> np.ndarray:
    """Simple peak-envelope compressor with attack/release smoothing."""
    mono = np.max(np.abs(x), axis=1) if x.ndim == 2 else np.abs(x)
    attack = math.exp(-1.0 / max(1.0, sr * attack_ms / 1000.0))
    release = math.exp(-1.0 / max(1.0, sr * release_ms / 1000.0))
    env = np.zeros_like(mono, dtype=np.float64)
    prev = 0.0
    for i, v in enumerate(mono):
        a = attack if v > prev else release
        prev = a * prev + (1.0 - a) * float(v)
        env[i] = prev
    env_db = 20.0 * np.log10(np.maximum(env, 1e-9))
    over = np.maximum(env_db - threshold_db, 0.0)
    gain_db = -over * (1.0 - 1.0 / max(1.0, ratio))
    return x * (10.0 ** (gain_db / 20.0))[:, None]


def _role_tone(x: np.ndarray, role: str, sr: int) -> Tuple[np.ndarray, Dict[str, float]]:
    """Conservative role cleanup; no boost above unity is applied."""
    decisions: Dict[str, float] = {}
    if role in {"Kick", "Bass"}:
        x = _highpass(x, sr, 28.0 if role == "Kick" else 32.0)
        decisions["highpass_hz"] = 28.0 if role == "Kick" else 32.0
    elif role in {"Lead Vocal", "Backing Vocal", "Guitar", "Piano", "Synth"}:
        x = _highpass(x, sr, 65.0 if "Vocal" in role else 55.0)
        decisions["highpass_hz"] = 65.0 if "Vocal" in role else 55.0
    elif role == "FX":
        x = _highpass(x, sr, 45.0)
        decisions["highpass_hz"] = 45.0
    return x, decisions


def _stereo(x: np.ndarray) -> np.ndarray:
    if x.ndim == 1:
        return np.column_stack([x, x])
    if x.shape[1] == 1:
        return np.repeat(x, 2, axis=1)
    return x[:, :2]


def auto_mix_stems(stems: Iterable[Tuple[str, str]], output_wav: str,
                   decisions_json: str | None = None,
                   config: AutoMixConfig | None = None) -> Dict:
    """Render a conservative automatic stereo mix from (path, role) stems.

    All processing happens locally. Inputs must share sample rate and channel layout
    can be mono/stereo; the output is stereo WAV at the input sample rate.
    """
    cfg = config or AutoMixConfig()
    loaded = []
    sr0 = None
    max_len = 0
    for path, role in stems:
        data, sr = sf.read(str(path), always_2d=True, dtype="float32")
        if sr0 is None:
            sr0 = sr
        elif abs(sr - sr0) > cfg.sample_rate_tolerance:
            raise ValueError(f"Sample-rate mismatch: {path} is {sr} Hz; expected {sr0} Hz")
        data = _stereo(data)
        loaded.append((str(path), role if role in ROLE_TARGETS else "Other", data))
        max_len = max(max_len, len(data))
    if not loaded:
        raise ValueError("No stems supplied")

    processed = []
    log = {"version": 1, "offline": True, "sample_rate": sr0,
           "config": asdict(cfg), "stems": [], "warnings": []}
    for path, role, data in loaded:
        if len(data) < max_len:
            data = np.pad(data, ((0, max_len - len(data)), (0, 0)))
        input_rms = _rms_db(data)
        target = ROLE_TARGETS[role]
        gain_db = float(np.clip(target - input_rms, cfg.max_cut_db, cfg.max_gain_db))
        y = _gain(data, gain_db)
        y, tone = _role_tone(y, role, sr0)
        pre_comp_peak = _peak_db(y)
        y = _compress(y, sr0, cfg.compressor_threshold_dbfs, cfg.compressor_ratio,
                       cfg.compressor_attack_ms, cfg.compressor_release_ms)
        processed.append(y)
        log["stems"].append({
            "file": path, "role": role, "input_rms_dbfs": round(input_rms, 3),
            "gain_db": round(gain_db, 3), "pre_compression_peak_dbfs": round(pre_comp_peak, 3),
            "tone": tone, "compression": {"threshold_dbfs": cfg.compressor_threshold_dbfs,
                                             "ratio": cfg.compressor_ratio},
        })

    mix = np.sum(processed, axis=0, dtype=np.float64)
    peak = _peak_db(mix)
    master_gain_db = min(0.0, cfg.mix_peak_dbfs - peak)
    mix = _gain(mix, master_gain_db)
    final_peak = _peak_db(mix)
    if final_peak > cfg.mix_peak_dbfs + 0.05:
        log["warnings"].append("Final peak remains above the configured ceiling.")
    mix = np.clip(mix, -1.0, 1.0).astype(np.float32)
    sf.write(str(output_wav), mix, sr0, subtype="PCM_24")
    log["master"] = {"pre_gain_peak_dbfs": round(peak, 3),
                     "master_gain_db": round(master_gain_db, 3),
                     "final_peak_dbfs": round(_peak_db(mix), 3),
                     "output": str(output_wav)}
    if decisions_json:
        Path(decisions_json).parent.mkdir(parents=True, exist_ok=True)
        Path(decisions_json).write_text(json.dumps(log, indent=2), encoding="utf-8")
    return log
