const { chromium } = require('playwright');
const http=require('http'),fs=require('fs'),path=require('path');
const srv=http.createServer((q,s)=>{const f=path.join(__dirname,decodeURIComponent(q.url.split('?')[0]));
 fs.readFile(f,(e,d)=>{if(e){s.writeHead(404);return s.end()}s.writeHead(200,{'Content-Type':f.endsWith('.js')?'text/javascript':'text/html'});s.end(d)})}).listen(8765);
(async()=>{const page=process.env.SCENE||'socialperks-city.html',w=+(process.env.W||1080),h=+(process.env.H||1920),only=process.argv[2];
 const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const p=await b.newPage({viewport:{width:w,height:h}});
 p.on('console',m=>{if(m.type()==='error')console.log('ERR',m.text())});
 await p.goto(`http://localhost:8765/${page}?w=${w}&h=${h}`);await p.waitForFunction('window.ready===true',{timeout:60000});
 fs.mkdirSync('frames',{recursive:true});
 const fps=30,N=300;const list=only?only.split(',').map(Number):[...Array(N).keys()];
 for(const i of list){await p.evaluate(t=>window.renderAt(t),i/fps);await p.screenshot({path:`frames/f${String(i).padStart(4,'0')}.png`})}
 await b.close();srv.close();})();
