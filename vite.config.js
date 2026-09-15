import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'
import { handleApi } from './server/api.js'
try { process.loadEnvFile('backend/.env') } catch {}
export default defineConfig({
 plugins:[vue(),{name:'wenjian-api',configureServer(server){server.middlewares.use('/api',async(req,res)=>{try{const chunks=[];for await(const c of req)chunks.push(c);const request=new Request(`http://${req.headers.host}/api${req.url}`,{method:req.method,headers:req.headers,...(['GET','HEAD'].includes(req.method)?{}:{body:Buffer.concat(chunks)})});const response=await handleApi(request,process.env);res.writeHead(response.status,Object.fromEntries(response.headers));res.end(Buffer.from(await response.arrayBuffer()))}catch{res.writeHead(500);res.end('Service unavailable')}})}}],
 server:{host:'127.0.0.1',port:5173,strictPort:true},
})
