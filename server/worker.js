import { handleApi } from './api.js'
import { assets } from './assets.generated.js'
export default { async fetch(request,env,ctx) {
 const url=new URL(request.url)
 if(url.pathname.startsWith('/api/')) return handleApi(request,env)
 if(!['GET','HEAD'].includes(request.method)) return new Response('Method not allowed',{status:405})
 const file=assets[url.pathname==='/'?'/index.html':url.pathname]
 if(!file) return new Response('页面不存在',{status:404,headers:{'Content-Type':'text/plain;charset=utf-8'}})
 const bytes=Uint8Array.from(atob(file.body),c=>c.charCodeAt(0))
 return new Response(request.method==='HEAD'?null:bytes,{headers:{'Content-Type':file.type,'Cache-Control':url.pathname.startsWith('/assets/')?'public,max-age=31536000,immutable':'no-cache','X-Content-Type-Options':'nosniff','Referrer-Policy':'strict-origin-when-cross-origin'}})
} }
