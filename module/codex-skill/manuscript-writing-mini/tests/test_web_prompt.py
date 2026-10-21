import importlib.util,tempfile,unittest
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'scripts/web_prompt.py'
spec=importlib.util.spec_from_file_location('web_prompt',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Tests(unittest.TestCase):
 def test_sources_change_and_missing_resource_fails(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t)/'module/codex-skill/demo';root.mkdir(parents=True)
   for name in m.SOURCES:
    p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('DEMO source '+name)
   p=Path(t)/'workflow-contract/portable-work.md';p.parent.mkdir();p.write_text('DEMO portable')
   first=m.render(root);self.assertEqual(first,m.render(root))
   (root/'SKILL.md').write_text('DEMO updated');self.assertNotEqual(first,m.render(root))
   p.unlink()
   with self.assertRaises(FileNotFoundError):m.render(root)
if __name__=='__main__':unittest.main()
