import numpy as np
import soundfile as sf

from mix_engine.auto_mix import auto_mix_stems


def test_auto_mix_renders_stereo_wav(tmp_path):
    sr = 48000
    t = np.arange(sr, dtype=np.float32) / sr
    kick = (0.08 * np.sin(2 * np.pi * 60 * t)).astype(np.float32)
    vocal = (0.03 * np.sin(2 * np.pi * 220 * t)).astype(np.float32)
    kick_path = tmp_path / "kick.wav"
    vocal_path = tmp_path / "vocal.wav"
    sf.write(kick_path, kick, sr, subtype="PCM_24")
    sf.write(vocal_path, vocal, sr, subtype="PCM_24")

    out = tmp_path / "mix.wav"
    log = auto_mix_stems([
        (str(kick_path), "Kick"),
        (str(vocal_path), "Lead Vocal"),
    ], str(out))

    data, out_sr = sf.read(out, always_2d=True)
    assert out_sr == sr
    assert data.shape == (sr, 2)
    assert np.max(np.abs(data)) <= 1.0
    assert log["offline"] is True
    assert len(log["stems"]) == 2


def test_sample_rate_mismatch_is_rejected(tmp_path):
    a = tmp_path / "a.wav"
    b = tmp_path / "b.wav"
    sf.write(a, np.zeros(1000), 44100)
    sf.write(b, np.zeros(1000), 48000)
    try:
        auto_mix_stems([(str(a), "Kick"), (str(b), "Bass")], str(tmp_path / "mix.wav"))
    except ValueError as exc:
        assert "Sample-rate mismatch" in str(exc)
    else:
        raise AssertionError("Expected sample-rate mismatch")
