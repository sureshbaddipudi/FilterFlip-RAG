import http.client,json
H='127.0.0.1:8772'
def req(method,path,body=None,headers=None,raw=None):
    c=http.client.HTTPConnection('127.0.0.1',8772,timeout=10)
    h={'Host':H}; h.update(headers or {})
    c.putrequest(method,path,skip_host=True,skip_accept_encoding=True)
    for k,v in h.items(): c.putheader(k,v)
    data=raw if raw is not None else (json.dumps(body).encode() if body is not None else b'')
    if method=='POST' and 'Content-Length' not in h: c.putheader('Content-Length',str(len(data)))
    c.endheaders(data)
    r=c.getresponse(); b=r.read(); return r.status,dict(r.getheaders()),b
s,h,b=req('GET','/api/bootstrap'); boot=json.loads(b); tok=boot['token']
cases=boot['cases']; trust=[c for c in cases if c['trust']]
print('bootstrap',s,'cases',len(cases),'trust flagged',len(trust))
print('trust questions',[c['question'][:30] for c in trust][:12])
P={'X-Run-Token':tok,'Content-Type':'application/json'}
def post(label,body,headers=P,raw=None):
    s,h,b=req('POST','/api/runs',body,headers,raw); print(f'{s}  {label}  {b[:90].decode(errors="replace")}')
tc=trust[0]['id']; nt=[c['id'] for c in cases if not c['trust']][0]
post('trust, case outside panel',{'mode':'trust','case_id':nt,'condition':'C'})
post('trust, condition BN2',{'mode':'trust','case_id':tc,'condition':'BN2'})
post('trust, condition PN1 lowercase',{'mode':'trust','case_id':tc,'condition':'pn1'})
post('trust, condition list',{'mode':'trust','case_id':tc,'condition':['C']})
post('trust, unknown extra field',{'mode':'trust','case_id':tc,'condition':'C','policy':'T'})
post('trust, case_id traversal',{'mode':'trust','case_id':'../../etc/passwd','condition':'C'})
post('trust, case_id huge',{'mode':'trust','case_id':'A'*900,'condition':'C'})
post('mode unknown',{'mode':'trust2','case_id':tc,'condition':'C'})
post('no token',{'mode':'trust','case_id':tc,'condition':'C'},{'Content-Type':'application/json'})
post('bad token',{'mode':'trust','case_id':tc,'condition':'C'},{'X-Run-Token':'x','Content-Type':'application/json'})
post('wrong content-type',{'mode':'trust','case_id':tc,'condition':'C'},{'X-Run-Token':tok,'Content-Type':'text/plain'})
post('body over 1024',None,P,raw=b'{"a":"'+b'x'*1100+b'"}')
post('not json',None,P,raw=b'{not json')
post('json array',None,P,raw=b'[1,2]')
post('null bytes',None,P,raw=b'{"mode":"trust","case_id":"\\u0000","condition":"C"}')
post('bad Origin',{'mode':'trust','case_id':tc,'condition':'C'},dict(P,Origin='http://evil.example'))
post('bad Host',{'mode':'trust','case_id':tc,'condition':'C'},dict(P,Host='evil.example:8772'))
post('Sec-Fetch-Site cross-site',{'mode':'trust','case_id':tc,'condition':'C'},dict(P,**{'Sec-Fetch-Site':'cross-site'}))
for p in ('/api/project','/api/findings','/semester-report.pdf','/project.js','/documents/semester-report.pdf','/../app/server.py','/%2e%2e/server.py','/api/runs/../../config.local.json','/trust_profile.json','/data/trust_contexts.json'):
    s,h,b=req('GET',p); print(f'GET {p} -> {s} {h.get("Content-Type")} len={len(b)}')
s,h,b=req('GET','/semester-report.pdf'); print({k:v for k,v in h.items() if k.lower() in ('content-security-policy','x-content-type-options','x-frame-options','cache-control','cross-origin-resource-policy')}); print(b[:5])
print('active after tests:',json.loads(req('GET','/api/bootstrap')[2])['active'])
