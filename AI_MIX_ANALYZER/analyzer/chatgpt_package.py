"""Build an evidence-first package for manual ChatGPT mix review."""
import json
import os
import zipfile
from .project_analysis import analyze_project, priority_actions

PROMPT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "CHATGPT_MIX_REVIEW_PROMPT.txt")


def load_prompt():
    """Load the canonical prompt shipped with the analyzer repository."""
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()


def _clean_analysis(d):
    """Keep the complete deterministic analysis while making JSON intent explicit."""
    return d


def build_project_payload(mix, stems, reference=None):
    valid_stems = []
    for path, data in stems.items():
        if isinstance(data, dict) and "error" not in data:
            valid_stems.append({
                "file": os.path.basename(path),
                "role": data.get("role", "Other"),
                "analysis": _clean_analysis(data),
            })

    project = analyze_project(mix, stems, reference)
    project["priority_actions"] = priority_actions(mix, stems, project)

    return {
        "schema_version": "3.0",
        "schema_name": "AI_MIX_ANALYSIS_CHATGPT",
        "project": {
            "mix_file": os.path.basename(mix.get("file", {}).get("path", mix.get("file", {}).get("filename", ""))) if mix else None,
            "reference_file": os.path.basename(reference.get("file", {}).get("path", reference.get("file", {}).get("filename", ""))) if isinstance(reference, dict) and "error" not in reference else None,
            "stem_count": len(valid_stems),
        },
        "mix": {"measurements": _clean_analysis(mix)},
        "reference": {
            "present": isinstance(reference, dict) and "error" not in reference,
            "measurements": _clean_analysis(reference) if isinstance(reference, dict) and "error" not in reference else None,
        },
        "stems": valid_stems,
        "relationships": project.get("stem_relationships", {}),
        "mix_vs_stem": project.get("mix_vs_stem", []),
        "reference_comparison": project.get("reference_comparison", {"available": False}),
        "project_evidence": {
            "priority_actions": project.get("priority_actions", []),
            "summary": project.get("mix"),
            "methodology": project.get("methodology", {}),
        },
        "analysis_sections": {
            "mix_sections": mix.get("sections", []) if isinstance(mix, dict) else [],
            "mix_time_analysis": mix.get("time_analysis", {}) if isinstance(mix, dict) else {},
        },
        "ai_context": {
            "purpose": "Objective evidence package for manual upload to ChatGPT. The analyzer does not make creative mix decisions.",
            "interpretation": "Use the measurements to reason about priorities, then recommend changes conservatively.",
            "limitations": project.get("methodology", {}),
        },
    }


def _safe_stem_name(path):
    name = os.path.splitext(os.path.basename(path))[0] or "stem"
    return "".join(c if c.isalnum() or c in " _-" else "_" for c in name).strip() or "stem"


def export_chatgpt_package(folder, mix_path, mix, stems, reference_path=None, reference=None):
    """Export MIX_ANALYSIS.json, individual stem JSONs, the canonical prompt and a ZIP."""
    os.makedirs(folder, exist_ok=True)
    payload = build_project_payload(mix, stems, reference)
    prompt = load_prompt()

    root = os.path.join(folder, "ChatGPT_Mix_Analysis")
    stems_dir = os.path.join(root, "stems")
    os.makedirs(stems_dir, exist_ok=True)

    with open(os.path.join(root, "MIX_ANALYSIS.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False, allow_nan=False)

    used = set()
    for path, data in stems.items():
        if not isinstance(data, dict) or "error" in data:
            continue
        base = _safe_stem_name(path)
        name = base
        i = 2
        while name.lower() in used:
            name = f"{base}_{i}"
            i += 1
        used.add(name.lower())
        with open(os.path.join(stems_dir, name + ".json"), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, allow_nan=False)

    with open(os.path.join(root, "CHATGPT_MIX_REVIEW_PROMPT.txt"), "w", encoding="utf-8") as f:
        f.write(prompt)

    with open(os.path.join(root, "README_UPLOAD_TO_CHATGPT.txt"), "w", encoding="utf-8") as f:
        f.write(
            "AI MIX ANALYZER — CHATGPT PACKAGE\n\n"
            "Recommended upload order:\n"
            "1. CHATGPT_MIX_REVIEW_PROMPT.txt\n"
            "2. MIX_ANALYSIS.json\n"
            "3. Individual stem JSON files only if additional detail is needed.\n\n"
            "The prompt instructs ChatGPT to treat measurements as evidence, distinguish evidence from inference, "
            "and recommend conservative, evidence-driven mixing/mastering actions.\n"
        )

    zip_path = os.path.join(folder, "ChatGPT_Mix_Analysis.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for base, _, files in os.walk(root):
            for fn in files:
                full = os.path.join(base, fn)
                z.write(full, os.path.relpath(full, folder))

    return zip_path, root
