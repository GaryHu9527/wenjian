import { studyArticles } from '../data/studyArticles.js'
const themes = {
 yueyang:['公共责任','君子','士人理想'], xiaoyao:['自由','寓言','有所待'], quanxue:['学习','积累','修养'],
 hongmen:['历史','处世','政治'], zhuzhiwu:['历史','外交','政治'], loushi:['君子','修养','志趣'], ailian:['君子','修养','志趣'],
}
const supplements=[
 {id:'lunyu-xue',title:'论语·学而篇',author:'孔子及弟子',dynasty:'春秋',text:'学而时习之，不亦说乎？有朋自远方来，不亦乐乎？人不知而不愠，不亦君子乎？',source:'https://zh.wikisource.org/zh-hant/論語/學而第一',tags:['学习','君子','修养']},
 {id:'lunyu-zheng',title:'论语·为政篇',author:'孔子及弟子',dynasty:'春秋',text:'温故而知新，可以为师矣。',source:'https://zh.wikisource.org/zh/論語/爲政第二',tags:['学习','积累']},
 {id:'mengzi',title:'孟子·尽心上',author:'孟子及弟子',dynasty:'战国',text:'穷则独善其身，达则兼善天下。',source:'https://zh.wikisource.org/wiki/孟子/盡心上',tags:['公共责任','修养','士人理想']},
]
export function searchCorpus(query='',{articleId,keywords=[],limit=5}={}) {
 const q=String(query).trim(), explicit=Array.isArray(keywords)?keywords.filter(k=>typeof k==='string' && k.trim()).slice(0,8):[]
 const contextTags=themes[articleId] || []
 const terms=[...new Set([q,...explicit].filter(Boolean))]
 const index=[...studyArticles.map(a=>({id:a.id,title:a.title,author:a.author,dynasty:a.dynasty,text:a.content.join('\n'),source:a.source,tags:themes[a.id]||[]})),...supplements]
 return index.filter(a=>a.id!==articleId).map(a=>{
  const haystack=`${a.title} ${a.author} ${a.dynasty} ${a.text} ${a.tags.join(' ')}`
  const hits=terms.filter(t=>haystack.includes(t)), common=a.tags.filter(t=>contextTags.includes(t))
  return {...a,score:hits.reduce((n,t)=>n+10+Math.min(t.length,30),0)+common.length,relation:hits.length?`关键词匹配：${hits.join('、')}`:`主题关联：${common.join('、')}`,relation_type:hits.length?'keyword':'theme'}
 }).filter(a=>a.score>0).sort((a,b)=>b.score-a.score).slice(0,Math.max(1,Math.min(limit,10)))
}
