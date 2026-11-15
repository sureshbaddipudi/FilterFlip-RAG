"""Serve unchanged case evidence and original review records by catalog identity."""
from pathlib import Path
from safety import load, require, STUDY_CONDITIONS
ROOT=Path(__file__).resolve().parent

def load_study(case_id):
    catalog=load(ROOT/'data/STUDY_CATALOG.json')
    require(isinstance(case_id,str) and case_id in catalog,'Unknown study case')
    item=catalog[case_id]
    # Paths originate only from the sealed catalog, never browser parameters.
    for value in item.values():
        require(not Path(value).is_absolute() and '..' not in Path(value).parts,'Invalid study path')
    packet=load(ROOT/'data'/item['case'])
    review=load(ROOT/'data'/item['review'])
    require(packet['case']['case_id']==case_id==review['case_id'],'Study identity mismatch')
    require(set(packet['conditions'])==set(STUDY_CONDITIONS),'Incomplete condition inventory')
    return {'case':packet['case'],'conditions':packet['conditions'],'review_records':review['records'],
            'primary_review_summary':packet['current_primary_review_summary'],
            'source_files':item,'kind':'recorded_study_evidence',
            'notice':'Saved reference and later reproduction answers, never fresh model output. Task-7 records retain their original attribution; Suresh agreed separately. Missing review fields stay missing.'}
