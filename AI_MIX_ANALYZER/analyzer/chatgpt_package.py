"""Build a compact, evidence-first package for manual ChatGPT mix review."""
import json
import os
import zipfile
from .project_analysis import analyze_project, priority_actions

PROMPT = """# AI Mix Analyzer — ChatGPT Review Instructions

You are reviewing a music mix using objective measurements exported by AI Mix Analyzer.

## Rules
1. Treat measured values as evidence, not absolute truth.
2. Do not invent measurements, missing stems, musical intent, or audible problems.
3. Clearly distinguish **measured evidence**, **inference**, and **recommendation**.
4. Prioritize the few changes most likely to improve the mix rather than suggesting EQ on every stem.
5. Consider stem roles and relationships together. A frequency overlap is a screening signal, not proof of masking.
6. Use frequency ranges, time/section information, and affected stems when the data supports them.
7. Avoid false precision. Give practical starting ranges rather than pretending one exact EQ value is universally correct.
8. Consider the reference mix when present, but account for differences in arrangement, mastering, loudness, and genre.
9. If evidence is insufficient, say what cannot be concluded and what listening test would resolve it.
10. Do not assume independently analyzed stems are sample-aligned unless the data explicitly says so.

## Required response
Produce a professional mix-review report with:

### 1. Executive assessment
- Overall strengths
- Biggest risks/problems
- Top 3 priorities

### 2. Evidence-based findings
For each important finding:
- Problem / observation
- Measured evidence
- Affected stem(s) and role(s)
- Frequency and/or section/time region when available
- Confidence: High / Medium / Low

### 3. Mixing action plan
Rank actions from highest to lowest priority. For each:
- What to change
- Which stem(s)
- Suggested starting approach
- What to listen for
- How to verify the change with the analyzer

### 4. Reference comparison
If a reference exists, identify meaningful level, spectrum, dynamics, or stereo differences supported by the measurements. Do not treat every difference as a defect.

### 5. Verification checklist
Give a short checklist for the next mix revision, including mono/stereo, headroom, dynamics, tonal balance, and the most important stem relationships supported by the evidence.

End with a concise **Mix v2 priority list** containing no more than 7 actions.
"""


def _clean_analysis(d):
    """Keep the complete deterministic analysis while making JSON intent explicit."""
    return d


def build_project_payload(mix, stems, reference=None):
    valid_stems=[]
    for path, data in stems.items():
        if isinstance(data, dict) and "error" not in data:
            valid_stems.append({"file":os.path.basename(path),"role":data.get("role","Other"),"analysis":_clean_analysis(data)})
    project=analyze_project(mix, stems, reference)
    project["priority_actions"]=priority_actions(mix, stems, project)
    return {
        "schema_version":"3.0",
        "schema_name":"AI_MIX_ANALYSIS_CHATGPT",
        "project":{
            "mix_file":os.path.basename(mix.get("file",{}).get("path",mix.get("file",{}).get("filename",""))) if mix else None,
            "reference_file":os.path.basename(reference.get("file",{}).get("path",reference.get("file",{}).get("filename",""))) if isinstance(reference,dict) and "error" not in reference else None,
            "stem_count":len(valid_stems)
        },
        "mix":{"measurements":_clean_analysis(mix)},
        "reference":{"present":isinstance(reference,dict) and "error" not in reference,"measurements":_clean_analysis(reference) if isinstance(reference,dict) and "error" not in reference else None},
        "stems":valid_stems,
        "relationships":project.get("stem_relationships",{}),
        "mix_vs_stem":project.get("mix_vs_stem",[]),
        "reference_comparison":project.get("reference_comparison",{"available":False}),
        "project_evidence":{
            "priority_actions":project.get("priority_actions",[]),
            "summary":project.get("mix"),
            "methodology":project.get("methodology",{})
        },
        "analysis_sections":{
            "mix_sections":mix.get("sections",[]) if isinstance(mix,dict) else [],
            "mix_time_analysis":mix.get("time_analysis",{}) if isinstance(mix,dict) else {}
        },
        "ai_context":{
            "purpose":"Objective evidence package for manual upload to ChatGPT. The analyzer does not make creative mix decisions.",
            "interpretation":"Use the measurements to reason about priorities, then recommend changes conservatively.",
            "limitations":project.get("methodology",{})
        }
    }


def export_chatgpt_package(folder, mix_path, mix, stems, reference_path=None, reference=None):
    os.makedirs(folder, exist_ok=True)
    payload=build_project_payload(mix, stems, reference)
    root=os.path.join(folder,"ChatGPT_Mix_Analysis")
    stems_dir=os.path.join(root,"stems")
    os.makedirs(stems_dir, exist_ok=True)
    with open(os.path.join(root,"MIX_ANALYSIS.json"),"w",encoding="utf-8") as f:
        json.dump(payload,f,indent=2,ensure_ascii=False,allow_nan=False)
    for path,data in stems.items():
        if not isinstance(data,dict) or "error" in data: continue
        name=os.path.splitext(os.path.basename(path))[0] or "stem"
        safe="".join(c if c.isalnum() or c in " _-" else "_" for c in name).strip() or "stem"
        with open(os.path.join(stems_dir,safe+".json"),"w",encoding="utf-8") as f:
            json.dump(data,f,indent=2,ensure_ascii=False,allow_nan=False)
    with open(os.path.join(root,"CHATGPT_PROMPT.md"),"w",encoding="utf-8") as f:
        f.write(PROMPT)
    zip_path=os.path.join(folder,"ChatGPT_Mix_Analysis.zip")
    with zipfile.ZipFile(zip_path,"w",zipfile.ZIP_DEFLATED) as z:
        for base,_,files in os.walk(root):
            for fn in files:
                full=os.path.join(base,fn)
                z.write(full,os.path.relpath(full,folder))
    return zip_path,root
