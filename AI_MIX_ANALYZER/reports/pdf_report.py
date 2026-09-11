from pathlib import Path

def _esc(s): return str(s).replace('\\','\\\\').replace('(','\\(').replace(')','\\)')
def export_pdf(data, path, recommendations=None):
    f=data['file']; l=data['loudness']; t=data['true_peak']; q=data['quality']; s=data['stereo']
    lines=['AI AUDIO MIXING & MASTERING ANALYZER','ANALYSIS REPORT','',f"File: {f['filename']}",f"Duration: {f['duration_s']:.2f} seconds",f"Sample rate: {f['sample_rate']} Hz   Channels: {f['channels']}",'','CORE MEASUREMENTS',f"Integrated loudness: {l['integrated_lufs']:.2f} LUFS",f"Short-term loudness: {l['short_term_lufs']:.2f} LUFS",f"Loudness range: {l['lra']:.2f} LU",f"True peak: {t['dbtp']:.2f} dBTP",f"RMS: {q['rms_db']:.2f} dBFS",f"Crest factor: {q['crest_factor_db']:.2f} dB",f"Stereo correlation: {s.get('correlation',1):.3f}",f"Stereo width: {s.get('width_db',0):.2f} dB",f"Clipped samples: {q['clipped_samples']}",'', 'AI-READY FINDINGS']
    for r in (recommendations or []): lines += [f"{r['severity'].upper()}: {r['problem']}",f"Evidence: {r['evidence']}",f"What to check: {r['what_to_check']}",f"Confidence: {r['confidence']}",'']
    if not recommendations: lines += ['No major evidence-based findings were generated.','']
    lines += ['DISCLAIMER','Measurements are decision-support evidence. Verify recommendations by listening and with trusted metering.']
    # split into pages at a conservative line count
    pages=[lines[i:i+48] for i in range(0,len(lines),48)]; contents=[]
    for page in pages:
        stream='BT /F1 10 Tf 48 770 Td 14 TL\n'
        for line in page: stream+=f'({_esc(line[:100])}) Tj T*\n'
        stream+='ET'; contents.append(stream)
    objs=['<< /Type /Catalog /Pages 2 0 R >>',None,'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>']; page_ids=[]
    for i,c in enumerate(contents): page_ids.append(4+i*2)
    objs[1]=f'<< /Type /Pages /Kids [{" ".join(str(x)+" 0 R" for x in page_ids)}] /Count {len(contents)} >>'
    for i,c in enumerate(contents): objs += [f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 3 0 R >> >> /Contents {5+i*2} 0 R >>',f'<< /Length {len(c.encode())} >>\nstream\n{c}\nendstream']
    out=b'%PDF-1.4\n'; offsets=[0]
    for n,o in enumerate(objs,1): offsets.append(len(out)); out+=f'{n} 0 obj\n{o}\nendobj\n'.encode()
    start=len(out); out+=f'xref\n0 {len(objs)+1}\n0000000000 65535 f \n'.encode()+b''.join(f'{x:010d} 00000 n \n'.encode() for x in offsets[1:]); out+=f'trailer\n<< /Size {len(objs)+1} /Root 1 0 R >>\nstartxref\n{start}\n%%EOF'.encode(); Path(path).write_bytes(out)
