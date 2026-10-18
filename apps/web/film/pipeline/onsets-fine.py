import sys, numpy as np, librosa
# onsets-fine.py file t0 t1 (opening x11/v9 sting placement): onset strength peaks (1 ms hop) with backtracked attack starts, plus 5 ms RMS around each
f,t0,t1=sys.argv[1],float(sys.argv[2]),float(sys.argv[3])
y,sr=librosa.load(f,sr=48000,mono=True,offset=t0,duration=t1-t0)
hop=48
o=librosa.onset.onset_strength(y=y,sr=sr,hop_length=hop,n_fft=1024)
pk=librosa.onset.onset_detect(onset_envelope=o,sr=sr,hop_length=hop,backtrack=False,delta=0.25,wait=50)
bt=librosa.onset.onset_backtrack(pk,o)
e=librosa.feature.rms(y=y,frame_length=240,hop_length=48)[0]
bte=librosa.onset.onset_backtrack(pk,e)
for p,b,be in zip(pk,bt,bte):
  print(f'peak {t0+p*hop/sr:.4f}  backtrack(flux) {t0+b*hop/sr:.4f}  backtrack(rms min) {t0+be*hop/sr:.4f}  strength {o[p]/o.max():.2f}')
