import csv,json,sys,tempfile,unittest,shutil
from pathlib import Path
import yaml
import fixtures as f
mc=f.mc
import routes
class Acceptance(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.base=Path(self.tmp.name);self.source=f.handoff(self.base/'MOCK_HANDOFF');self.root=self.base/'manuscript'
 def tearDown(self):self.tmp.cleanup()
 def complete(self,review=False):return f.create(self.root,self.source,review)
 def test_A_B_intake_and_resume(self):
  result=mc.init(self.root,self.source,'original_research',True)
  self.assertEqual(result['status'],'AVAILABLE');self.assertTrue((self.root/'manuscript_blueprint/00_intake_audit.md').exists())
  self.assertEqual(mc.state(self.root)['current_phase'],0)
  self.assertFalse(mc.filled(self.root/'manuscript_blueprint/00_intake_audit.md'))
  with self.assertRaises(FileExistsError):mc.init(self.root,self.source,'review',True)
 def test_C_K_complete_original(self):
  self.complete();result=mc.finalize(self.root)
  self.assertEqual(result['status'],'MANUSCRIPT_DRAFT_READY',result)
  self.assertTrue(result['test_only']);self.assertTrue((self.root/'MOCK_DRAFT_ONLY.md').is_file());self.assertFalse((self.root/'MANUSCRIPT_DRAFT_READY.md').exists())
 def test_D_G_H_review_selected_sources(self):
  self.complete(True);result=mc.finalize(self.root)
  self.assertEqual(result['status'],'MANUSCRIPT_DRAFT_READY',result)
  self.assertEqual(mc.rows(self.root/'inputs/handoff/04_results_facts.csv'),[])
  self.assertEqual(len(mc.rows(self.root/'source_verification/literature_visual_inventory.csv')),2)
  (self.root/'source_verification/mock_original.md').write_text('MOCK changed source')
  self.assertTrue(any('Source/brief changed' in e for e in mc.check(self.root)['blockers']))
 def test_E_F_brief_completeness(self):
  self.complete()
  for kind,name in [('figure','Figure'),('table','Table')]:
   p=self.root/f'{kind}s/briefs/{name}_01.yaml';self.assertEqual(mc.brief_errors(p,kind),[])
   d=yaml.safe_load(p.read_text());d.pop('scientific_question' if kind=='figure' else 'rows');p.write_text(yaml.safe_dump(d))
   self.assertTrue(mc.brief_errors(p,kind))
 def test_I_reproduced_requires_clearance(self):
  self.complete(True);p=self.root/'source_verification/V01.yaml';d=yaml.safe_load(p.read_text());d['source_mode']='LITERATURE_REPRODUCED';d['permission']='UNKNOWN';p.write_text(yaml.safe_dump(d))
  self.assertTrue(any('Reproduction not cleared' in e for e in mc.check(self.root)['blockers']))
  d['permission']='PERMISSION_GRANTED';p.write_text(yaml.safe_dump(d));f.review_complete(self.root)
  self.assertEqual(mc.check(self.root)['status'],'MANUSCRIPT_DRAFT_READY')
 def test_I_adapted_and_reference_only(self):
  self.complete(True);p=self.root/'source_verification/V01.yaml';d=yaml.safe_load(p.read_text());d['source_mode']='LITERATURE_ADAPTED';p.write_text(yaml.safe_dump(d));f.review_complete(self.root)
  self.assertEqual(mc.check(self.root)['status'],'MANUSCRIPT_DRAFT_READY')
  d['source_mode']='REFERENCE_ONLY';p.write_text(yaml.safe_dump(d));self.assertEqual(mc.check(self.root)['status'],'BLOCKED')
 def test_I_synthesis_requires_fact_map(self):
  self.complete(True);p=self.root/'source_verification/V01.yaml';d=yaml.safe_load(p.read_text());d['fact_source_map']=[];p.write_text(yaml.safe_dump(d))
  self.assertTrue(any('multi-source mapping' in e for e in mc.check(self.root)['blockers']))
 def test_J_N_real_routes_and_boundaries(self):
  for name in mc.M['allowed_specialists']:
   r=routes.route(name);self.assertFalse(r['executed']);self.assertTrue(all(Path(p).is_file() for p in r['paths']))
  for name in ['nature-polishing','nature-reviewer','latex-document-skill','academic-typesetting']:
   with self.assertRaises(ValueError):routes.route(name)
 def test_L_central_result_absent(self):
  self.complete();p=self.root/'inputs/handoff/04_results_facts.csv';f.csvwrite(p,[])
  result=mc.check(self.root);self.assertEqual(result['status'],'BLOCKED');self.assertNotIn('[DATA_REQUIRED', (self.root/'manuscript.md').read_text())
 def test_M_incomplete_manuscript_invalidates_marker(self):
  self.complete();mc.finalize(self.root);(self.root/'manuscript.md').write_text('# MOCK outline only\n')
  result=mc.finalize(self.root);self.assertNotEqual(result['status'],'MANUSCRIPT_DRAFT_READY');self.assertFalse((self.root/'MOCK_DRAFT_ONLY.md').exists())
 def test_gates_and_blueprint_change(self):
  mc.init(self.root,self.source,'original_research',True)
  with self.assertRaises(ValueError):mc.lock(self.root)
  self.root=self.base/'complete';self.complete();(self.root/'manuscript_blueprint/01_research_story.md').write_text('MOCK new story')
  self.assertIn('Approve current complete blueprint',mc.check(self.root)['pending'])
 def test_numeric_tampering(self):
  self.complete();p=self.root/'numeric_trace.csv';r=mc.rows(p);r[0]['value']='20';f.csvwrite(p,r)
  self.assertTrue(any('Untraceable numeric' in e for e in mc.check(self.root)['blockers']))
 def test_unknown_citation(self):
  self.complete();p=self.root/'manuscript.md';p.write_text(p.read_text()+'\n[@mock_nonexistent]\n')
  self.assertIn('Unknown citation mock_nonexistent',mc.check(self.root)['blockers'])
 def test_unclassified_author_check(self):
  self.complete();s=mc.state(self.root);s['unresolved_items']=[{'classification':'AUTHOR_INPUT_NEEDED','impact':'CENTRAL','item':'Missing evidence'}];mc.save(self.root,s)
  self.assertEqual(mc.check(self.root)['status'],'BLOCKED')
 def test_noncentral_author_check_status(self):
  self.complete();s=mc.state(self.root);s['unresolved_items']=[{'classification':'AUTHOR_INPUT_NEEDED','impact':'NONCENTRAL','item':'Confirm author affiliation'}];mc.save(self.root,s);f.review_complete(self.root)
  self.assertEqual(mc.check(self.root)['status'],'DRAFT_COMPLETE_WITH_AUTHOR_CHECKS')
 def test_missing_caption_asset_and_verification(self):
  self.complete(True);(self.root/'source_verification/V01.yaml').unlink()
  self.assertIn('Missing verification V01',mc.check(self.root)['blockers'])
  (self.root/'figures/final/Figure_01_caption.md').unlink();self.assertEqual(mc.check(self.root)['status'],'BLOCKED')
 def test_mock_never_production(self):
  self.complete();s=mc.state(self.root);s['test_only']=False;mc.save(self.root,s)
  self.assertEqual(mc.finalize(self.root)['status'],'BLOCKED');self.assertFalse((self.root/'MANUSCRIPT_DRAFT_READY.md').exists())
 def test_path_escape_and_map_preflight(self):
  with self.assertRaises(ValueError):mc.init(self.root,self.source,'original_research',True,{'README.md':'../outside'})
  self.assertFalse(self.root.exists())
 def test_manifest_and_state(self):
  paths=mc.M['always_load']+mc.M['templates']+mc.M['scripts']
  for group in mc.M['phase_routes'].values():paths+=group
  for d in mc.M['paper_types'].values():paths.append(d['guide'])
  for rel in paths:self.assertTrue((mc.SKILL/rel).is_file(),rel)
  s=json.loads((mc.SKILL/'templates/state.json').read_text());s['current_phase']=42;self.assertTrue(mc.state_errors(s))
if __name__=='__main__':unittest.main(verbosity=2)
