import { createServer } from 'node:http'
import worker from '../dist/server/index.js'
try {process.loadEnvFile('backend/.env')} catch {}
const port=Number(process.env.PREVIEW_PORT || 4173)
createServer(async(req,res)=>{
 try { const chunks=[];for await(const c of req) chunks.push(c);const request=new Request(`http://${req.headers.host}${req.url}`,{method:req.method,headers:req.headers,...(['GET','HEAD'].includes(req.method)?{}:{body:Buffer.concat(chunks)})});const response=await worker.fetch(request,process.env,{});res.writeHead(response.status,Object.fromEntries(response.headers));res.end(Buffer.from(await response.arrayBuffer())) }catch {res.writeHead(500);res.end('Preview error')}
}).listen(port,'127.0.0.1',()=>console.log(`Production preview: http://127.0.0.1:${port}`))
