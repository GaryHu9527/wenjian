import { studyArticles } from '../data/studyArticles.js'
export const MODES = ['word', 'grammar', 'translation', 'knowledge', 'comprehensive']
const clean = value => String(value || '').replace(/[\s，。！？、；：“”‘’？!?,.;:]/g, '')
export function findArticle(article, text = '') {
  return studyArticles.find(a => a.id === article?.id || a.title === article?.title) || studyArticles.find(a => text && clean(a.content.join('')).includes(clean(text)))
}
export function analyzeLocal(text, mode, article) {
  const a = findArticle(article, text)
  if (!a || !clean(text)) throw new Error('请选择书库中的原文。')
  if (!MODES.includes(mode)) throw new Error('不支持的分析类型。')
  if (mode === 'comprehensive') return Object.fromEntries(MODES.filter(m => m !== mode).map(m => [m, analyzeLocal(text, m, a)]))
  const focus = clean(text)
  const rows = a.rows.filter(([original]) => clean(original).includes(focus) || focus.includes(clean(original)))
  const notes = a.notes.filter(n => focus.includes(clean(n.text)))
  const patterns = a.grammar.filter(g => focus.includes(clean(g.text)) || clean(g.text).includes(focus))
  const base = { source_mode: 'reference', source_label: '篇目学习资料', source_url: a.source, matched: rows.length > 0 }
  const rangeNote = rows.length ? '以下为选文所在段落的参考译文，不是选词的逐字翻译。' : '选文跨越段落或不在当前原文中，请缩小选择范围。'
  if (mode === 'word') return { ...base, summary: notes.length ? '选文中的重点字词' : '所选文字暂未收录独立词条，可结合段落译文理解。', items: notes.map(n => ({ ...n, type: '字词注释', confidence: 'reference' })), context_translation: rows.map(r => r[1]).join('\n\n'), range_note: rangeNote }
  if (mode === 'translation') return { ...base, literal: rows.map(r => r[1]).join('\n\n'), natural: '', range_note: rangeNote, original: rows.map(r => r[0]).join('\n\n'), key_points: notes.map(n => ({ text: n.text, explanation: n.meaning })) }
  if (mode === 'grammar') return { ...base, patterns, sentence_pattern: patterns[0]?.pattern || '暂无匹配的句式条目', modern_order: patterns[0]?.order || '', explanation: patterns[0]?.explanation || '这不表示所选文字没有特殊句式。可查看本篇已收录的语法条目，或启用 AI 分析。', available_patterns: a.grammar, components: [] }
  return { ...base, summary: a.background, literary_context: a.appreciation.join('\n\n'), people: [{ name: a.author, description: `《${a.title}》作者署名：${a.author}。` }], keywords: [a.title, a.author, a.dynasty], questions: a.questions }
}
export function answerLocal(question, text, article) {
  const a = findArticle(article, text)
  if (!a) throw new Error('请选择书库中的篇目。')
  const q = question.trim()
  const analysis = analyzeLocal(text || a.content[0], 'comprehensive', a)
  let answer, supported = true
  if (/语法|句式|倒装|前置|后置|省略|活用|判断句|还原/.test(q)) {
    const patterns = analysis.grammar.patterns.length ? analysis.grammar.patterns : a.grammar
    answer = patterns.map(g => `“${g.text}”：${g.pattern}。可按“${g.order}”理解。${g.explanation}`).join('\n\n')
  } else if (/翻译|译文|句意|什么意思|如何理解|怎么理解|怎样理解/.test(q)) {
    answer = `${analysis.translation.range_note}\n\n${analysis.translation.literal || '请在原文中选取一个段落内的文字，再查看对应译文。'}`
  } else if (/字词|词义|释义|读音|怎么读|通假/.test(q)) {
    const matched = a.notes.filter(n => q.includes(n.text))
    const notes = matched.length ? matched : q.includes(a.title) || /本篇|这篇/.test(q) ? a.notes : analysis.word.items.length ? analysis.word.items : a.notes
    answer = notes.map(n => `${n.text}：${n.meaning}`).join('\n')
  } else if (/结构|写法|手法|表达|修辞|安排/.test(q)) answer = a.appreciation.join('\n\n')
  else if (/背景|主旨|主题|思想|作者|为什么|为何/.test(q) && (a.questions.includes(q) || /背景|主旨|主题|思想|作者/.test(q))) answer = `${a.background}\n\n${a.appreciation.join('\n\n')}`
  else {
    const note = a.notes.find(n => q.includes(n.text) && n.text.length > 1)
    if (note) answer = `${note.text}：${note.meaning}`
    else { supported = false; answer = '这道问题超出了当前篇目资料的问答范围，暂时无法据此给出可靠答案。你可以改问下方的篇目问题，或在设置中切换到已配置的 AI 服务。' }
  }
  return { answer, supported, source_mode: 'reference', source_label: '基于篇目资料的检索回答', source_url: a.source, related_questions: a.questions }
}
