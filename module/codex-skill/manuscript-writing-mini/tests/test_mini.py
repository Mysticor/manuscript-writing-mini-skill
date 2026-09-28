import os
import unittest,tempfile,sys,importlib.util,yaml
from pathlib import Path
import fixtures as f
mc=f.mc
class MiniAcceptance(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.base=Path(self.tmp.name);self.src=f.handoff(self.base/'handoff');self.root=self.base/'manuscript'
 def tearDown(self):self.tmp.cleanup()
 def complete(self):
  f.create(self.root,self.src)
  for p in (self.root/'manuscript_blueprint').glob('*.md'):
   if p.name not in ['00_intake_audit.md','writing_plan.md','decision_log.md']:p.unlink()
  # Strip extra fixture fields to test actual compact briefs, not full briefs with a compact label.
  for kind,name in [('figure','Figure'),('table','Table')]:
   p=self.root/f'{kind}s/briefs/{name}_01.yaml';d=yaml.safe_load(p.read_text())
   d={k:v for k,v in d.items() if k in mc.M['compact_'+kind+'_fields']+['brief_schema']}
   p.write_text(yaml.safe_dump(d))
  f.gate(self.root,'C');mc.lock(self.root);f.review_complete(self.root)
 def test_init_only_one_plan(self):
  mc.init(self.root,self.src,'original_research',True)
  self.assertEqual({p.name for p in (self.root/'manuscript_blueprint').glob('*.md')},{'00_intake_audit.md','writing_plan.md','decision_log.md'})
  with self.assertRaises(ValueError):mc.lock(self.root)
 def test_compact_complete_and_review_import(self):
  self.complete();r=mc.finalize(self.root);self.assertEqual(r['status'],'MANUSCRIPT_DRAFT_READY',r)
  p=Path(os.environ.get('DOWNSTREAM_SKILL_ROOT', '/nonexistent/optional-skill'))/'scripts/reviewctl.py'
  if not p.is_file(): self.skipTest('Optional downstream Skill is not installed')
  spec=importlib.util.spec_from_file_location('mini_downstream_review',p);review=importlib.util.module_from_spec(spec);spec.loader.exec_module(review)
  result=review.init(self.base/'review',self.root,True)
  self.assertEqual(result['status'],'BASELINE_STRUCTURALLY_COMPLETE',result)
  self.assertTrue((self.base/'review/manuscript_blueprint/writing_plan.md').is_file())
 def test_deleted_plan_cannot_bypass_lock(self):
  self.complete();(self.root/'manuscript_blueprint/writing_plan.md').unlink();f.gate(self.root,'C')
  with self.assertRaises(ValueError):mc.lock(self.root)
  self.assertNotEqual(mc.check(self.root)['status'],'MANUSCRIPT_DRAFT_READY')
 def test_empty_plan_section_rejected(self):
  self.complete();p=self.root/'manuscript_blueprint/writing_plan.md';p.write_text(p.read_text().split('## Displays and sources')[0]);f.gate(self.root,'C')
  with self.assertRaises(ValueError):mc.lock(self.root)
 def test_compact_does_not_allow_empty_sources(self):
  self.complete();p=self.root/'figures/briefs/Figure_01.yaml';d=yaml.safe_load(p.read_text());d['expected_source_files']=[];p.write_text(yaml.safe_dump(d))
  self.assertTrue(mc.brief_errors(p,'figure'));self.assertEqual(mc.check(self.root)['status'],'BLOCKED')
 def test_complex_requires_full(self):
  self.complete();p=self.root/'figures/briefs/Figure_01.yaml';d=yaml.safe_load(p.read_text());d['panel_count']=2;d['panels']*=2;p.write_text(yaml.safe_dump(d))
  self.assertTrue(any('full brief' in e for e in mc.brief_errors(p,'figure')))
 def test_full_legacy_still_accepted(self):
  f.create(self.root,self.src);(self.root/'manuscript_blueprint/writing_plan.md').unlink()
  for kind,name in [('figure','Figure'),('table','Table')]:
   p=self.root/f'{kind}s/briefs/{name}_01.yaml';d=yaml.safe_load(p.read_text());d.pop('brief_schema',None);p.write_text(yaml.safe_dump(d));self.assertEqual(mc.brief_errors(p,kind),[])
  f.gate(self.root,'C');mc.lock(self.root);f.review_complete(self.root)
  self.assertEqual(mc.finalize(self.root)['status'],'MANUSCRIPT_DRAFT_READY')
 def test_progress_note_not_scientific_change(self):
  self.complete();before=mc.fingerprint(self.root,True);(self.root/'resume.md').write_text('Next: verify the caption and continue the next section.')
  self.assertEqual(before,mc.fingerprint(self.root,True))
 def test_compact_numeric_tamper_blocked(self):
  self.complete();p=self.root/'numeric_trace.csv';rows=mc.rows(p);rows[0]['value']='1000';f.csvwrite(p,rows)
  self.assertEqual(mc.check(self.root)['status'],'BLOCKED')
 def test_unknown_schema_rejected(self):
  self.complete();p=self.root/'tables/briefs/Table_01.yaml';d=yaml.safe_load(p.read_text());d['brief_schema']='skip-checks';p.write_text(yaml.safe_dump(d))
  self.assertTrue(mc.brief_errors(p,'table'))
if __name__=='__main__':unittest.main()
