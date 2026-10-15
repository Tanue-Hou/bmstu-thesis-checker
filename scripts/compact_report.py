"""Bound large evidence/location arrays without changing findings or decisions."""
from copy import deepcopy


def project_report(report, detail='full'):
    if detail not in {'full','compact'}:
        raise ValueError('detail must be full or compact')
    if detail=='full':
        return report
    result=deepcopy(report)
    for finding in result.get('findings',[]):
        refs=finding.get('evidence_refs',[])
        finding['evidence_ref_count']=len(refs)
        finding['evidence_refs_truncated']=len(refs)>1
        finding['evidence_refs']=refs[:1]
        precise=finding.get('precise_locations')
        if precise is not None:
            examples=precise.get('occurrences',[])
            precise['source_sample_limit']=precise.get('limit')
            precise['occurrences']=examples[:3]
            precise['truncated']=bool(precise.get('truncated') or len(examples)>3)
            precise['limit']=3
    paragraphs=result.get('native_paragraph_observations',{})
    examples=paragraphs.get('native_paragraph_records')
    if examples is not None:
        paragraphs['native_paragraph_records']=examples[:3]
        paragraphs['records_truncated']=bool(paragraphs.get('records_truncated') or len(examples)>3)
    result['output_detail']={'level':'compact','complete_findings_list':True,
        'location_examples_per_finding':3,'evidence_refs_per_finding':1,
        'expand_with':'Request detail=full for all retained evidence references and location samples.'}
    return result
