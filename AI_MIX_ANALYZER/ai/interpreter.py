def interpret(r,target=-14):
    issues=[]; l=r['loudness']['integrated_lufs']; tp=r['true_peak']['dbtp']; q=r['quality']; st=r['stereo']
    def add(problem,evidence,severity,why,check,confidence): issues.append({'problem':problem,'evidence':evidence,'severity':severity,'why_it_may_matter':why,'what_to_check':check,'confidence':confidence})
    if tp>-1: add('True peak may be too high',f'{tp:.2f} dBTP','High','May cause codec or playback distortion','Check limiter ceiling and true-peak oversampling','High')
    if l>target+1: add('Master is above loudness target',f'{l:.1f} LUFS vs {target:.1f} LUFS','Medium','May reduce headroom and dynamic contrast','Review limiter/compression and loudness target','High')
    if q['clipped_samples']: add('Clipped samples detected',str(q['clipped_samples']),'High','Hard clipping can create audible distortion','Inspect timestamps and source gain staging','High')
    if st.get('correlation',1)<0: add('Potential phase incompatibility',f"Correlation {st['correlation']:.2f}",'High','Mono summing may cancel content','Check wide effects and low-frequency stereo','High')
    return issues
