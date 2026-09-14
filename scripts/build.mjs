import { build } from 'vite'
import { readdir, readFile, writeFile, mkdir, rm, copyFile } from 'node:fs/promises'
import path from 'node:path'
await rm('dist',{recursive:true,force:true})
await build({build:{outDir:'dist/client'}})
const mime={'.html':'text/html;charset=utf-8','.js':'text/javascript;charset=utf-8','.css':'text/css;charset=utf-8','.svg':'image/svg+xml','.png':'image/png','.ico':'image/x-icon'}
const assets={}
async function walk(dir){for(const item of await readdir(dir,{withFileTypes:true})){const file=path.join(dir,item.name);if(item.isDirectory()) await walk(file);else {const key='/'+path.relative('dist/client',file).split(path.sep).join('/');assets[key]={type:mime[path.extname(file)]||'application/octet-stream',body:(await readFile(file)).toString('base64')}}}}
await walk('dist/client')
await writeFile('server/assets.generated.js',`export const assets=${JSON.stringify(assets)};\n`)
await build({configFile:false,publicDir:false,build:{ssr:'server/worker.js',outDir:'dist/server',emptyOutDir:true,rollupOptions:{output:{entryFileNames:'index.js'}}}})
await mkdir('dist/.openai',{recursive:true})
await copyFile('.openai/hosting.json','dist/.openai/hosting.json')
console.log('Built frontend and self-contained Worker.')
