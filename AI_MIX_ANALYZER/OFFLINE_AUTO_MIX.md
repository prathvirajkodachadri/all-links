# Offline Auto Mix v1

This adds a **fully local/offline** automatic mixing engine without changing the existing analyzer workflow.

## What it does

- Reads WAV stems locally with `soundfile`.
- Requires all stems to use the same sample rate.
- Converts mono inputs to stereo safely.
- Applies conservative role-aware gain staging.
- Applies basic role-specific high-pass cleanup.
- Applies a transparent, explainable peak-envelope compressor.
- Sums stems to stereo and applies a final peak ceiling.
- Writes a 24-bit PCM `AUTO_MIX.wav`.
- Writes `AUTO_MIX_DECISIONS.json` containing every decision and measurement.

No cloud service, API key, internet connection, or external AI model is required.

## Windows usage

From the `AI_MIX_ANALYZER` directory:

```powershell
python offline_auto_mix.py --stem "C:\audio\kick.wav" --role Kick --stem "C:\audio\bass.wav" --role Bass --stem "C:\audio\vocal.wav" --role "Lead Vocal" --output "C:\audio\AUTO_MIX.wav"
```

Repeat `--stem PATH --role ROLE` for every stem. Available roles are:

`Other`, `Kick`, `Snare`, `Drums`, `Bass`, `Lead Vocal`, `Backing Vocal`, `Guitar`, `Piano`, `Synth`, `FX`.

## Important

v1 is intentionally conservative and deterministic. It is an **automatic DSP mixer**, not a claim of human-level AI mixing. The decision log makes the processing inspectable and provides a clean foundation for the next stage: using the existing analyzer's masking/stereo/dynamics evidence to drive context-aware mix decisions, then adding a local model only where it improves musical decision making.

The existing `main.py` analyzer is not replaced by this feature.
