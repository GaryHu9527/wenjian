import test from 'node:test'
import assert from 'node:assert/strict'
import { studyArticles } from '../src/data/studyArticles.js'
import { analyzeLocal, answerLocal } from '../src/services/study.js'
import { handleApi } from '../server/api.js'
import worker from '../dist/server/index.js'
const req=(path,payload)=>new Request(`https://wenjian.example${path}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)})
test('every article has its own complete reading layers and reference answers',()=>{
 for(const a of studyArticles){assert.ok(a.source.startsWith('https://'));assert.equal(a.translation.length,a.content.length);assert.ok(a.notes.length && a.grammar.length && a.appreciation.length);for(const [text,translation] of a.rows){assert.equal(analyzeLocal(text,'translation',a).literal,translation)};for(const q of a.questions){const answer=answerLocal(q,a.content[0],a);assert.equal(answer.supported,true);assert.ok(answer.answer.length>20)}}
})
test('unmatched grammar and word selections never get another article’s fabricated examples',()=>{
 const a=studyArticles.find(a=>a.id==='xiaoyao');const d=analyzeLocal('北冥有鱼','grammar',a);assert.equal(d.patterns.length,0);assert.ok(!JSON.stringify(d).includes('吾谁与归'));assert.equal(answerLocal('明天会下雨吗？','北冥有鱼',a).supported,false)
})
test('fronted object example and reference scope are explicit',()=>{
 const a=studyArticles[0];assert.equal(analyzeLocal('吾谁与归','grammar',a).patterns[0].order,'吾与谁归');assert.match(analyzeLocal('吾谁与归','translation',a).range_note,/段落/)
})
test('API rejects malformed input and reports unconfigured services honestly',async()=>{
 for(const body of [[],null,{text:4,mode:'grammar'},{text:'吾谁与归',mode:'invalid'},{text:'吾谁与归',mode:'grammar',article:[]}]){const r=await handleApi(req('/api/analyze',body),{});assert.equal(r.status,400)}
 const health=await (await handleApi(new Request('https://wenjian.example/api/health'),{})).json();assert.equal(health.data.ai_available,false)
 const ai=await handleApi(req('/api/chat',{question:'为什么？',selected_text:'吾谁与归',engine:'ai'}),{});assert.equal(ai.status,503)
 const zhihu=await handleApi(req('/api/zhihu/search',{text:'岳阳楼记'}),{});assert.equal(zhihu.status,503)
})
test('same-origin API requests and local reading work through the production Worker',async()=>{
 const r=await worker.fetch(new Request('https://wenjian.example/'),{});assert.equal(r.status,200);assert.match(await r.text(),/文鉴/)
 for(const a of studyArticles){const r=await worker.fetch(req('/api/analyze',{text:a.content[0],mode:'translation',article:{id:a.id}}),{});assert.equal(r.status,200);assert.equal((await r.json()).data.literal,a.translation[0])}
 const bad=await handleApi(new Request('https://wenjian.example/api/chat',{method:'POST',headers:{Origin:'https://evil.example'},body:'{}'}),{});assert.equal(bad.status,403)
})
test('real AI chat includes actual question and history, and invalid responses are rejected',async()=>{
 const original=globalThis.fetch, requests=[]
 const env={AI_API_KEY:'test-key',AI_BASE_URL:'https://ai.example/v1',AI_MODEL:'test-model'}
 try{globalThis.fetch=async(url,options)=>{requests.push(JSON.parse(options.body));return Response.json({choices:[{message:{content:JSON.stringify({answer:'谁是介词与的宾语。',related_questions:[]})}}]})};
 const r=await handleApi(req('/api/chat',{question:'谁作什么成分？',selected_text:'吾谁与归',context:'微斯人，吾谁与归？',engine:'ai',history:[{role:'user',text:'先前的问题'}]}),env);assert.equal(r.status,200);assert.equal(requests[0].messages.at(-1).content,'谁作什么成分？');assert.ok(requests[0].messages.some(m=>m.content==='先前的问题'))
 globalThis.fetch=async()=>Response.json({choices:[{message:{content:'{"items":"invalid"}'}}]});const invalid=await handleApi(req('/api/analyze',{text:'吾谁与归',mode:'word',engine:'ai'}),env);assert.equal(invalid.status,502)
 }finally{globalThis.fetch=original}
})
test('Zhihu quota errors become a retryable error and are not disguised as real content',async()=>{
 const original=globalThis.fetch;try{globalThis.fetch=async()=>Response.json({Code:1001,Message:'rate limit exceeded'});const r=await handleApi(req('/api/zhihu/search',{text:'岳阳楼记'}),{ZHIHU_API_KEY:'test'});assert.equal(r.status,429);assert.equal((await r.json()).error.code,'ZHIHU_RATE_LIMITED')}finally{globalThis.fetch=original}
})

test('project brief: corpus alias, context-aware query and four-category demo work without keys',async()=>{
 const article={id:'yueyang',title:'岳阳楼记',author:'范仲淹',dynasty:'北宋'}
 const corpus=await handleApi(req('/api/corpus',{query:'先天下之忧而忧',article}),{});assert.equal(corpus.status,200);const items=(await corpus.json()).data.items;assert.ok(items.some(i=>i.title==='孟子·尽心上'));assert.ok(items.every(i=>i.id!=='yueyang'&&i.source.startsWith('https://')))
 const demo=await handleApi(req('/api/zhihu/search',{text:'先天下之忧而忧',article,engine:'mock'}),{});assert.equal(demo.status,200);const data=(await demo.json()).data;assert.equal(data.source_mode,'mock');for(const term of ['岳阳楼记','范仲淹','北宋','先天下之忧而忧'])assert.ok(data.query.includes(term));assert.deepEqual(data.items.map(i=>i.category),['discussion','question','column','person']);assert.ok(data.items.every(i=>!i.url))
})
test('project brief: knowledge analysis actually returns related corpus for the example passage',()=>{
 const data=analyzeLocal('先天下之忧而忧','knowledge',studyArticles[0]);assert.ok(data.corpus.some(i=>i.title==='孟子·尽心上'));assert.ok(data.corpus.every(i=>i.relation_type==='theme'))
})

test('project brief example has meaning, structure, translation and corpus through the API',async()=>{
 const r=await handleApi(req('/api/analyze',{text:'先天下之忧而忧',mode:'comprehensive',article:{id:'yueyang'}}),{});assert.equal(r.status,200);const d=(await r.json()).data;assert.ok(d.word.items.length);assert.ok(d.grammar.patterns.length);assert.ok(d.translation.literal.includes('天下人忧虑'));assert.ok(d.knowledge.corpus.length)
})
