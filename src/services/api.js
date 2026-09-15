import axios from 'axios'
import { aiHeaders } from './aiSession'
import { analyzeLocal, answerLocal } from './study'
import { safeUrl } from './storage'
const client = axios.create({ timeout: 30000 })
export async function apiRequest(path, payload, signal, headers = {}) {
  try {
    const response = payload === undefined ? await client.get(path, { signal }) : await client.post(path, payload, { signal, headers })
    if (!response.data?.success) throw new Error(response.data?.error?.message || '服务响应异常，请重试。')
    return response.data.data
  } catch (e) {
    if (e.code === 'ERR_CANCELED') throw e
    throw new Error(e.response?.data?.error?.message || (e.code === 'ECONNABORTED' ? '请求超时，请稍后重试。' : e.message === 'Network Error' ? '暂时无法连接服务，请检查网络。' : e.message))
  }
}
export async function analyzeText(text, mode, context, article, engine = 'reference', signal) {
  if (engine === 'reference') return analyzeLocal(text, mode, article)
  return apiRequest('/api/analyze', { text, mode, context, article, engine: 'ai' }, signal, aiHeaders())
}
export async function chatAboutText(question, selectedText, context, article, engine = 'reference', signal, history = []) {
  if (engine === 'reference') return answerLocal(question, selectedText, article)
  return apiRequest('/api/chat', { question, selected_text: selectedText, context, article, history, engine: 'ai' }, signal, aiHeaders())
}
export async function searchZhihu(text, article, signal, discussionMode = 'live') {
  const result = await apiRequest('/api/zhihu/search', { text: text || article.title, article, count: 5, engine: discussionMode === 'mock' ? 'mock' : 'live' }, signal)
  return { items: (result.items || []).map((i, n) => ({ ...i, id: i.id || i.url || n, url: safeUrl(i.url), authorUrl: safeUrl(i.author_url), excerpt: (i.excerpt || '').replace(/<[^>]+>/g, ''), stats: typeof i.stats === 'object' ? `赞同 ${i.stats?.vote_up_count ?? 0} · 评论 ${i.stats?.comment_count ?? 0}` : i.stats || '', category: i.category || (i.url?.includes('/p/') ? 'column' : i.url?.includes('/people/') ? 'person' : 'discussion') })), relatedQuestions: result.related_questions || [], sourceMode: result.source_mode }
}
