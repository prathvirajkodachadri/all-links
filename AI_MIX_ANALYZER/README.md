# AI Audio Mixing & Mastering Analyzer
Standalone Python desktop analyzer; no VST/AU/AAX/plugin components.

## Run
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```
The current foundation provides non-destructive loading, metadata, BS.1770-style loudness history, true-peak oversampling, RMS/crest/clipping/DC checks, FFT bands, stereo/correlation, evidence-based interpretations, JSON/CSV export, background analysis, and tests. Extend modules independently for PDF/PNG reports, drag/drop, full EBU validation, reference comparison, and advanced visual panels.
