# AI_MIX_ANALYZER — Professional Audio Measurement & ChatGPT Evidence Engine

A local Python desktop application for measuring a final mix and its stems and producing structured, evidence-first data for manual review in ChatGPT or by a human mix engineer.

## Recommended workflow — no API required
1. Upload one **MIX / FINAL MIX**.
2. Upload all relevant **STEMS** and assign their roles.
3. Optionally upload a **REFERENCE MIX**.
4. Run **ANALYZE PROJECT**.
5. Export the normal per-file JSON files and `MIX_ANALYSIS.json`.
6. Use the ChatGPT-ready package when you want a complete evidence bundle for manual upload to ChatGPT.

The analyzer is intentionally **not an embedded AI mixer**. It measures the audio. ChatGPT is the interpretation layer. This avoids API keys, API costs, and fabricated local AI decisions.

## ChatGPT-ready evidence package
The package generator in `analyzer/chatgpt_package.py` creates:

```text
ChatGPT_Mix_Analysis/
├── MIX_ANALYSIS.json
├── CHATGPT_PROMPT.md
└── stems/
    ├── Kick.json
    ├── Bass.json
    └── ...
```

It also creates `ChatGPT_Mix_Analysis.zip` for convenient manual upload. `MIX_ANALYSIS.json` uses schema version **3.0** and is organized around:

- project metadata
- complete mix measurements
- optional reference measurements
- complete per-stem measurements and roles
- cross-stem spectral relationships
- relative stem-level relationships
- mix-vs-stem frequency-band evidence
- mix-vs-reference level and spectral comparison
- section/time analysis
- deterministic technical priority checks
- methodology and limitations

`CHATGPT_PROMPT.md` tells ChatGPT to separate measured evidence from inference, avoid inventing facts, consider stem roles, rank the most important actions, use frequency/time regions when supported, and provide a verification plan for the next mix revision.

## Analysis coverage
- Loudness / LUFS
- True peak
- RMS and crest-factor evidence
- Spectrum and frequency-band evidence
- Stereo correlation and stereo measurements available from the analyzer
- Section and time-history measurements
- Cross-stem spectral overlap screening
- Relative stem-level relationships
- Mix-vs-stem frequency-band comparison
- Mix-vs-reference comparison when a reference is supplied
- Deterministic technical priority checks

## Evidence philosophy
The application reports measurements and relationships; it should not pretend that a number alone proves an artistic problem. Spectral overlap is a screening hypothesis, not definitive psychoacoustic masking. Independent stem timelines are not assumed sample-aligned. Reference differences are not automatically defects because arrangement, genre, mastering, and loudness can differ.

Use ChatGPT to interpret the evidence together with your musical intent and listening observations.

## Run
```bash
pip install -r requirements.txt
python main.py
```

## Tests
```bash
pytest -q
```

Audio analysis remains local. The application contains no LLM, cloud audio upload, AI SDK, or API key requirement.
