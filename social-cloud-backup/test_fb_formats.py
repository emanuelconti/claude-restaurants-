import sys,os,json,tempfile,importlib.util,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent/'publishers/gms'))
import fb_publish as f
class Formats(unittest.TestCase):
 def run_format(self,slot,product):
  from PIL import Image
  with tempfile.TemporaryDirectory() as root:
   folder=Path(root)/'2099-01-01'/f'carousel-{slot}';folder.mkdir(parents=True)
   for n in ('one.jpg','two.jpg'):Image.new('RGB',(30,40),'violet').save(folder/n)
   (folder/'carousel.json').write_text(json.dumps(dict(caption='A unique approved topic\nBody',slides=['one.jpg','two.jpg'])))
   calls=[]
   def api(method,path,token,params=None):
    calls.append((method,path,params or {}))
    if path.endswith('/photos'):return {'id':f'photo{len(calls)}'}
    if method=='GET' and path.startswith('photo'):return {'images':[{'source':'stored'}]}
    if path.endswith('/feed'):return {'id':'post'}
    return {'permalink_url':'https://facebook.com/verified'}
   catalog={'products':[dict(title=t+' Hoodie',handle=str(i),images=[{'src':'https://cdn.shopify.com/test.jpg'}],variants=[{'price':'79'}]) for i,t in enumerate(('Be Kind','Peace Starts With Us','Enjoy The Little Things'))]}
   import io
   with patch.dict(os.environ,FB_PAGE_TOKEN_GMS='placeholder',FB_PAGE_ID_GMS='page',GMS_PUBLIC_ASSET_BASE='https://raw.githubusercontent.com/emanuelconti/claude-restaurants-/commit/approved'),patch.object(f,'page_token',return_value='placeholder'),patch.object(f,'recent',return_value=[]),patch.object(f,'call',side_effect=api),patch.object(f.IG,'check_public'),patch.object(f.urllib.request,'urlopen',return_value=io.BytesIO(json.dumps(catalog).encode())),patch.object(sys,'argv',['fb','--date','2099-01-01','--slot',str(slot),'--out',root]):f.main()
   feed=[x[2] for x in calls if x[1]=='page/feed'][0]
   self.assertNotIn('child_attachments',feed)
   self.assertEqual(len(json.loads(feed['attached_media'])),3 if product else 2)
   self.assertIn('https://goodmessagestudio.com',feed['message'])
   receipt=json.loads((folder/'published-facebook.json').read_text())
   self.assertEqual(receipt['format'],'native_products' if product else 'native_editorial_carousel')
 def test_editorial_uses_all_reviewed_slides(self):self.run_format(1,False)
 def test_products_use_native_photos_with_sgd(self):self.run_format(4,True)
if __name__ == '__main__': unittest.main()
