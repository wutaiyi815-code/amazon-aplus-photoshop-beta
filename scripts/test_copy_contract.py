"""Regression checks for merged WPS cells, source-copy coverage and saved PSD text."""
from pathlib import Path
import copy,json,tempfile,unittest,zipfile,xml.etree.ElementTree as ET
from openpyxl import Workbook
from workspace import attributes
from copy_contract import extract_candidates,validate_copy
NS='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
class CopyTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.ws=Path(self.tmp.name)
  file=self.ws/'source.xlsx';book=Workbook();sh=book.active;sh.title='产品信息'
  sh.append(['Section 1 Banner','Headline','Source Product Headline'])
  sh.append([None,'Copy','Casual | Cute | OOTD'])
  sh.append(['Section 2 Fit','Headline','Loose Fit'])
  sh.append(['Section 3 Detail','Copy','Hooded Neck; Full Zipper'])
  # Preserve original XML values inside merged ranges, as real WPS source files do.
  book.save(file)
  with zipfile.ZipFile(file) as z:parts={n:z.read(n) for n in z.namelist()}
  xml=ET.fromstring(parts['xl/worksheets/sheet1.xml']);merges=ET.SubElement(xml,'{'+NS+'}mergeCells',{'count':'2'})
  ET.SubElement(merges,'{'+NS+'}mergeCell',{'ref':'A1:C1'})
  ET.SubElement(merges,'{'+NS+'}mergeCell',{'ref':'A2:A3'})
  parts['xl/worksheets/sheet1.xml']=ET.tostring(xml,encoding='utf-8')
  with zipfile.ZipFile(file,'w',zipfile.ZIP_DEFLATED) as z:
   for name,data in parts.items():z.writestr(name,data)
  self.attrs=attributes(file);self.candidates=extract_candidates(self.attrs)
  self.layout={'modules':[dict(name=n,layers=[]) for n in ['campaign','fit_detail']]}
  self.plan={'reviewed':True,'entries':[]}
  for i,c in enumerate(self.candidates):
   target='campaign' if c['section']=='1' else 'fit_detail';name='Source text '+str(i)
   mod=next(m for m in self.layout['modules'] if m['name']==target)
   mod['layers'].append(dict(type='text',name=name,text=c['text']))
   self.plan['entries'].append(dict(id=c['id'],decision='adopt',placements=[dict(module=target,layer=name,text=c['text'])]))
  (self.ws/'attributes.json').write_text(json.dumps(self.attrs,ensure_ascii=False),encoding='utf-8')
 def tearDown(self):self.tmp.cleanup()
 def check(self,plan=None,layout=None,native=None,require=False):
  (self.ws/'copy_plan.json').write_text(json.dumps(plan or self.plan,ensure_ascii=False),encoding='utf-8')
  return validate_copy(self.ws,layout or self.layout,native,require)[0]
 def test_preserves_non_anchor_title_and_section(self):
  grid={c['cell']:c['value'] for c in self.attrs['产品信息']['cells']}
  self.assertEqual(grid['C1'],'Source Product Headline');self.assertEqual(grid['A3'],'Section 2 Fit')
  self.assertEqual(len(self.candidates),4)
  self.assertEqual(next(c for c in self.candidates if c['cell']=='C3')['section'],'2')
  self.assertFalse(self.check())
 def test_missing_source_and_unreviewed_rejected(self):
  p=copy.deepcopy(self.plan);p['entries'].pop();self.assertTrue(any('unaccounted' in e for e in self.check(p)))
  p=copy.deepcopy(self.plan);p['reviewed']=False;self.assertTrue(any('not reviewed' in e for e in self.check(p)))
 def test_replacement_and_wrong_module_rejected(self):
  p=copy.deepcopy(self.plan);l=copy.deepcopy(self.layout);p['entries'][0]['placements'][0]['text']='New campaign slogan'
  l['modules'][0]['layers'][0]['text']='New campaign slogan'
  self.assertTrue(any('omitted/replaced' in e for e in self.check(p,l)))
  p=copy.deepcopy(self.plan);p['entries'][0]['placements'][0]['module']='fit_detail'
  self.assertTrue(any('module-layer' in e for e in self.check(p)))
 def test_typography_and_split_preserve_content(self):
  p=copy.deepcopy(self.plan);l=copy.deepcopy(self.layout)
  p['entries'][0]['placements'][0]['text']='SOURCE PRODUCT\rHEADLINE'
  l['modules'][0]['layers'][0]['text']='SOURCE PRODUCT\rHEADLINE';self.assertFalse(self.check(p,l))
  p=copy.deepcopy(self.plan);l=copy.deepcopy(self.layout);item=p['entries'][-1]
  item['placements']=[dict(module='fit_detail',layer='Detail one',text='Hooded Neck;'),dict(module='fit_detail',layer='Detail two',text='Full Zipper')]
  l['modules'][1]['layers'].pop();l['modules'][1]['layers'] += [dict(type='text',name='Detail one',text='Hooded Neck;'),dict(type='text',name='Detail two',text='Full Zipper')]
  self.assertFalse(self.check(p,l))
 def test_exclusion_and_revision_need_evidence(self):
  p=copy.deepcopy(self.plan);p['entries'][0]=dict(id=p['entries'][0]['id'],decision='exclude')
  self.assertTrue(self.check(p))
  p['entries'][0].update(reason_code='out_of_scope',reason='User requested only fit/detail in this fixture.',evidence='Explicit fixture scope');self.assertFalse(self.check(p))
  p=copy.deepcopy(self.plan);p['entries'][0]['decision']='adapt';self.assertTrue(self.check(p))
  p['entries'][0].update(reason_code='typo',reason='Confirmed spelling correction.',evidence='Source-to-output comparison');self.assertFalse(self.check(p))
 def test_saved_psd_text_and_visibility(self):
  self.assertTrue(any('snapshot' in e for e in self.check(require=True)))
  native=[dict(name=mod['name']+' / '+n['name'],text=n['text'],visible=True,opacity=100) for mod in self.layout['modules'] for n in mod['layers']]
  self.assertFalse(self.check(native=native,require=True));native[0]['text']='Wrong saved title'
  self.assertTrue(any('saved PSD text' in e for e in self.check(native=native,require=True)))
  native[0]['text']=self.layout['modules'][0]['layers'][0]['text'];native[0]['visible']=False
  self.assertTrue(any('hidden' in e for e in self.check(native=native,require=True)))
 def test_flat_column_blank_formula_and_manual_source(self):
  attrs={'Sheet':dict(reader='read_only_full_xml_cells',cells=[
   dict(cell='A1',value='Section1 Headline'),dict(cell='B1',value=''),
   dict(cell='A2',value='Section2 Copy'),dict(cell='B2',value='Warm Fleece Fabric'),
   dict(cell='A3',value='Section3 Copy'),dict(cell='B3',value='=IMAGE("x")',cached_value=None)])}
  self.assertEqual([c['id'] for c in extract_candidates(attrs)],['Sheet!B2'])
  attrs={'Sheet':dict(reader='read_only_full_xml_cells',cells=[
   dict(cell='A1',value='页面'),dict(cell='B1',value='Headline'),dict(cell='C1',value='Copy'),
   dict(cell='A2',value='Section1 Banner'),dict(cell='B2',value='Product Title'),dict(cell='C2',value='Product body'),
   dict(cell='A3',value='尺码表'),dict(cell='B3',value='SIZE'),dict(cell='C3',value='LENGTH')])}
  self.assertEqual([c['id'] for c in extract_candidates(attrs)],['Sheet!B2','Sheet!C2'])
if __name__=='__main__':unittest.main()

