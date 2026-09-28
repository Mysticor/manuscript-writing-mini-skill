"""Mechanical Stage 2 gates. Scientific judgment and prose belong to the Agent."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,csv,hashlib,json,re,shutil,sys,tempfile
import yaml
SKILL=Path(__file__).resolve().parents[1]
M=yaml.safe_load((SKILL/'manifest.yaml').read_text())
REQUIRED=['README.md','readiness.json','01_target_journal_profile.md','02_research_story_facts.md','03_claim_registry.yaml','04_results_facts.csv','05_methods_fact_sheet.yaml','06_data_fact_sheet.yaml','07_statistics_fact_sheet.yaml','08_literature_canon.md','09_claim_reference_map.csv','10_key_paper_exemplars.md','references.bib','11_asset_inventory.csv','12_table_ready_data_inventory.md','13_supplementary_evidence_candidates.md','14_limitations_boundary_conditions.md','15_terminology_ledger.yaml','16_ethics_data_code_availability.md','17_unresolved_items.md','18_author_input_needed.md']
OPTIONAL=['literature_visual_inventory.csv','literature_table_inventory.csv','literature_formula_inventory.csv']
STATES={'DRAFT_IN_PROGRESS','DRAFT_COMPLETE_WITH_AUTHOR_CHECKS','MANUSCRIPT_DRAFT_READY','BLOCKED'}
# Shared project coordination; stage logic remains local.
import sys as _coord_sys
_coord_sys.path.insert(0,str(Path(__file__).resolve().parents[4]/'workflow-contract'))
import project_contract as _coord

def now():return datetime.now(timezone.utc).isoformat()
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read_json(p):return json.loads(Path(p).read_text())
def write_json(p,d):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w',dir=p.parent,delete=False,encoding='utf-8') as f:json.dump(d,f,ensure_ascii=False,indent=2);tmp=Path(f.name)
    tmp.replace(p)
def rows(p):
    with Path(p).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def path(root,value):
    if not value or Path(value).is_absolute() or '..' in Path(value).parts:raise ValueError('Expected root-relative file: '+str(value))
    root=Path(root).resolve();p=(root/value).resolve()
    if not p.is_relative_to(root) or not p.is_file():raise ValueError('Missing/external file: '+str(value))
    return p

def state(root):return read_json(Path(root)/'state.json')
def state_errors(s):
    template=read_json(SKILL/'templates/state.json');errors=['Missing state '+k for k in template if k not in s]
    if type(s.get('current_phase'))!=int or s['current_phase'] not in range(10):errors.append('Invalid phase')
    if s.get('paper_type') not in M['paper_types']:errors.append('Invalid paper type')
    if s.get('draft_readiness') not in STATES:errors.append('Invalid draft readiness')
    for k in ['unresolved_items','author_decisions']:
        if not isinstance(s.get(k),list):errors.append('Invalid state list '+k)
    return errors

def save(root,s):
    errors=state_errors(s)
    if errors:raise ValueError('; '.join(errors))
    s['last_updated']=now();write_json(Path(root)/'state.json',s)
def filled(p):return Path(p).is_file() and bool(Path(p).read_text().strip()) and not re.search(r'\[TO_COMPLETE\]|Status: UNFILLED',Path(p).read_text(),re.I)

def init(root,handoff,paper_type,test_only=False,input_map=None):
    root=Path(root).resolve();handoff=Path(handoff).resolve()
    if root.exists():raise FileExistsError('Use state/resume; manuscript directory already exists')
    if root==handoff or root.is_relative_to(handoff):raise ValueError('Do not write manuscript inside original handoff')
    if not handoff.is_dir():raise FileNotFoundError(str(handoff))
    for p in handoff.rglob('*'):
        if p.is_symlink():raise ValueError('Handoff symlinks require explicit materialization before import')
    if paper_type not in M['paper_types']:raise ValueError('Invalid paper type')
    for canonical,source in (input_map or {}).items():
        if canonical not in REQUIRED+OPTIONAL:raise ValueError('Unknown canonical input: '+canonical)
        src=path(handoff,source)
        if (handoff/canonical).exists() and src!=handoff/canonical:raise FileExistsError(canonical)
    shutil.copytree(SKILL/'templates',root)
    snapshot=root/'inputs/handoff';snapshot.parent.mkdir(parents=True);shutil.copytree(handoff,snapshot)
    mapping=input_map or {}
    for canonical,source in mapping.items():
        if canonical not in REQUIRED+OPTIONAL:raise ValueError('Unknown canonical input: '+canonical)
        src=path(snapshot,source);dest=snapshot/canonical
        if dest.exists() and src!=dest:raise FileExistsError('Canonical input already exists: '+canonical)
        if src!=dest:shutil.copy2(src,dest)
    for d in ['figures/briefs','figures/source','figures/working','figures/final','tables/briefs','tables/source','tables/final','source_verification','checks','history']:(root/d).mkdir(parents=True,exist_ok=True)
    for name in ['references.bib','15_terminology_ledger.yaml']:
        if (snapshot/name).exists():shutil.copy2(snapshot/name,root/('terminology_ledger.yaml' if name.endswith('.yaml') else name))
    s=read_json(root/'state.json');s.update(project=root.name,manuscript_title_working=root.name,paper_type=paper_type,test_only=test_only,input_map=mapping,source_handoff=str(handoff))
    save(root,s)
    return intake(root)

def intake(root):
    root=Path(root);snap=root/'inputs/handoff';s=state(root);items=[];errors=[]
    for name in REQUIRED+OPTIONAL:
        exists=(snap/name).is_file();status='AVAILABLE' if exists else ('MISSING_BUT_NONBLOCKING' if name in OPTIONAL else 'BLOCKING')
        items.append({'item':name,'status':status})
        if status=='BLOCKING':errors.append('Missing input '+name)
    if (snap/'readiness.json').exists():
        r=read_json(snap/'readiness.json')
        if r.get('status')=='BLOCKED':errors.append('Stage 1 handoff blocked')
        if (r.get('test_only') or r.get('mock')) and not s['test_only']:errors.append('MOCK handoff cannot be production input')
    if (snap/'package_checksums.json').exists():
        for rel,h in read_json(snap/'package_checksums.json').items():
            if digest(path(snap,rel))!=h:errors.append('Input checksum mismatch: '+rel)
    if (snap/'03_claim_registry.yaml').exists() and (snap/'04_results_facts.csv').exists():
        claims=yaml.safe_load((snap/'03_claim_registry.yaml').read_text()).get('claims',[]) or []
        results={r['result_id']:r for r in rows(snap/'04_results_facts.csv')}
        if len(results)!=len(rows(snap/'04_results_facts.csv')):errors.append('Duplicate result IDs')
        central=[c for c in claims if str(c.get('importance','')).upper()=='CENTRAL']
        if not central:errors.append('No evidenced central claim')
        for c in central:
            support=c.get('supporting_result_ids',[]);lit=c.get('supporting_literature',[])
            review=s['paper_type'] in {'review','systematic_review','perspective'}
            if c.get('status')!='SUPPORTED' or not (support or (review and lit)):errors.append('Central claim lacks real evidence: '+c.get('claim_id',''))
            if review and lit and not support:
                for key in lit:
                    if not re.search(r'@\w+\s*[{(]\s*'+re.escape(key)+r'\s*,',(snap/'references.bib').read_text()):errors.append('Unresolved synthesis source '+key)
            for rid in support:
                r=results.get(rid)
                if not r or r.get('status')!='ACTUAL':errors.append('Central result absent/non-actual: '+rid);continue
                for k,hkey in [('source_file','source_sha256'),('analysis_script','analysis_sha256')]:
                    try:
                        p=path(snap,r.get(k,''))
                        if r.get(hkey) and digest(p)!=r[hkey]:errors.append('Result evidence changed: '+rid)
                    except ValueError as e:errors.append(str(e))
    report={'status':'BLOCKED' if errors else 'AVAILABLE','items':items,'blockers':errors,'checked_at':now()}
    write_json(root/'checks/intake.json',report)
    # Do not overwrite the Agent's substantive intake audit on resume.
    p=root/'manuscript_blueprint/00_intake_audit.md'
    if not filled(p):p.write_text('# Manuscript Intake — mechanical inventory\n\nStatus: UNFILLED\nAgent must audit core facts and boundaries, then read selected sources at use; inventory alone is not a scientific audit.\n\n'+ '\n'.join(f'- {i["item"]}: {i["status"]}' for i in items)+'\n\nBlockers: '+str(errors)+'\n')
    return report

def fingerprint(root,blueprint=False):
    root=Path(root).resolve();h=hashlib.sha256()
    folders=['manuscript_blueprint','figures/briefs','tables/briefs'] if blueprint else ['manuscript_blueprint','figures','tables','source_verification','inputs']
    files=[]
    for folder in folders:files += [p for p in (root/folder).rglob('*') if p.is_file() and p.name!='decision_log.md']
    if not blueprint:
        files += [root/n for n in ['manuscript.md','supplementary.md','references.bib','terminology_ledger.yaml','manuscript_asset_manifest.csv','numeric_trace.csv','claim_evidence_map.csv','section_registry.csv','unresolved_items.md','author_input_needed.md'] if (root/n).is_file()]
    else:files += [root/n for n in ['claim_evidence_map.csv','section_registry.csv'] if (root/n).exists()]
    for p in sorted(set(files)):
        h.update(str(p.relative_to(root)).encode())
        if blueprint and p.suffix=='.yaml':
            d=yaml.safe_load(p.read_text());d.pop('status',None);h.update(json.dumps(d,sort_keys=True).encode())
        elif blueprint and p.name=='section_registry.csv':
            rs=rows(p)
            for r in rs:r.pop('status',None)
            h.update(json.dumps(rs,sort_keys=True).encode())
        else:h.update(p.read_bytes())
    s=state(root);h.update(json.dumps({k:s.get(k) for k in ['paper_type','target_journal','manuscript_title_working']},sort_keys=True).encode())
    if not blueprint:h.update(json.dumps(s.get('unresolved_items',[]),sort_keys=True).encode())
    return h.hexdigest()

def approve(root,gate,record,choice):
    root=Path(root);p=path(root,record)
    if len(p.read_text().strip())<25:raise ValueError('Record the actual user decision; not a blank approval')
    s=state(root);d={'gate':gate,'record':record,'hash':digest(p),'choice':choice,'at':now(),'by':'user','fingerprint':fingerprint(root,gate!='D')}
    s['author_decisions'].append(d);save(root,s)
    with (root/'manuscript_blueprint/decision_log.md').open('a') as f:f.write('\n'+json.dumps(d,ensure_ascii=False)+'\n')
    return d

def approved(root,gate,fresh=False):
    ds=[x for x in state(root)['author_decisions'] if x.get('gate')==gate and x.get('by') in {'user','agent_auto'}]
    if not ds:return False
    d=ds[-1]
    return digest(path(root,d['record']))==d['hash'] and (not fresh or d['fingerprint']==fingerprint(root,gate!='D'))

def brief_errors(file,kind):
    d=yaml.safe_load(Path(file).read_text());errors=[]
    if not isinstance(d,dict):return ['Brief must be a mapping']
    schema=d.get('brief_schema','full')
    if schema not in {'full','compact-v1'}:return ['Unknown brief schema']
    compact=schema=='compact-v1'
    for k in M[('compact_' if compact else '')+kind+'_fields']:
        if k not in d or d[k] is None or d[k]=='':errors.append('Missing brief field '+k)
    if compact:
        for k in (['expected_source_files','expected_outputs'] if kind=='figure' else ['rows','columns','data_sources']):
            if not isinstance(d.get(k),list) or not d[k] or any(not isinstance(v,str) or not v.strip() for v in d[k]):errors.append('Expected nonempty string list '+k)
        if kind=='figure' and (type(d.get('panel_count')) is not int or d['panel_count']!=1 or d.get('figure_type')=='MIXED_MULTI_PANEL'):
            errors.append('Complex/multi-panel figures require full brief schema')
    if kind=='figure':
        if d.get('figure_type') not in M['figure_types']:errors.append('Invalid figure type')
        panels=d.get('panels',[])
        if not isinstance(panels,list) or any(not isinstance(p,dict) for p in panels):return errors+['Panels must be a list of mappings']
        if not panels or d.get('panel_count')!=len(panels):errors.append('Panel count/content mismatch')
        for p in panels:
            for k in ['label','scientific_role','exact_content','sources','axes_variables','visual_form']:
                if not p.get(k):errors.append('Incomplete panel '+k)
        if d.get('generation_route')!='nature-figure':errors.append('Figure production must route to nature-figure')
    return errors

def plan_errors(root):
    root=Path(root);folder=root/'manuscript_blueprint';errors=[]
    if not filled(folder/'00_intake_audit.md'):errors.append('Substantive intake audit missing')
    mini=folder/'writing_plan.md'
    if mini.exists():
        text=mini.read_text()
        if not filled(mini):errors.append('Writing plan incomplete')
        for heading in ['Positioning','Sections and evidence','Displays and sources','Boundaries and delivery']:
            match=re.search(r'^## '+re.escape(heading)+r'\s*\n(.*?)(?=^## |\Z)',text,re.M|re.S)
            if not match or len(match.group(1).strip())<20:errors.append('Missing substantive plan section '+heading)
    else:
        for name in ['01_research_story.md','02_claim_evidence_map.md','03_section_plan.md','04_figure_plan.md','05_table_plan.md','06_asset_plan.md','07_literature_visual_plan.md','08_supplementary_plan.md','09_citation_plan.md']:
            if not filled(folder/name):errors.append('Legacy blueprint incomplete: '+name)
    return errors

def lock(root):
    root=Path(root)
    if not all(approved(root,g) for g in 'AB') or not approved(root,'C',True):raise ValueError('Gates A/B and current C required')
    errors=plan_errors(root)
    if errors:raise ValueError('; '.join(errors))
    for kind in ['figure','table']:
        for p in (root/(kind+'s')/'briefs').glob('*.yaml'):
            errs=brief_errors(p,kind)
            if errs:raise ValueError('; '.join(errs))
    s=state(root);s['blueprint_status']='BLUEPRINT_APPROVED';s['blueprint_hash']=fingerprint(root,True);save(root,s)
    return s

def transition(root,phase):
    s=state(root)
    if phase!=s['current_phase']+1:raise ValueError('Sequential transition required; explicitly log deliberate reopening')
    g={2:'A',3:'B',4:'C'}.get(phase)
    if g and not approved(root,g):raise ValueError('User Gate '+g+' required')
    if phase>=5 and (s['blueprint_status']!='BLUEPRINT_APPROVED' or s['blueprint_hash']!=fingerprint(root,True)):raise ValueError('Approved blueprint required or changed')
    if phase==9:raise ValueError('Use finalize for final readiness gate')
    s['current_phase']=phase;save(root,s);return s

def literature_trace_valid(root,r,text):
    """Validate an explicit literature-number trace, never a replacement study result."""
    if r.get('source_mode')!='LITERATURE_NUMERIC':return False
    required=['text_excerpt','value','unit','verification_path','verification_sha256','citation_key']
    if any(not r.get(k) for k in required) or r['text_excerpt'] not in text:return False
    vp=path(root,r['verification_path'])
    if digest(vp)!=r['verification_sha256']:return False
    v=yaml.safe_load(vp.read_text())
    if v.get('status')!='VERIFIED' or not v.get('locator') or not v.get('observed_evidence'):return False
    if v.get('source_mode') not in M['source_modes'][1:]:return False
    if digest(path(root,v.get('original_path','')))!=v.get('original_sha256'):return False
    key=r['citation_key']
    bib=(Path(root)/'references.bib').read_text()
    if key!=v.get('citation_key') or not re.search(r'(?<!\w)@'+re.escape(key)+r'(?![\w:./-])',text):return False
    if not re.search(r'@\w+\s*[{(]\s*'+re.escape(key)+r'\s*,',bib):return False
    return any(n.get('result_id')==r.get('result_id') and n.get('value')==r['value'] and n.get('unit')==r['unit'] and n.get('text_excerpt')==r['text_excerpt'] for n in v.get('numeric_values',[]))

def _check(root):
    root=Path(root);s=state(root);blocking=state_errors(s);pending=[];snap=root/'inputs/handoff'
    blocking += intake(root)['blockers']
    pending += plan_errors(root)
    if s['blueprint_status']!='BLUEPRINT_APPROVED' or s['blueprint_hash']!=fingerprint(root,True):pending.append('Approve current complete blueprint')
    for item in s['unresolved_items']:
        if item.get('classification')=='BLOCKING':blocking.append(item.get('item','Unresolved central blocker'))
    paper=root/'manuscript.md';text=paper.read_text() if paper.exists() else ''
    if not text.strip():pending.append('Complete manuscript.md missing')
    sections=rows(root/'section_registry.csv')
    if not sections:pending.append('Section registry absent')
    headings=list(re.finditer(r'^#{1,6}\s+(.+)$',text,re.M))
    bodies={m.group(1).strip():text[m.end():headings[i+1].start() if i+1<len(headings) else len(text)] for i,m in enumerate(headings)}
    for r in sections:
        body=bodies.get(r['heading'],'').strip()
        prose=' '.join(l for l in body.splitlines() if not re.match(r'^\s*(?:[-*]|\d+[.)]|\|)',l))
        if r.get('status')!='DRAFTED' or len(prose)<45:pending.append('Missing substantive approved section: '+r['heading'])
    for name in ['supplementary.md','terminology_ledger.yaml','unresolved_items.md','author_input_needed.md']:
        if not (root/name).exists() or not filled(root/name):pending.append('Missing/unfilled '+name)
    for token in re.findall(r'\[(AUTHOR_INPUT_NEEDED|DATA_REQUIRED|SOURCE_REQUIRED|VERIFY):[^\]]*\]',text):
        if token!='AUTHOR_INPUT_NEEDED':blocking.append('Unresolved evidence placeholder '+token)
    for item in s['unresolved_items']:
        if item.get('classification') not in {'AUTHOR_INPUT_NEEDED','MISSING_BUT_NONBLOCKING','RESOLVED','BLOCKING'}:blocking.append('Unclassified unresolved item')
        if item.get('classification')=='AUTHOR_INPUT_NEEDED' and (item.get('impact')!='NONCENTRAL' or not item.get('item')):blocking.append('Author check may hide central evidence')
    author_tokens=re.findall(r'\[AUTHOR_INPUT_NEEDED:[^\]]*\]',text)
    author_items=[i for i in s['unresolved_items'] if i.get('classification')=='AUTHOR_INPUT_NEEDED' and i.get('impact')=='NONCENTRAL']
    if author_tokens and not author_items:blocking.append('Unclassified author placeholders')
    # Original source keys, not any arbitrary numeric text, establish data traceability.
    resultmap={r['result_id']:r for r in rows(snap/'04_results_facts.csv')}
    cmap=rows(root/'claim_evidence_map.csv');originals={c['claim_id']:c for c in yaml.safe_load((snap/'03_claim_registry.yaml').read_text()).get('claims',[])}
    if not cmap:pending.append('Manuscript claim map absent')
    if len({c['claim_id'] for c in cmap})!=len(cmap):blocking.append('Duplicate manuscript claim IDs')
    if not any(c.get('importance')=='CENTRAL' for c in cmap):blocking.append('No central manuscript claim')
    for c in cmap:
        old=originals.get(c['claim_id'])
        if not old:blocking.append('Claim missing from handoff: '+c['claim_id']);continue
        declared={x.strip() for x in c.get('supporting_results','').split(';') if x.strip()}
        if not declared<=set(old.get('supporting_result_ids',[])):blocking.append('Claim result mapping not supported by handoff')
    traces=rows(root/'numeric_trace.csv');traceids=set()
    for r in traces:
        value=resultmap.get(r.get('result_id'))
        if r.get('source_mode')=='LITERATURE_NUMERIC':
            # Never let a supplemental literature trace shadow a frozen handoff result.
            if value is not None or not literature_trace_valid(root,r,text):blocking.append('Untraceable literature numeric excerpt')
        elif not value or r.get('value')!=value['value'] or r.get('unit')!=value['unit'] or r.get('text_excerpt') not in text:blocking.append('Untraceable numeric excerpt')
        else:traceids.add(r['result_id'])
    for c in cmap:
        if c.get('importance')=='CENTRAL':
            old=originals.get(c['claim_id'])
            if not old or old.get('status')!='SUPPORTED':blocking.append('Unsupported central manuscript claim '+c['claim_id'])
            if old:
                for rid in old.get('supporting_result_ids',[]):
                    if resultmap[rid].get('kind')=='numeric' and rid not in traceids:blocking.append('Central numerical result lacks prose trace '+rid)
    assets=rows(root/'manuscript_asset_manifest.csv');assetids=set();verifications={}
    for p in (root/'source_verification').glob('*.yaml'):
        d=yaml.safe_load(p.read_text());vid=d.get('verification_id');verifications[vid]=d
    for a in assets:
        aid=a['manuscript_asset_id']
        if not aid or aid in assetids:blocking.append('Empty/duplicate asset ID')
        assetids.add(aid)
        if a['type'] not in {'FIGURE','TABLE'}:blocking.append('Unknown final display type')
        if a['status']!='FINAL':pending.append('Asset not final: '+aid)
        for k in ['provenance','copyright_status','processing','generator','source_type']:
            if not a.get(k):blocking.append('Missing asset provenance '+aid+': '+k)
        if a.get('copyright_status') not in {'OWNED','LICENSED','PERMISSION_GRANTED','PUBLIC_DOMAIN'}:blocking.append('Unresolved rights '+aid)
        final=path(root,a['final_path'])
        if digest(final)!=a['sha256']:blocking.append('Changed asset '+aid)
        caption=path(root,a['caption_path']).read_text().strip()
        if len(caption)<30:pending.append('Missing meaningful caption '+aid)
        if aid not in text:pending.append('Display not called out: '+aid)
        brief=path(root,a['brief_path']);kind='figure' if a['type']=='FIGURE' else 'table'
        blocking += [aid+': '+e for e in brief_errors(brief,kind)]
        bd=yaml.safe_load(brief.read_text())
        if a.get('generation_code'):path(root,a['generation_code'])
        if kind=='figure':
            for out in bd['expected_outputs']:path(root,out)
            for src in bd['expected_source_files']:path(root,src)
        else:path(root,bd['source_file'])
        literate=a['source_type'] in M['source_modes'][1:] or bool(a.get('paper_ids'))
        vids=[x.strip() for x in a.get('verification_ids','').split(';') if x.strip()]
        if literate and not vids:blocking.append('Selected literature component unverified '+aid)
        for vid in vids:
            v=verifications.get(vid)
            if not v:blocking.append('Missing verification '+vid);continue
            for k in M['verification_fields']:
                if v.get(k) is None or v.get(k)=='':blocking.append('Verification missing '+k)
            if v.get('brief_path')!=a['brief_path']:blocking.append('Verification refers to another brief '+vid)
            if not (v.get('component_id')==aid or str(v.get('component_id','')).startswith(aid+':')):blocking.append('Verification component mismatch '+vid)
            if v['status']!='VERIFIED' or v['source_mode'] not in M['source_modes'][1:]:blocking.append('Invalid used-source verification '+vid)
            if digest(path(root,v['original_path']))!=v['original_sha256'] or digest(brief)!=v['brief_sha256']:blocking.append('Source/brief changed after verification '+vid)
            if v['source_mode']=='LITERATURE_REPRODUCED' and v['permission'] not in {'LICENSED','PERMISSION_GRANTED','PUBLIC_DOMAIN'}:blocking.append('Reproduction not cleared '+vid)
            if v['source_mode']=='LITERATURE_SYNTHESIZED' and len(v.get('fact_source_map',[]))<2:blocking.append('Synthesis lacks multi-source mapping')
    # Planned briefs may not disappear simply because absent from the final manifest.
    for folder,key in [('figures','figure_id'),('tables','table_id')]:
        for p in (root/folder/'briefs').glob('*.yaml'):
            d=yaml.safe_load(p.read_text())
            if d.get('status')=='OMITTED_WITH_REASON' and not d.get('omission_reason'):blocking.append('Display omission requires explicit reason')
            if d.get('status')!='OMITTED_WITH_REASON' and d.get(key) not in assetids:pending.append('Planned display not produced: '+str(d.get(key)))
    bib=(root/'references.bib').read_text() if (root/'references.bib').exists() else ''
    keys=set(re.findall(r'@\w+\s*[{(]\s*([^,\s]+)\s*,',bib))
    cites=set(re.findall(r'(?<!\w)@([\w:./-]+)',text))
    for key in cites-keys:blocking.append('Unknown citation '+key)
    for label in re.findall(r'\b(?:Figure|Table)\s+\d+\b',text):
        if label not in assetids:pending.append('Unresolved display callout '+label)
    audit=s.get('content_check') or {}
    if audit.get('fingerprint')!=fingerprint(root) or audit.get('status')!='PASS':pending.append('Current full-draft factual read-through needed')
    elif digest(path(root,audit['record']))!=audit.get('hash'):blocking.append('Content check record changed')
    if not approved(root,'D',True):pending.append('Current Gate D completion record needed')
    if not s['test_only'] and re.search(r'\b(MOCK|FIXTURE)\b',text):blocking.append('MOCK text cannot be production manuscript')
    status='BLOCKED' if blocking else ('DRAFT_IN_PROGRESS' if pending else ('DRAFT_COMPLETE_WITH_AUTHOR_CHECKS' if author_items else 'MANUSCRIPT_DRAFT_READY'))
    return {'status':status,'blockers':sorted(set(blocking)),'pending':sorted(set(pending)),'test_only':s['test_only'],'checked_at':now(),'fingerprint':fingerprint(root)}

def check(root):
    try:return _check(root)
    except (ValueError,TypeError,KeyError,AttributeError,OSError,yaml.YAMLError) as e:return {'status':'BLOCKED','blockers':['Malformed/missing input: '+str(e)],'pending':[],'test_only':state(root).get('test_only',False)}

def finalize(root):
    root=Path(root);r=check(root);s=state(root);s['draft_readiness']=r['status'];save(root,s);write_json(root/'checks/readiness.json',r)
    for marker_name in ['MANUSCRIPT_DRAFT_READY.md','DRAFT_COMPLETE_WITH_AUTHOR_CHECKS.md','MOCK_DRAFT_ONLY.md']:
        marker=root/marker_name
        if marker.exists():marker.rename(root/'history'/('invalidated-'+datetime.now().strftime('%Y%m%d%H%M%S%f')+'-'+marker_name))
    if r['status'] not in {'MANUSCRIPT_DRAFT_READY','DRAFT_COMPLETE_WITH_AUTHOR_CHECKS'}:return r
    s['current_phase']=9;save(root,s)
    name='MOCK_DRAFT_ONLY.md' if r['test_only'] else ('MANUSCRIPT_DRAFT_READY.md' if r['status']=='MANUSCRIPT_DRAFT_READY' else 'DRAFT_COMPLETE_WITH_AUTHOR_CHECKS.md')
    (root/name).write_text(r['status']+'\n\n'+('MOCK: software dry-run only.\n' if r['test_only'] else '')+'Complete Stage 2 draft; not polished, peer-reviewed, submission-cleared or typeset.\nRead manuscript.md, supplementary.md, blueprint, assets and checks/readiness.json.\n')
    return r

def main():
    p=argparse.ArgumentParser();sp=p.add_subparsers(dest='command',required=True)
    for cmd in ['init','intake','state','approve','lock','transition','fingerprint','check','finalize','brief']:
        a=sp.add_parser(cmd);a.add_argument('project')
        if cmd=='init':a.add_argument('--handoff',required=True);a.add_argument('--paper-type',choices=list(M['paper_types']),required=True);a.add_argument('--mock',action='store_true');a.add_argument('--input-map')
        if cmd=='approve':a.add_argument('--gate',choices=list('ABCD'),required=True);a.add_argument('--record',required=True);a.add_argument('--choice',required=True)
        if cmd=='transition':a.add_argument('--phase',type=int,required=True)
        if cmd=='brief':a.add_argument('--kind',choices=['figure','table'],required=True)
    a=p.parse_args()
    try:
        if a.command!='init':_coord.enter(a.project,'manuscript_writing',a.command=='finalize')
        if a.command=='init':r=init(a.project,a.handoff,a.paper_type,a.mock,read_json(a.input_map) if a.input_map else None)
        elif a.command=='state':
            r=state(a.project)
            if state_errors(r):raise ValueError('; '.join(state_errors(r)))
        elif a.command=='approve':r=approve(a.project,a.gate,a.record,a.choice)
        elif a.command=='transition':r=transition(a.project,a.phase)
        elif a.command=='fingerprint':r={'fingerprint':fingerprint(a.project)}
        elif a.command=='brief':r={'errors':brief_errors(a.project,a.kind)}
        else:r=globals()[a.command](a.project)
        if a.command=='init':_coord.enter(a.project,'manuscript_writing')
        if a.command=='finalize' and r.get('status')=='MANUSCRIPT_DRAFT_READY':_coord.completed(a.project,'manuscript_writing',Path(a.project)/'checks/readiness.json',{'manuscript_draft':Path(a.project)/'manuscript.md'})
        if a.command=='approve':_coord.record_decision(a.project,'manuscript_writing',r)
        print(json.dumps(r,ensure_ascii=False,indent=2));return 2 if r.get('status') in {'BLOCKED','DRAFT_IN_PROGRESS'} or r.get('errors') else 0
    except (ValueError,FileExistsError,FileNotFoundError,KeyError) as e:print(json.dumps({'status':'ERROR','error':str(e)}));return 1
if __name__=='__main__':sys.exit(main())
