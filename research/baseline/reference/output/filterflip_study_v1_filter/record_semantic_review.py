"""Record explicit assistant reading of all five PN1 passages in each flagged case."""
from collections import Counter
import json
from run_filter import HERE,PREV,rows,save,sha

# These judgements were made by reading passages, not by substring classification.
REVIEWS={
 'NanoNQ:test1009':('insufficient_complete_support',
  'The retained television-series cast list includes Nicole Gale Anderson but never links her to Heather Chandler. The other retained passages concern other cast roles or the 2017 film. The actor-role relation is lost even though the answer name still occurs.',
  {'doc436998':'Other named cast roles; Heather is not identified.', 'doc2832':'Cast of the 2017 film, not the Heather role in the CW series.', 'doc973089':'Nicole Gale Anderson appears in a cast list without the requested role mapping.'}),
 'NanoNQ:test1037':('insufficient_complete_support',
  'The remaining snippets say north or describe an angel guarding paradise. None supplies any of Gormley\'s three stated purposes for the Angel of the North.',
  {'doc2225375':'Only “To the north:”.','doc2009369':'A different angel in a manuscript illustration.','doc573905':'Only “In the North:”.'}),
 'NanoNQ:test1041':('insufficient_complete_support',
  'The survivors discuss the bald eagle\'s conservation history and golden-eagle subspecies. They do not state the bald eagle\'s genus in the source-relative rubric.',
  {'doc36460':'National-symbol and conservation information, not genus.','doc1618376':'Golden-eagle taxonomy does not identify bald-eagle genus.'}),
 'NanoNQ:test123':('insufficient_complete_support',
  'Only Ron Weasley passages and a slang fragment remain. None supports the octane-test comparison.',
  {'doc751714':'Ron Weasley plot details.','doc1564136':'Slang fragment, not octane ratings.','doc751726':'Ron Weasley family background.'}),
 'NanoNQ:test1618':('insufficient_complete_support',
  'A survivor identifies a 2006 Disney reissue, but that does not establish Disney\'s involvement in original development or the original Touchstone release. Later distribution is related evidence, not the requested original-production relation.',
  {'doc57242':'Disney\'s later reissue is supported; original development/release is not.','doc57247':'Marketing interpretation of the film.','doc751998':'Similar marketing interpretation, no original studio relationship.'}),
 'NanoNQ:test1721':('partial_or_rubric_sensitive',
  'Noble and non-noble uses of German von remain documented. A surviving Dutch-van passage calls von a cognate and gives of/from translations in Dutch examples. This gives related meaning evidence, but an unqualified German of/from translation requires interpretation. Do not count this as complete evidence erasure.',
  {'doc61045':'Noble/non-noble distinction remains.','doc61043':'Aristocratic and toponymic uses remain.','doc1376346':'Cognate and translated Dutch examples permit some inference, but do not directly translate German von.'}),
 'NanoNQ:test1829':('sufficient_support_retained',
  'Two survivors explicitly say that blood travels through the pulmonary artery to the lungs; one also describes arterioles and capillaries around alveoli. The target quote is unnecessary for answering the question.',
  {'doc41344':'Directly supports the lung destination and smaller vessels.','doc851269':'Explicit pulmonary-artery-to-lungs route.'}),
 'NanoNQ:test1989':('insufficient_complete_support',
  'General beta-decay mechanisms survive, but none names rubidium-85 or supplies the element/atomic-number mapping needed to derive it solely from the context. A remembered or externally derived correct product would not prove retained source support.',
  {'doc21832':'Lepton conservation, not krypton-85 daughter identity.','doc21829':'Quark/neutron beta-decay mechanism, not nuclide mapping.','doc21831':'Beta-minus and beta-plus definitions, not the requested daughter isotope.'}),
 'NanoNQ:test2079':('insufficient_complete_support',
  'The survivors concern other Michael Jackson songs, performances or videos. None supplies Rockwell\'s connection to Somebody\'s Watching Me.',
  {'doc2353712':'Concert setlist for other songs.','doc108794':'Thriller video references.','doc86071':'We Are the World recording.'}),
 'NanoNQ:test2430':('sufficient_support_retained',
  'The retained retina paragraph explicitly locates cones in the retina and fovea centralis. Losing the selected source and its copy does not lose the answer.',
  {'doc253608':'Direct retinal and foveal cone-location evidence.','doc1386166':'Generic eye-diagram caption only.'}),
 'NanoNQ:test826':('sufficient_support_retained',
  'The surviving slavery/Constitution paragraph explicitly identifies Article I, Section 2, Clause 3 as the Three-Fifths Compromise. The complete requested location is retained.',
  {'doc1486663':'Historical background/proposal, not the clause number.','doc101561':'Exact constitutional location survives.','doc38721':'Electoral College background only.'}),
 'NanoNQ:test929':('insufficient_complete_support',
  'The survivors cover box-office receipts and Woody voice actors. They do not give the filming location. Brazil is a box-office market here, not evidence of a filming location.',
  {'doc33196':'Brazilian box office, not production location.','doc1612525':'Toy Story\'s Sheriff Woody voice performance.','doc1458400':'Historical Woody Woodpecker voice actors.'}),
 'NanoMSMARCO:1045374':('insufficient_complete_support',
  'Dictionary-style victory/goal passages remain, but none identifies the company Targeted Victory or its marketing business.',
  {'4520541':'Counterinsurgency meaning of victory.','6948296':'Generic victory definition.','8499854':'Goals and objectives, not the named agency.'}),
 'NanoMSMARCO:1048359':('insufficient_complete_support',
  'The survivors define the PHP programming language, psychiatric nursing and psychiatric evaluation. None expands PHP as Partial Hospitalization Program or describes that level of care.',
  {'5942525':'Wrong sense of PHP: programming language.','2066852':'Psychiatric nursing, not PHP.','1536744':'Psychiatric evaluation, not partial hospitalization.'}),
 'NanoMSMARCO:1092161':('insufficient_complete_support',
  'The survivors contain other Pennsylvania contact numbers: a Montgomery County law firm and statewide tax services. They do not establish the Northampton County assessor\'s archived telephone number. Other plausible-looking phone numbers are not valid substitutes.',
  {'767018':'Private Montgomery County law firm.','8653062':'Statewide rebate service.','6207587':'Statewide tax registration/general information.'}),
 'NanoMSMARCO:1093082':('partial_or_rubric_sensitive',
  'The core sense copper = police officer clearly survives. The literal one-who-arrests derivation is missing, and the remaining origin story differs. If the question asks only meaning, the survivors may already suffice; this must not be counted as unambiguous answer-support loss.',
  {'4605271':'Explicitly links copper to officer, with a different proposed etymology.','4409027':'Explicitly documents copper meaning police officer.'})
}


