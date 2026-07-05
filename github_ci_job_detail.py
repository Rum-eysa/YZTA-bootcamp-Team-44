import json
import urllib.request
repo='Rum-eysa/YZTA-bootcamp-Team-44'
job_id=84451054072
url=f'https://api.github.com/repos/{repo}/actions/jobs/{job_id}'
req=urllib.request.Request(url, headers={'User-Agent':'python-urllib','Accept':'application/vnd.github+json'})
with urllib.request.urlopen(req, timeout=30) as r:
    data=json.loads(r.read())
print(json.dumps(data, indent=2)[:5000])
