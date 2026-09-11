from analyzer.chatgpt_package import build_project_payload


def sample(name, lufs=-14.0, rms=-18.0, peak=-1.5, corr=0.8):
    bands=[{"low_hz":20,"high_hz":40,"level_db":-30.0},{"low_hz":40,"high_hz":80,"level_db":-20.0}]
    return {
        "file":{"filename":name,"path":name,"duration_s":180.0,"sample_rate":48000,"channels":2},
        "loudness":{"integrated_lufs":lufs},
        "true_peak":{"dbtp":peak},
        "dynamics":{"rms":{"overall_dbfs":rms}},
        "spectrum":{"frequency_bands":bands},
        "stereo":{"correlation":{"overall":corr}},
        "quality":{"clipped_samples":0},
        "sections":[],
        "time_analysis":{}
    }


def test_chatgpt_payload_schema_and_reference():
    mix=sample("Mix.wav")
    stem=sample("Kick.wav")
    stem["role"]="Kick"
    ref=sample("Reference.wav",lufs=-12.0)
    payload=build_project_payload(mix,{"Kick.wav":stem},ref)
    assert payload["schema_version"] == "3.0"
    assert payload["schema_name"] == "AI_MIX_ANALYSIS_CHATGPT"
    assert payload["project"]["stem_count"] == 1
    assert payload["reference"]["present"] is True
    assert payload["reference_comparison"]["available"] is True
    assert payload["reference_comparison"]["metrics"]["integrated_lufs"]["difference"] == -2.0
    assert payload["stems"][0]["role"] == "Kick"
    assert "priority_actions" in payload["project_evidence"]
