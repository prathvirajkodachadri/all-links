# AI_MIX_ANALYZER — Professional Audio Measurement & Evidence Engine

A local, deterministic Python desktop application for measuring audio stems and mixes. It exports objective JSON, CSV and PDF evidence for later interpretation by a human or external reasoning tool.

## It does
- Decode supported audio and preserve source files
- Measure loudness, true peak, RMS, crest factor and section dynamics
- Measure spectrum, stereo, Mid/Side, correlation and technical QC
- Compare cross-stem frequency overlap and role metadata
- Export versioned measurement evidence

## It does not do
- No LLM, AI SDK, cloud upload or API key
- No mix score
- No universal good/bad judgments
- No mixing recommendations or automatic processing

## Run
```bash
pip install -r requirements.txt
python main.py
```

## Tests
```bash
pytest -q
```

The primary machine-readable export is the versioned evidence JSON. Methodology and limitations are embedded in the package. Audio remains local.

## Loudness methodology
Loudness output is structured as integrated, momentary (400 ms), short-term (3 s), and LRA fields, each with timed histories and statistics. If `pyloudnorm` is installed, integrated loudness uses its BS.1770-compatible meter. Windowed histories are calculated independently from K-weighted energy windows and are not derived by averaging LUFS values. LRA is explicitly labeled as an EBU R 128 / Tech 3342-style estimate. Silence is represented by `null` plus `below_measurement_floor`, not an arbitrary loudness value. Channel-layout limitations and settings are included in the exported methodology.
