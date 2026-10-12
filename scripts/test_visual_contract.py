"""Regression tests for requested background/decoration contracts."""
from pathlib import Path
import copy,json,tempfile,unittest
from visual_contract import validate_visual
class VisualTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.ws=Path(self.tmp.name);(self.ws/'checks').mkdir()
  for name,data in [('one.bin',b'first texture'),('renamed.bin',b'first texture'),('two.bin',b'second backdrop'),('derived.bin',b'recolored first texture')]:
   (self.ws/name).write_bytes(data)
 def tearDown(self):self.tmp.cleanup()
 def image(self,name='Base',file='one.bin',role='background_texture',source='texture-one'):
  return dict(type='image',name=name,file=file,box=[0,0,640,220],role='decor',design_role=role,background_source_id=source)
 def layout(self,n=4):
  return dict(width=640,modules=[dict(name='module'+str(i),height=220,layers=[]) for i in range(n)])
 def test_rule1_required_for_four_modules_not_three(self):
  self.assertTrue(any('more than three' in p for p in validate_visual(self.ws,self.layout())[0]))
  self.assertFalse(validate_visual(self.ws,self.layout(3))[0])
  c=self.layout();c['modules'][2]['layers']=[self.image()];self.assertFalse(validate_visual(self.ws,c)[0])
 def test_campaign_needs_other_real_image_overlay(self):
  c=self.layout();c['modules'][0]['layers']=[self.image(role='background_campaign')]
  c['modules'][0]['layers'].append(dict(type='text',name='Headline',text='Product Title',size=52))
  self.assertTrue(any('more than three' in p for p in validate_visual(self.ws,c)[0]))
  c['modules'][0]['layers'].append(dict(type='image',name='Product flat',file='two.bin',box=[10,50,100,140],role='product'))
  self.assertFalse(validate_visual(self.ws,c)[0])
 def test_rename_same_bytes_and_derivative_same_source_rejected(self):
  c=self.layout();c['modules'][2]['layers']=[self.image()]
  c['modules'][3]['layers']=[self.image(file='renamed.bin',source='different-claimed-ID')]
  self.assertTrue(any('adjacent' in p for p in validate_visual(self.ws,c)[0]))
  c['modules'][3]['layers']=[self.image(file='derived.bin',source='texture-one')]
  self.assertTrue(any('adjacent' in p for p in validate_visual(self.ws,c)[0]))
 def test_distinct_adjacent_backgrounds_and_nonadjacent_reuse(self):
  c=self.layout();c['modules'][0]['layers']=[self.image()]
  c['modules'][2]['layers']=[self.image()];c['modules'][3]['layers']=[self.image(file='two.bin',source='texture-two')]
  self.assertFalse(validate_visual(self.ws,c)[0])
 def test_large_pale_type_conflict_but_functional_title_allowed(self):
  c=self.layout();c['modules'][2]['layers']=[self.image(),dict(type='text',name='Product headline',text='Product Title',size=50)]
  self.assertFalse(validate_visual(self.ws,c)[0])
  c['modules'][2]['layers'].append(dict(type='text',name='Ghost lettering',text='DAILY ROTATION',design_role='decorative_large_pale_type',opacity=18))
  self.assertTrue(any('conflicts' in p for p in validate_visual(self.ws,c)[0]))
  c['modules'][2]['layers'][-1]['opacity']=0;self.assertFalse(validate_visual(self.ws,c)[0])
 def test_full_background_classification_and_source_required(self):
  c=self.layout(1);b=self.image();b.pop('design_role');c['modules'][0]['layers']=[b]
  self.assertTrue(any('classify' in p for p in validate_visual(self.ws,c)[0]))
  b['design_role']='background_texture';b['background_source_id']=''
  self.assertTrue(any('source_id' in p for p in validate_visual(self.ws,c)[0]))
 def test_grouped_hidden_background_not_counted(self):
  c=self.layout();c['modules'][2]['layers']=[dict(type='group',name='Hidden background',opacity=0,layers=[self.image()])]
  self.assertTrue(any('more than three' in p for p in validate_visual(self.ws,c)[0]))
 def test_post_export_review_requires_actual_reference_and_all_checks(self):
  c=self.layout();c['modules'][2]['layers']=[self.image()]
  self.assertTrue(any('inspection missing' in p for p in validate_visual(self.ws,c,True)[0]))
  p=self.ws/'checks/visual_balance.json';review=dict(status='passed',notes='Actual reference and exported image reviewed.',reference_files=['two.bin'],checks={k:True for k in ['subject_scale','rule1_visible','decoration_restraint','adjacent_backgrounds']})
  p.write_text(json.dumps(review),encoding='utf-8');issues,evidence=validate_visual(self.ws,c,True)
  self.assertFalse(issues);self.assertIn(str(p),evidence)
  review['checks']['subject_scale']=False;p.write_text(json.dumps(review),encoding='utf-8')
  self.assertTrue(any('subject_scale' in e for e in validate_visual(self.ws,c,True)[0]))
if __name__=='__main__':unittest.main()

