"""Synthetic XSS fixture on a separate port. Never invokes a model or research worker."""
import sys
from pathlib import Path
from unittest.mock import Mock,patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import server
if __name__=='__main__':
    marker='SYNTHETIC SECURITY TEST <img src="/xss-probe" onerror="document.body.dataset.xss=\'executed\'"> <script>alert(1)</script>'
    m=Mock();m.active='c'*32;m.cases={'synthetic':{'case_id':'synthetic','question':marker}};m.benign=set();m.approved=set();m.qualifications={}
    m.start.side_effect=RuntimeError('Synthetic fixture only; no generation')
    m.snapshot.return_value={'effective_status':'completed','state':{'case_id':'synthetic','mode':'variants','condition':'C','status':'completed','kind':'SYNTHETIC SECURITY TEST'},'events':[],
      'result':{'status':'completed','conditions':{'C':{'retrieved':[{'text':marker,'record_id':'synthetic'}],
        'policies':{'U':{'kept':[0],'representatives':[0],'singleton_bypass':False}},
        'answers':{'U':{'text':marker,'status':'synthetic','seconds':0}}}}}}
    with patch.object(server,'Manager',return_value=m):s=server.Server('unused',8781)
    try:s.serve_forever()
    finally:s.server_close()
