import sys,os,json,tempfile,importlib.util,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parent/'publishers/gms'))
import fb_publish as f
class Formats(unittest.TestCase):
 def run_format(self,slot,product,tiny_remote=False):
  from PIL import Image
  with tempfile.TemporaryDirectory() as root:
   folder=Path(root)/'2099-01-01'/f'carousel-{slot}';folder.mkdir(parents=True)
   for n in ('one.jpg','two.jpg'):Image.new('RGB',(30,40),'violet').save(folder/n)
   (folder/'carousel.json').write_text(json.dumps(dict(caption='A unique approved topic\nBody',slides=['one.jpg','two.jpg'])))
   calls=[]
   def api(method,path,token,params=None):
    calls.append((method,path,params or {}))
    if path.endswith('/photos'):return {'id':f'photo{len(calls)}'}
    if method=='GET' and path.startswith('photo'):return {'images':[{'source':'stored','width':1 if tiny_remote else 1080,'height':1 if tiny_remote else 1350}]}
    if path.endswith('/feed'):return {'id':'post'}
    return {'permalink_url':'https://facebook.com/verified'}
   catalog={'products':[dict(title=t+' Hoodie',handle=str(i),images=[{'src':'https://cdn.shopify.com/test.jpg'}],variants=[{'price':'79'}]) for i,t in enumerate(('Be Kind','Peace Starts With Us','Enjoy The Little Things'))]}
   import io
   with patch.dict(os.environ,FB_PAGE_TOKEN_GMS='placeholder',FB_PAGE_ID_GMS='page',GMS_PUBLIC_ASSET_BASE='https://raw.githubusercontent.com/emanuelconti/claude-restaurants-/commit/approved'),patch.object(f,'page_token',return_value='placeholder'),patch.object(f,'recent',return_value=[]),patch.object(f,'product_card',return_value=b'checked-native-card'),patch.object(f,'call',side_effect=api),patch.object(f.IG,'check_public'),patch.object(f.urllib.request,'urlopen',side_effect=lambda *a,**kw:io.BytesIO(json.dumps(catalog).encode())),patch.object(sys,'argv',['fb','--date','2099-01-01','--slot',str(slot),'--out',root]):
    if tiny_remote:
     with self.assertRaisesRegex(SystemExit,'tiny placeholder'):f.main()
     self.assertFalse(any(x[1]=='page/feed' for x in calls))
     self.assertFalse((folder/'published-facebook.json').exists())
     return
    f.main()
   feed=[x[2] for x in calls if x[1]=='page/feed'][0]
   self.assertNotIn('child_attachments',feed)
   self.assertEqual(len(json.loads(feed['attached_media'])),3 if product else 2)
   self.assertIn('https://goodmessagestudio.com',feed['message'])
   receipt=json.loads((folder/'published-facebook.json').read_text())
   self.assertEqual(receipt['format'],'native_products' if product else 'native_editorial_carousel')
 def test_remote_placeholder_never_creates_feed_post(self):self.run_format(1,False,True)
 def test_tiny_product_placeholder_is_rejected(self):
  from PIL import Image
  import io
  raw=io.BytesIO();Image.new('RGB',(1,1),'white').save(raw,'PNG')
  with self.assertRaisesRegex(RuntimeError,'placeholder'):f.product_card(raw.getvalue(),'Product','S$79')
 def test_product_card_has_fixed_portrait_size(self):
  from PIL import Image
  import io
  raw=io.BytesIO();Image.new('RGB',(800,1000),'#b0bbaa').save(raw,'JPEG')
  encoded=f.product_card(raw.getvalue(),'Enjoy The Little Things Hoodie','Shop now · S$79')
  with Image.open(io.BytesIO(encoded)) as image:self.assertEqual(image.size,(1080,1350))
 def test_editorial_uses_all_reviewed_slides(self):self.run_format(1,False)
 def test_products_use_native_photos_with_sgd(self):self.run_format(4,True)
if __name__ == '__main__': unittest.main()
