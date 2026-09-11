"""Manual, no-API exporter for a ChatGPT-ready mix evidence package.

Run from AI_MIX_ANALYZER with: python export_chatgpt.py
"""
import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from analyzer.chatgpt_package import export_chatgpt_package


def choose_json(title, multiple=False):
    fn = filedialog.askopenfilenames if multiple else filedialog.askopenfilename
    return fn(title=title, filetypes=[("JSON files", "*.json"), ("All files", "*.*")])


def main():
    root = tk.Tk(); root.withdraw()
    mix_path = choose_json("Select MIX JSON")
    if not mix_path: return
    mix_path = mix_path if isinstance(mix_path, str) else mix_path[0]
    stem_paths = choose_json("Select STEM JSON files", multiple=True)
    if not stem_paths:
        messagebox.showwarning("Stems required", "Select at least one stem JSON file.")
        return
    reference_path = choose_json("Select REFERENCE JSON (Cancel for none)")
    try:
        with open(mix_path, encoding="utf-8") as f: mix = json.load(f)
        stems = {}
        for p in stem_paths:
            with open(p, encoding="utf-8") as f: stems[p] = json.load(f)
        reference = None
        if reference_path:
            with open(reference_path, encoding="utf-8") as f: reference = json.load(f)
        folder = filedialog.askdirectory(title="Choose ChatGPT package output folder")
        if not folder: return
        zip_path, package_dir = export_chatgpt_package(folder, mix_path, mix, stems, reference_path, reference)
        messagebox.showinfo("ChatGPT package ready", f"Package created:\n\n{package_dir}\n\nZIP:\n{zip_path}")
    except Exception as exc:
        messagebox.showerror("Export failed", f"{type(exc).__name__}: {exc}")
    finally:
        root.destroy()


if __name__ == "__main__":
    main()
