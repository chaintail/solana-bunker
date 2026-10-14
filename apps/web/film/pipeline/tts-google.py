import json,base64,sys,urllib.request
from google.oauth2 import service_account
import google.auth.transport.requests
c=service_account.Credentials.from_service_account_file('/home/claude/.secrets/gcp-tts-sa.json',scopes=['https://www.googleapis.com/auth/cloud-platform']); c.refresh(google.auth.transport.requests.Request())
name,lang,out=sys.argv[1:4]; ssml=sys.argv[4]
body={"input":{"ssml":ssml},"voice":{"languageCode":lang,"name":name},"audioConfig":{"audioEncoding":"LINEAR16","sampleRateHertz":24000}}
req=urllib.request.Request("https://texttospeech.googleapis.com/v1/text:synthesize",data=json.dumps(body).encode(),headers={"Authorization":"Bearer "+c.token,"Content-Type":"application/json"})
try: open(out,"wb").write(base64.b64decode(json.load(urllib.request.urlopen(req))["audioContent"]))
except urllib.error.HTTPError as e: print(e.read().decode()); sys.exit(1)
print('ok',out)
