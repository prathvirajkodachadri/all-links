import numpy as np

def compare_spectral_masking(a, b, sr):
    """Heuristic stem-overlap report. It identifies overlap, not guaranteed audible masking."""
    sa=a['spectrum']; sb=b['spectrum']; fa=np.asarray(sa['frequencies_hz']); ma=np.asarray(sa['magnitude']); mb=np.asarray(sb['magnitude'])
    n=min(len(fa),len(mb)); fa=fa[:n]; ma=ma[:n]; mb=mb[:n]; band=(fa>=20)&(fa<=20000)
    if not band.any(): return {'overlap_score':0.0,'bands':[]}
    x=ma[band]/(ma[band].max()+1e-12); y=mb[band]/(mb[band].max()+1e-12); overlap=float(np.mean(np.minimum(x,y)))
    ranges=[(20,60,'sub-bass'),(60,150,'bass'),(150,400,'low-mid'),(400,2000,'mid'),(2000,5000,'upper-mid'),(5000,10000,'presence'),(10000,20000,'high')]
    bands=[]
    for lo,hi,name in ranges:
        m=(fa[band]>=lo)&(fa[band]<hi)
        if m.any():
            v=float(np.mean(np.minimum(x[m],y[m])))
            if v>.18: bands.append({'band':name,'range_hz':[lo,hi],'overlap_score':round(v,3)})
    return {'overlap_score':round(overlap,3),'bands':bands,'note':'Overlap is a hypothesis; verify by listening and with solo/mute checks.'}

def project_masking(results):
    items=[(p,d) for p,d in results.items() if d and 'error' not in d]
    out=[]
    for i,(pa,da) in enumerate(items):
        for pb,db in items[i+1:]:
            r=compare_spectral_masking(da,db,da['file']['sample_rate'])
            if r['overlap_score']>.16: out.append({'track_a':da['file']['filename'],'track_b':db['file']['filename'],**r})
    return out
