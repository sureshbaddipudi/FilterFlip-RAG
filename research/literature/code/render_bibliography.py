#!/usr/bin/env python3
"""Render the inspected reference editions; no network, model or source edits."""
from pathlib import Path
import argparse,json
P=Path(__file__).resolve().parent.parent

def escape(value):
 mapping={'\\':r'\textbackslash{}','{':r'\{','}':r'\}','&':r'\&','%':r'\%','#':r'\#','$':r'\$','_':r'\_','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}
 return ''.join(mapping.get(c,c) for c in ' '.join(str(value).split()))
def render(rows):
 entries=['% FilterFlip Task 10: inspected editions, as of 2026-11-01.\n% Metadata/formatting only; this bibliography does not establish novelty.\n']
 for r in rows:
  id=r['paper_id'];kind='inproceedings' if id in ['R14','R15'] else 'misc';fields={'author':' and '.join(escape(a) for a in r['authors']),'title':'{'+escape(r['title'])+'}','year':r['citation_year']}
  if id=='R14':fields.update(booktitle='Proceedings of the 2026 Conference on Empirical Methods in Natural Language Processing',pages='12549--12575',doi='10.18653/2026.emnlp-main.546',url=r['publication_record_url'],note='Published PDF inspected; arXiv 2608.23965v1 metadata cross-checked')
  elif id=='R15':fields.update(booktitle='Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)',pages='4609--4631',doi='10.18653/v1/2025.acl-long.230',url=r['publication_record_url'],note='Published PDF inspected')
  else:
   fields.update(eprint=r['arxiv_id'],archivePrefix='arXiv',url=r['record_url'],note=escape('Inspected v'+str(r['inspected_version'])+' dated '+r['inspected_version_date']+'. '+r['publication_status']))
  entries.append('@'+kind+'{filterflip_'+id.lower()+',\n'+',\n'.join('  '+k+' = {'+v+'}' for k,v in fields.items())+'\n}\n')
 return '\n'.join(entries)
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();rows=json.loads((P/'PAPER_REGISTRY.json').read_text())
 with a.out.open('x') as f:f.write(render(rows))
 print('Rendered',len(rows),'references without changing source records')
if __name__=='__main__':main()
