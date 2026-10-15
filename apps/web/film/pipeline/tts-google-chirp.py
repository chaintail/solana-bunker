import json,base64,sys,urllib.request
from google.oauth2 import service_account
import google.auth.transport.requests
# Chirp 3 HD: plain text / markup (no SSML). usage: tts-google-chirp.py <voice> <lang> <out.wav> <text> [markup]
c=service_account.Credentials.from_service_account_file('/home/claude/.secrets/gcp-tts-sa.json',scopes=['https://www.googleapis.com/auth/cloud-platform']); c.refresh(google.auth.transport.requests.Request())
name,lang,out,text=sys.argv[1:5]; mode=sys.argv[5] if len(sys.argv)>5 else 'text'
body={"input":{mode:text},"voice":{"languageCode":lang,"name":name},"audioConfig":{"audioEncoding":"LINEAR16","sampleRateHertz":24000}}
req=urllib.request.Request("https://texttospeech.googleapis.com/v1beta1/text:synthesize",data=json.dumps(body).encode(),headers={"Authorization":"Bearer "+c.token,"Content-Type":"application/json"})
try: open(out,"wb").write(base64.b64decode(json.load(urllib.request.urlopen(req))["audioContent"]))
except urllib.error.HTTPError as e: print(e.read().decode()); sys.exit(1)
print('ok',out)
