export function buildZhihuQuery(text,article={}) {
 const parts=[article.title,article.author,article.dynasty,text]
 return [...new Set(parts.filter(v=>typeof v==='string' && v.trim()).map(v=>v.trim()))].join(' ').slice(0,100)
}
export function discussionCategory(item) {
 const type=String(item.ContentType || item.type || '').toLowerCase(), url=item.Url || item.url || ''
 if(['question','问题','提问'].includes(type)) return 'question'
 if(['article','column','文章','专栏'].includes(type) || url.includes('/p/')) return 'column'
 if(['people','person','user','人物','用户'].includes(type) || /\/(people|org)\//.test(url)) return 'person'
 if(/\/question\/[^/]+\/?$/.test(url)) return 'question'
 return 'discussion'
}
export function demoDiscussions(text,article={}) {
 const title=article.title || '当前篇目', focus=(text || title).slice(0,32)
 const items=[
  {category:'discussion',title:`怎样理解“${focus}”？`,excerpt:'演示：这里将呈现围绕选文的回答摘录。真实检索会由知乎接口返回内容与出处。'},
  {category:'question',title:`《${title}》的表达与思想有什么关联？`,excerpt:'演示：问题分类用于继续追问文本背后的背景和思想。'},
  {category:'column',title:`从篇章结构读《${title}》`,excerpt:'演示：这里展示长文与专栏类检索结果的排版。'},
  {category:'person',title:article.author || '篇目作者',excerpt:`演示：当前检索上下文包含${article.author || '作者'}、${article.dynasty || '时代'}与《${title}》。人物分类仅显示接口实际返回的用户或机构主页，不等同于历史人物百科。`},
 ].map((i,n)=>({...i,id:`demo-${n}`,url:null,author:'演示示例',stats:'无真实互动数据'}))
 return {query:buildZhihuQuery(text,article),items,related_questions:items.filter(i=>i.category==='question').map(i=>({title:i.title,url:null})),source_mode:'mock'}
}
