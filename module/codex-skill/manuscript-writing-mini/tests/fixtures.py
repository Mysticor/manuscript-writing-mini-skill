"""MOCK ONLY acceptance material, no real publications or author decisions."""
import csv,json,sys,shutil
from pathlib import Path
import yaml
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import manuscriptctl as mc

def csvwrite(p,data):
 p=Path(p)
 fields=next(csv.reader(p.read_text().splitlines())) if p.exists() else list(data[0])
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(data)
def gate(root,g):
 p=root/'checks'/f'mock-user-{g}.md';p.write_text('MOCK simulated user decision for test Gate '+g+'. No actual user approval is asserted. This fixture accepts its synthetic plan only.\n')
 mc.approve(root,g,str(p.relative_to(root)),'MOCK approved')
def handoff(dest):
 src=Path(__file__).resolve().parents[4]/'test-fixtures/handoff'
 shutil.copytree(src,dest)
 return dest

def create(root,source,review=False):
 mc.init(root,source,'review' if review else 'original_research',True)
 snap=root/'inputs/handoff'
 # A review has synthesis evidence and genuine local MOCK source documents, no pretend experiments.
 if review:
  (snap/'package_checksums.json').unlink(missing_ok=True)
  claims=yaml.safe_load((snap/'03_claim_registry.yaml').read_text())
  claims['claims'][0].update(claim='MOCK corpus separates retaining inputs from reporting aggregates',supporting_result_ids=[],supporting_experiments=[],supporting_literature=['mock_source','mock_aggregate'])
  (snap/'03_claim_registry.yaml').write_text(yaml.safe_dump(claims))
  csvwrite(snap/'04_results_facts.csv',[])
  bib='@misc{mock_source, title={MOCK raw-input design note}, author={Fixture}, year={2026}, note={Not a publication}}\n@misc{mock_aggregate, title={MOCK aggregate design note}, author={Fixture}, year={2026}, note={Not a publication}}\n'
  (snap/'references.bib').write_text(bib);(root/'references.bib').write_text(bib)
 (root/'source_verification/mock_original.md').write_text('# MOCK original source: raw-input design note\n\nPage 1, Figure 1 panel a. Caption: retain the input rows before calculation. A raw-input record preserves individual values and permits recalculation. This is a software test note, not a publication. Author: Fixture; own work; permission OWNED.\n')
 (root/'source_verification/mock_aggregate.md').write_text('# MOCK original source: aggregate design note\n\nPage 1, Figure 1 panel a. Caption: report a summary after calculation. An aggregate record preserves a mean but does not by itself retain input rows. This is a software test note, not a publication. Author: Fixture; own work; permission OWNED.\n')
 original_docs={
 '00_intake_audit.md':'The supplied record contains synthetic values 1, 2, 3, analysis code and R01 with mean 2. C01 is supported only for these inputs. No real field, failed scientific hypothesis, uncertainty estimate, photos or model outputs exist. The target is generic. This is a MOCK software exercise; field-level novelty must not be invented.',
 '01_research_story.md':'In a MOCK arithmetic fixture, a summary must remain traceable to its inputs. The question is whether the recorded mean matches the preserved values. We calculate an arithmetic mean, expose the source rows, and report R01. The boundary is a fixed synthetic list; there is no population inference or broader scientific discovery.',
 '02_claim_evidence_map.md':'C01: the mean of the supplied synthetic values equals 2. Evidence: E01/R01 and data/mock.csv plus code/mock_analysis.py. Demonstrate once in Results; Methods specifies the calculation. Discussion bounds this to the fixture. No performance or significance claims are authorized.',
 '03_section_plan.md':'Abstract answers what this fixture establishes. Introduction explains source-to-summary traceability. Methods permits recalculation. Results demonstrates C01 with the numeric trace and Table 1; Figure 1 explains processing, not an independent experiment. Discussion limits interpretation. Conclusion closes the original question. Draft Results and Methods before framing.',
 '04_figure_plan.md':'Figure 1 explains the read → calculate → report process as one schematic panel. It supports reproducibility, not the numeric finding. The detailed YAML brief is routed to nature-figure. No photos or generated scientific evidence are required.',
 '05_table_plan.md':'Table 1 exposes the three individual input values so the reader can check the mean. Exact values suit a table. Figure 1 displays a process rather than repeating these numbers.',
 '06_asset_plan.md':'Retain the original CSV and analysis script. Table source is a byte-preserving copy of the CSV; the schematic is an owned MOCK vector fixture. No experimental photo or model outputs exist. No AI evidence is used. Publish source paths and hashes in the asset manifest.',
 '07_literature_visual_plan.md':'No external literature visual is needed for the original-research MOCK. The local source notes serve testing of targeted verification separately. Inventory candidates remain REFERENCE_ONLY until explicitly selected.',
 '08_supplementary_plan.md':'Keep the complete decisive evidence, calculation rule, inputs and result in main text/Table 1. SI documents the test provenance and absence of statistical inference; no central evidence is hidden there.',
 '09_citation_plan.md':'Use only mock_source, the explicitly labelled local fixture specification. It is not a scientific publication and has no DOI. No external literature search, citation-padding or invented journal metadata is appropriate.'}
 if review:
  original_docs.update({
   '00_intake_audit.md':'The MOCK corpus comprises two local design notes, covering input retention and aggregate reporting. There are no experiments or numerical research results. The supported synthesis separates the information retained by these designs. It cannot establish field consensus, prevalence or superiority.',
   '01_research_story.md':'Scope: two MOCK design notes, not a field survey. Organizing principle: information retained through summarization. Taxonomy: input-preserving versus aggregate-only records. Both communicate data but serve different audit needs. The synthesis adds a decision axis; it does not claim a new scientific result or comprehensive coverage.',
   '02_claim_evidence_map.md':'C01 synthesis: retaining inputs and reporting aggregates serve different information needs. Supported by mock_source and mock_aggregate. No disagreement about their declared contents is observed; broader effectiveness is unknown. The corpus is too small and artificial for consensus claims.',
   '03_section_plan.md':'Scope defines the two-note corpus. Retention taxonomy groups ideas by record content. Synthesis and trade-offs explains what the axis reveals. Open questions identifies missing comparisons without inventing failures. Conclusion bounds the conceptual map. No experimental Methods/Results are imposed.',
   '04_figure_plan.md':'Figure 1 is a synthesis of the two MOCK notes organized by retained information. The horizontal distinction compares raw input retention and aggregate retention; it is not a copied panel. Map each concept to the original note, then verify both sources at use.',
   '05_table_plan.md':'No table is planned for this small review fixture: the concept distinction is adequately expressed by Figure 1 and continuous prose. Adding an empty study-comparison table would duplicate the same information.',
   '06_asset_plan.md':'Produce one synthetic taxonomy vector fixture with both local source notes retained. Use LITERATURE_SYNTHESIZED with fact-to-source mapping and owned test assets. No photograph, benchmark or model output exists.',
   '07_literature_visual_plan.md':'Select MOCK P1 Figure 1 and P2 Figure 1 from the visual inventory because they support the retention axis. Reopen each note, locate page 1/panel a, compare caption with surrounding text, verify its limited claim. Record original hashes before synthesis.',
   '08_supplementary_plan.md':'Main text retains the organizing distinction and its boundary. SI preserves the corpus definition and notes that no systematic search or meta-analysis occurred.',
   '09_citation_plan.md':'Cite mock_source and mock_aggregate for their own concepts. Both are labelled MOCK local notes. No invented DOI or real publication is used. The synthesis is a reasoned organization of these notes, not a claim about published literature.'})
 for name,body in original_docs.items():(root/'manuscript_blueprint'/name).write_text('# '+name[3:-3]+'\n\nStatus: MOCK COMPLETE\n\n'+body+'\n')
 (root/'manuscript_blueprint/decision_log.md').write_text('# MOCK decisions only\n')
 headings=['Scope','Retention taxonomy','Synthesis and trade-offs','Open questions','Conclusion'] if review else ['Abstract','Introduction','Methods','Results','Discussion','Conclusion']
 csvwrite(root/'section_registry.csv',[dict(section_id=f'S{i}',heading=h,purpose=original_docs['03_section_plan.md'],question_answered=h,claim_ids='C01',evidence='MOCK source notes' if review else 'R01;E01',required_displays='Figure 1' if review else 'Figure 1;Table 1',key_citations='mock_source',transition_in='Preceding argument',transition_out='Next inferential question',exclude='Real-world novelty, unperformed analyses',status='DRAFTED') for i,h in enumerate(headings)])
 csvwrite(root/'claim_evidence_map.csv',[dict(claim_id='C01',claim='MOCK retention synthesis' if review else 'MOCK mean equals 2',importance='CENTRAL',target_section='Retention taxonomy' if review else 'Results',supporting_results='' if review else 'R01',supporting_experiments='' if review else 'E01',supporting_literature='mock_source;mock_aggregate' if review else 'mock_source',conflicting_papers='None in MOCK corpus; wider evidence unknown',evidence_strength='Direct MOCK evidence',boundary='Synthetic fixture only',possible_overclaim='No field consensus or generalization',display_need='Figure 1' if review else 'Table 1')])
 f=yaml.safe_load((mc.SKILL/'templates/figure_brief.yaml').read_text())
 f.update(figure_id='Figure 1',working_title='MOCK retention taxonomy' if review else 'MOCK calculation workflow',target_section=headings[1],scientific_question='What information survives summarization?' if review else 'How can the summary be recalculated?',main_claim='C01',why_figure='Expose conceptual relationship across processing steps',why_table_insufficient='A table of exact inputs does not explain the transformation',figure_type='LITERATURE_SYNTHESIZED' if review else 'METHOD_WORKFLOW',overall_layout='One horizontal panel, left input-retaining record, right aggregate record, labelled transition',panel_count=1,required_data=[],required_photos=[],required_model_outputs=[],required_literature=['mock_source','mock_aggregate'] if review else [],labels_annotations=['Inputs','Mean','Retained information'],statistics='N/A: conceptual workflow, no statistical marks',caption_requirements='Explain both nodes and transformation; MOCK only; sources attributed',reviewer_concern='Could schematic imply real evidence or full literature coverage? Explicitly restrict scope.',generation_route='nature-figure',expected_source_files=['figures/source/mock.svg'],expected_outputs=['figures/final/Figure_01.svg'],provenance_mode='LITERATURE_SYNTHESIZED' if review else 'OWNED',status='FINAL',panels=[dict(label='a',scientific_role='Explain information transformation',exact_content='Two labelled boxes: retained inputs → reported mean. State that input rows are not recoverable from mean alone.',sources=['mock_source','mock_aggregate'] if review else ['inputs/handoff/code/mock_analysis.py'],axes_variables='N/A: schematic',visual_form='Flat vector boxes, one arrow, navy labels on white, no generated imagery')])
 (root/'figures/briefs/Figure_01.yaml').write_text(yaml.safe_dump(f,sort_keys=False))
 svg='<svg xmlns="http://www.w3.org/2000/svg" width="640" height="160"><rect width="640" height="160" fill="white"/><g fill="none" stroke="#18416a" stroke-width="2"><rect x="20" y="50" width="230" height="60"/><rect x="390" y="50" width="230" height="60"/><path d="M250 80H390m-12-7 12 7-12 7"/></g><g font-family="sans-serif" font-size="16" fill="#18416a"><text x="40" y="85">Retained input rows</text><text x="410" y="85">Reported mean</text><text x="20" y="25">MOCK fixture only</text></g></svg>'
 (root/'figures/source/mock.svg').write_text(svg);(root/'figures/final/Figure_01.svg').write_text(svg)
 caption='Figure 1. MOCK transformation from retained input rows to a reported mean. Boxes identify information states; the arrow denotes summarization, not causality. This owned software fixture is not empirical evidence.'
 if review:caption+=' Concepts synthesized from the MOCK raw-input and aggregate notes, with no claim of field coverage.'
 (root/'figures/final/Figure_01_caption.md').write_text(caption)
 assets=[dict.fromkeys(next(csv.reader((root/'manuscript_asset_manifest.csv').read_text().splitlines())), '')]
 assets[0].update(manuscript_asset_id='Figure 1',type='FIGURE',final_role='Explain conceptual transformation',source_type='LITERATURE_SYNTHESIZED' if review else 'OWNED',source_asset_ids='MOCK_SVG',experiment_ids='',paper_ids='mock_source;mock_aggregate' if review else '',processing='Owned vector fixture copied unchanged',generator='MOCK fixture; nature-figure route checked, not specialist-rendered',generation_code='',provenance='Owned synthetic test artwork only',copyright_status='OWNED',final_path='figures/final/Figure_01.svg',sha256=mc.digest(root/'figures/final/Figure_01.svg'),caption_path='figures/final/Figure_01_caption.md',brief_path='figures/briefs/Figure_01.yaml',verification_ids='V01;V02' if review else '',status='FINAL')
 if review:
  inventory=root/'source_verification/literature_visual_inventory.csv'
  csvwrite(inventory,[dict(component_id='P1_F1',paper_id='mock_source',figure='1',panel='a',pdf_page='1',original_path='source_verification/mock_original.md',potential_role='Input retention taxonomy'),dict(component_id='P2_F1',paper_id='mock_aggregate',figure='1',panel='a',pdf_page='1',original_path='source_verification/mock_aggregate.md',potential_role='Aggregate retention taxonomy')])
  for vid,pid,orig in [('V01','mock_source','mock_original.md'),('V02','mock_aggregate','mock_aggregate.md')]:
   v=yaml.safe_load((mc.SKILL/'templates/source_verification.yaml').read_text())
   v.update(verification_id=vid,component_id='Figure 1:a',paper_id=pid,doi='N/A: MOCK local note, not a publication',source_mode='LITERATURE_SYNTHESIZED',original_path='source_verification/'+orig,original_sha256=mc.digest(root/'source_verification'/orig),locator='Page 1; Figure 1; panel a',original_caption='Retain input rows before calculation.' if vid=='V01' else 'Report a summary after calculation.',surrounding_context=(root/'source_verification'/orig).read_text(),author_claim='Input rows retained' if vid=='V01' else 'Aggregate alone omits original rows',observed_evidence='Explicit MOCK design note; not experimental evidence',assumptions='These two local notes only',reuse_appropriateness='Useful to compare information retention; no generalization',licence='Owned MOCK fixture',permission='OWNED',attribution='Cite both MOCK local notes in caption',modifications='New organizing axis connects both concepts',fact_source_map=[{'fact':'Raw rows retained','source':'mock_source','locator':'p1 Figure1a'},{'fact':'Aggregate omits rows','source':'mock_aggregate','locator':'p1 Figure1a'}],verified_at=mc.now(),brief_path='figures/briefs/Figure_01.yaml',brief_sha256=mc.digest(root/'figures/briefs/Figure_01.yaml'),status='VERIFIED')
   (root/'source_verification'/f'{vid}.yaml').write_text(yaml.safe_dump(v,sort_keys=False))
 else:
  t=yaml.safe_load((mc.SKILL/'templates/table_brief.yaml').read_text())
  t.update(table_id='Table 1',target_section='Results',scientific_purpose='Expose original inputs for recalculation',question_answered='What values underlie R01?',why_table='Exact rows, not trend or distribution inference',rows=['Input 1','Input 2','Input 3'],columns=['Input order','value (dimensionless)'],data_sources=['inputs/handoff/data/mock.csv'],literature_sources=[],sorting='Original input order',statistics='Raw values only; mean stated in Results; no inference',highlighting='None; all rows retained',main_message='Calculation is inspectable from the full input list',placement='MAIN',source_file='tables/source/mock.csv',caption_requirements='State synthetic inputs, units and no inferred population',status='FINAL')
  (root/'tables/briefs/Table_01.yaml').write_text(yaml.safe_dump(t,sort_keys=False))
  shutil.copy2(snap/'data/mock.csv',root/'tables/source/mock.csv')
  (root/'tables/final/Table_01.md').write_text('| Input order | Value (dimensionless) |\n|---|---|\n| 1 | 1 |\n| 2 | 2 |\n| 3 | 3 |\n')
  (root/'tables/final/Table_01_caption.md').write_text('Table 1. All three synthetic inputs in their original order. Values are dimensionless and are not observations from participants or a population. No inferential statistics apply.')
  a=dict.fromkeys(assets[0],'');a.update(manuscript_asset_id='Table 1',type='TABLE',final_role='Decisive raw inputs',source_type='OWNED',source_asset_ids='A01',experiment_ids='E01',processing='CSV rows transcribed without omission',generator='MOCK fixture table',provenance='inputs/handoff/data/mock.csv',copyright_status='OWNED',final_path='tables/final/Table_01.md',sha256=mc.digest(root/'tables/final/Table_01.md'),caption_path='tables/final/Table_01_caption.md',brief_path='tables/briefs/Table_01.yaml',status='FINAL');assets.append(a)
 csvwrite(root/'manuscript_asset_manifest.csv',assets)
 original='''# MOCK: Source-traceable arithmetic in a synthetic fixture

## Abstract
This software fixture connects an arithmetic summary to preserved inputs and executable analysis. The supplied synthetic list produces the recorded mean. The manuscript exposes the input rows and computation so that the report can be checked. It establishes no scientific finding or population-level inference.

## Introduction
A summary is interpretable only within the record that produced it. Here, the local MOCK specification supplies a fixed input list and a calculation script [@mock_source]. The question is limited to whether the recorded mean is consistent with those materials. No claim about the novelty or accuracy of a research method is made.

## Methods
The analysis used the synthetic values 1, 2 and 3, retained in data/mock.csv within the handoff. The provided script added the values and divided by the number of inputs. No filtering, random sampling or hypothesis test was applied. Figure 1 represents this computation as an information transformation. Its vector artwork is an explanatory fixture, not a measurement or model output.

## Results
The mean was 2 dimensionless units for the three synthetic inputs. This statement corresponds to R01 and can be recalculated from Table 1 using the preserved script. The result supports C01 only for the supplied list. It does not estimate an unknown population quantity, so a confidence interval or significance test would not answer the question posed here.

## Discussion
The input record and calculation make the reported summary inspectable. That traceability is the limited purpose of this fixture. The example contains no comparator, observed system or independent replication; it therefore cannot support claims about empirical performance, robustness or generalizability. The source-retention details appear in Supplementary Information without displacing the decisive inputs from the main manuscript.

## Conclusion
For the supplied synthetic list, the stored result agrees with the explicit computation. Keeping the inputs, calculation and bounded interpretation together permits verification of this software example. Further scientific conclusions would require a real research question and corresponding evidence.
'''
 reviewtext='''# MOCK: Organizing record designs by retained information

## Scope
This conceptual review concerns two local MOCK design notes, not published research. One specifies input retention and the other aggregate reporting [@mock_source; @mock_aggregate]. The purpose is to organize their information content using a common comparison axis. The corpus was supplied for a software fixture; no systematic search or claim of literature coverage is implied.

## Retention taxonomy
Input-preserving and aggregate-only records answer different questions. The former retains the rows needed to revisit a calculation, whereas the latter communicates a summary without those rows. Figure 1 organizes this distinction by what remains available after summarization. This classification connects the two notes through a concept rather than treating each note as an independent narrative unit.

## Synthesis and trade-offs
A reported aggregate can communicate a result while leaving the underlying calculation unavailable for inspection. Retaining inputs preserves the possibility of recalculation, provided that the computation is also specified. These are differences in information content, not demonstrated differences in efficiency or reliability. Neither local note supplies comparative measurements that would establish the superiority of one design.

## Open questions
The supplied corpus does not establish which retention strategy suits a particular research setting. It contains no evidence about storage constraints, access requirements or practical use. Those questions remain outside the synthesis. Evaluating them would require additional evidence rather than extending the conceptual distinction into an unsupported recommendation.

## Conclusion
Retained information provides a useful organizing axis for these two MOCK notes. It distinguishes communicating a summary from preserving the ability to revisit its inputs. The resulting map is deliberately limited to the supplied sources and should not be interpreted as a consensus about scientific record design.
'''
 (root/'manuscript.md').write_text(reviewtext if review else original)
 if not review:csvwrite(root/'numeric_trace.csv',[dict(text_excerpt='The mean was 2 dimensionless units',result_id='R01',value='2',unit='dimensionless',source_note='MOCK R01 from supplied data and analysis')])
 (root/'supplementary.md').write_text('# MOCK Supplementary Information\n\nThe fixture preserves its source notes, inputs and computation under inputs/handoff. No additional scientific analyses were performed. The main manuscript retains its entire decisive evidence chain. These materials are software acceptance examples, not a scientific submission.\n')
 (root/'terminology_ledger.yaml').write_text('status: MOCK\nterms:\n  synthetic inputs: fixed test values, not sampled observations\n  mean: arithmetic average\n  retention: information preserved in the local notes\n')
 for n in ['unresolved_items.md','author_input_needed.md']:(root/n).write_text('# MOCK\n\nNo unresolved fixture inputs. Real scientific use requires actual research materials and user decisions.\n')
 if (root/'manuscript_blueprint/writing_plan.md').exists():
  (root/'manuscript_blueprint/writing_plan.md').write_text('# Writing plan\n\n'+ '\n\n'.join('## '+h+'\n'+body for h,body in [('Positioning',original_docs['01_research_story.md']),('Sections and evidence',original_docs['03_section_plan.md']),('Displays and sources',original_docs['04_figure_plan.md']+' '+original_docs['05_table_plan.md']),('Boundaries and delivery',original_docs['08_supplementary_plan.md']+' '+original_docs['09_citation_plan.md'])]))
 for g in 'ABC':gate(root,g)
 mc.lock(root)
 review_complete(root)
 return root

def review_complete(root):
 record=root/'checks/content-readthrough.md'
 record.write_text('MOCK acceptance read-through: compared every claim with the synthetic source. Confirmed calculation, scope, Methods/Results alignment, citations, captions, decisive evidence placement and consistent terminology. No real scientific validity or publication readiness is asserted.\n')
 s=mc.state(root);s['content_check']={'status':'PASS','fingerprint':mc.fingerprint(root),'record':str(record.relative_to(root)),'hash':mc.digest(record)};mc.save(root,s)
 gate(root,'D')
