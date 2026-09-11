import csv, json
from reports.structured_csv import export_section_csv, export_stereo_csv, export_time_history_csv

def test_structured_exports(tmp_path):
 d={'loudness':{'momentary':{'history':[{'time_s':0.1,'lufs':-12.3}]},'short_term':{'history':[]}},'dynamics':{'rms':{'history':[{'time_s':0.1,'rms_dbfs':-18.2,'crest_factor_db':10.1}]}},'spectrum':{'history':[{'time_s':0.1,'centroid_hz':1200}]},'stereo':{'correlation':{'history':[{'time_s':0.1,'correlation':.7,'mid_rms_dbfs':-18,'side_rms_dbfs':-25}]}},'time_analysis':{'detailed_sections':{'sections':[]}}}
 for fn in (export_section_csv,export_stereo_csv,export_time_history_csv):
  p=tmp_path/(fn.__name__+'.csv'); fn(d,p); assert p.exists(); list(csv.DictReader(open(p)))
