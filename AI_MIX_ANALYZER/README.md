# AI_MIX_ANALYZER — Professional Audio Measurement & Mix Evidence Engine

A local Python desktop application for measuring a final mix and its stems and producing structured evidence for human or external AI interpretation.

## Project workflow
1. Upload one **MIX / FINAL MIX**.
2. Upload one or more **STEMS** separately.
3. Optionally upload a **REFERENCE MIX**.
4. Run **ANALYZE PROJECT**.
5. Export JSON in one click.

The project export includes individual audio JSON files plus `MIX_ANALYSIS.json` containing cross-stem relationships, mix-vs-stem comparisons, and deterministic priority checks.

## Analysis
- Loudness, true peak, RMS and crest factor
- Spectrum and frequency-band evidence
- Stereo, Mid/Side, correlation and mono compatibility
- Section and time-history measurements
- Cross-stem spectral overlap screening
- Stem level relationships
- Mix-vs-stem frequency-band comparison
- Priority-ranked technical checks
- Optional reference mix analysis

## Important limitation
Spectral overlap is a screening hypothesis, not definitive psychoacoustic masking. The analyzer does not claim to know the artistic intent of a mix and does not automatically apply processing or make irreversible creative decisions. Use the evidence with listening and engineering judgment.

## Run
```bash
pip install -r requirements.txt
python main.py
```

## Tests
```bash
pytest -q
```

Audio remains local. The application does not contain an LLM, cloud upload, AI SDK, or API key.
