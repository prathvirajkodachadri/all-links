# AI_MIX_ANALYZER — Professional Audio Measurement & ChatGPT Evidence Engine

A local Python desktop application for measuring a final mix and its stems and producing structured, evidence-first data for manual review in ChatGPT or by a human mix engineer.

## Recommended workflow — no API required
1. Upload one **MIX / FINAL MIX**.
2. Upload all relevant **STEMS** and assign their roles.
3. Optionally upload a **REFERENCE MIX**.
4. Click **ANALYZE PROJECT** and wait until analysis is fully complete.
5. Use **EXPORT FOR CHATGPT** to create `ChatGPT_Mix_Analysis.zip` when you want the complete ChatGPT evidence bundle.
6. Use **EXPORT STEM JSON** when you want only the individual stem measurement JSON files.

The export buttons remain disabled until every selected file has been analyzed successfully. If any file fails, the application reports the failed file(s) and requires the project to be analyzed successfully before export. This prevents incomplete exports from being mistaken for complete project evidence.

The analyzer is intentionally **not an embedded AI mixer**. It measures the audio. ChatGPT is the interpretation layer. This avoids API keys, API costs, and fabricated local AI decisions.

## The three main actions

```text
ANALYZE PROJECT
EXPORT FOR CHATGPT
EXPORT STEM JSON
```

### ANALYZE PROJECT
Analyzes the final mix, all selected stems, and the optional reference mix. It also calculates deterministic project-level relationships and priority checks.

### EXPORT FOR CHATGPT
Creates:

```text
ChatGPT_Mix_Analysis.zip
└── ChatGPT_Mix_Analysis/
    ├── MIX_ANALYSIS.json
    ├── CHATGPT_MIX_REVIEW_PROMPT.txt
    ├── README_UPLOAD_TO_CHATGPT.txt
    └── stems/
        ├── Kick.json
        ├── Bass.json
        └── ...
```

`MIX_ANALYSIS.json` is the main evidence file for ChatGPT. The prompt is also included in the ZIP so the package is self-contained.

Recommended manual upload order in ChatGPT:
1. `CHATGPT_MIX_REVIEW_PROMPT.txt`
2. `MIX_ANALYSIS.json`
3. Individual stem JSON files if additional detail is needed.

### EXPORT STEM JSON
Exports one JSON file per successfully analyzed stem to a folder selected by the user. This is useful when a particular stem needs to be inspected separately or shared without the complete ChatGPT package.

## Canonical ChatGPT prompt
The permanent prompt is:

`CHATGPT_MIX_REVIEW_PROMPT.txt`

It is intentionally detailed but designed to remain under 10 A4 pages when rendered as normal text. It instructs ChatGPT to:

- treat analyzer values as evidence rather than absolute truth
- distinguish measured evidence, inference, action, and verification
- prioritize the few changes most likely to improve the mix
- use cross-stem relationships rather than isolated metrics
- consider sections/time history and reference comparisons when available
- recommend practical starting ranges without false precision
- recommend industry-leading third-party plugins only when justified by evidence
- provide plugin-specific starting settings, listening goals, and bypass criteria
- exclude UAD plugins
- avoid EQ/compression/saturation/widening by template
- finish with a concise Mix V2 priority list of no more than seven actions

## JSON evidence structure
`MIX_ANALYSIS.json` uses schema version **3.0** and is organized around:

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
