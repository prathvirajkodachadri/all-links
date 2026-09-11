"""Command-line entry point for the fully local automatic mixer.

Example:
  python offline_auto_mix.py --stem vocal.wav --role "Lead Vocal" \
      --stem kick.wav --role Kick --stem bass.wav --role Bass \
      --output AUTO_MIX.wav

The command accepts one --stem followed immediately by one --role, repeated as
needed. No network/API/model is required.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from mix_engine import AutoMixConfig, auto_mix_stems


def main() -> int:
    p = argparse.ArgumentParser(description="Offline AI Mix Analyzer automatic mixer v1")
    p.add_argument("--stem", action="append", required=True, help="Stem WAV path; repeat for each stem")
    p.add_argument("--role", action="append", required=True,
                   choices=["Other", "Kick", "Snare", "Drums", "Bass", "Lead Vocal",
                            "Backing Vocal", "Guitar", "Piano", "Synth", "FX"])
    p.add_argument("--output", default="AUTO_MIX.wav", help="Output stereo WAV")
    p.add_argument("--decisions", default="AUTO_MIX_DECISIONS.json", help="Decision log JSON")
    args = p.parse_args()
    if len(args.stem) != len(args.role):
        p.error("Each --stem must have a matching --role")
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    log = auto_mix_stems(list(zip(args.stem, args.role)), args.output, args.decisions, AutoMixConfig())
    print(f"Rendered: {log['master']['output']}")
    print(f"Final peak: {log['master']['final_peak_dbfs']:.2f} dBFS")
    print(f"Decision log: {args.decisions}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
