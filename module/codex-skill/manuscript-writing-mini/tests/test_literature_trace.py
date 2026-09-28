import unittest,tempfile,sys,yaml
from pathlib import Path
import fixtures
m=fixtures.mc
class LiteratureTrace(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.p=Path(self.t.name);(self.p/'source_verification').mkdir();(self.p/'source.pdf').write_bytes(b'original source');(self.p/'references.bib').write_text('@article{paper, title={Example}}')
  self.text='The reported error was 0.7% [@paper].';self.row=dict(source_mode='LITERATURE_NUMERIC',text_excerpt='0.7%',value='0.7',unit='%',result_id='LIT1',citation_key='paper',verification_path='source_verification/n.yaml')
  self.v=dict(status='VERIFIED',source_mode='LITERATURE_SYNTHESIZED',locator='p3',observed_evidence='0.7% in the stated test',original_path='source.pdf',original_sha256=m.digest(self.p/'source.pdf'),citation_key='paper',numeric_values=[{k:self.row[k] for k in ['result_id','value','unit','text_excerpt']}]);self.save()
 def save(self):
  f=self.p/self.row['verification_path'];f.write_text(yaml.safe_dump(self.v));self.row['verification_sha256']=m.digest(f)
 def tearDown(self):self.t.cleanup()
 def test_valid(self):self.assertTrue(m.literature_trace_valid(self.p,self.row,self.text))
 def test_changed_source(self):
  (self.p/'source.pdf').write_bytes(b'changed');self.assertFalse(m.literature_trace_valid(self.p,self.row,self.text))
 def test_changed_record(self):
  (self.p/self.row['verification_path']).write_text('changed');self.assertFalse(m.literature_trace_valid(self.p,self.row,self.text))
 def test_value_mismatch(self):
  self.row['value']='1.0';self.assertFalse(m.literature_trace_valid(self.p,self.row,self.text))
 def test_uncited(self):self.assertFalse(m.literature_trace_valid(self.p,self.row,'0.7%'))
 def test_no_locator(self):
  self.v['locator']='';self.save();self.assertFalse(m.literature_trace_valid(self.p,self.row,self.text))
 def test_not_verified(self):
  self.v['status']='PENDING';self.save();self.assertFalse(m.literature_trace_valid(self.p,self.row,self.text))
if __name__=='__main__':unittest.main()