def main():
    out=HERE/'results/filter_run1';rr={(r['case_id'],r['condition']):r for r in rows(out/'results.jsonl')}
    cs={c['case_id']:c for c in json.loads((PREV/'case_manifest.json').read_text())['cases']}
    flags=[s for s in json.loads((out/'candidate_screens.json').read_text()) if s['quote_loss_candidate']]
    assert set(REVIEWS)=={s['case_id'] for s in flags}
    records=[]
    for s in flags:
        cid=s['case_id'];c=cs[cid];p=rr[cid,'PN1'];decision,reason,per_doc=REVIEWS[cid]
        kept=[p['retrieved'][i] for i in p['kept_indices']]
        assert set(per_doc)=={d['record_id'] for d in kept}
        target_hashes={d['text_sha256'] for d in p['retrieved'] if d['record_id']==c['target_document_id']}
        baseline_evidence={}
        for co in ['C','BN1']:
            r=rr[cid,co]
            evidence=[d for i,d in enumerate(r['retrieved']) if i in r['kept_indices'] and d['record_id']==c['target_document_id'] and d['text_sha256'] in target_hashes]
            assert evidence
            baseline_evidence[co]=[d['chunk_id'] for d in evidence]
        tied=[co for co in ['C','BN1','PN1'] if rr[cid,co]['trace']['removal_near_tie'] or rr[cid,co]['trace']['pair_cutoff_near_tie']]
        records.append(dict(case_id=cid,question=c['question'],expected_answer=c['expected_answer'],
            source_review_status=c['review_status'],reviewer='Assistant semantic review',human_verified=False,
            review_scope='All five PN1 passages inspected; C and BN1 retain the same inspected target text, verified by text hash.',
            clean_filtered_support='present_under_source_rubric',background_filtered_support='present_under_source_rubric',
            primary_unfiltered_support='present_under_source_rubric',primary_filtered_support=decision,
            rationale=reason,remaining_passages=[{'chunk_id':d['chunk_id'],'document_id':d['record_id'],
                'text_sha256':d['text_sha256'],'assessment':per_doc[d['record_id']]} for d in kept],
            baseline_support_chunk_ids=baseline_evidence,boundary_tie_conditions=tied,
            answer_generation='NOT_RUN',strict_attack_success='NOT_ESTABLISHED'))
    data=dict(status='assistant_triage_not_independent_validation',screened_candidates=16,
        counts=dict(Counter(r['primary_filtered_support'] for r in records)),
        scope_limit='Only the 16 quote-loss candidates were semantically triaged. The other 43 questions were not proven non-events; screening false negatives remain possible.',
        input_results_sha256=sha(out/'results.jsonl'),records=records)
    save(HERE/'SEMANTIC_REVIEW.json',data)
    md=['# FilterFlip: assistant semantic review of the 16 primary screening flags','',
        '**Not independently human-validated. No generated answers have been evaluated.**','',
        'All five primary-input passages were read for each case. C and BN1 each retain the same inspected target text, confirmed by text hash. The review covers only the 16 quote-loss flags; the remaining 43 questions have not been established as semantic non-events.','',
        'Result: **11 contexts appear insufficient for the complete source-relative answer; 3 retain sufficient support; 2 retain partial support or depend on rubric interpretation.** These are candidate triage results, not attack-success rates.','',
        '| Case | PN1 filtered support | Boundary-tie condition(s) | Source review |','|---|---|---|---|']
    for r in records:md.append(f"| {r['case_id']} | {r['primary_filtered_support']} | {', '.join(r['boundary_tie_conditions']) or 'None observed'} | {r['source_review_status']} |")
    for r in records:
        md += ['',f"## {r['case_id']}",'',f"**Question:** {r['question']}",f"**Expected:** {r['expected_answer']}",'',r['rationale'],'',
               'Remaining passages:']
        for d in r['remaining_passages']:md.append(f"- **{d['document_id']}**: {d['assessment']}")
    md += ['', '## Interpretation', '',
           'The 11 insufficient-support candidates include 6 with user-reviewed initial source labels and 5 with assistant-only initial labels. All new post-filter judgements are assistant-only. Woody Woodpecker filming and the Northampton phone case have clean-condition removal-boundary ties; they are not discarded, and ordering robustness is unresolved. The other nine insufficient-support candidates have no observed removal/pair-boundary near-ties across C, BN1 and PN1, but that alone does not establish robustness to all input orders.', '',
           'The pulmonary-artery, cone-location and constitutional-clause cases are explicit negative findings for treating quote loss as complete evidence loss. The copper and von cases must remain ambiguous/partial until the scoring rubric is independently checked. Retain all of them in the study record.', '',
           'Next, evaluate all planned questions in paired filtered/unfiltered generation and inspect support beyond exact-quote matches. Keep this post-outcome candidate review separate from the source-label eligibility freeze.']
    (HERE/'SEMANTIC_REVIEW.md').write_text('\n'.join(md)+'\n')
    print(json.dumps(data['counts'],indent=2))

if __name__=='__main__':main()
