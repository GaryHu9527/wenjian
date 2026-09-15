<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import AiSettings from './components/AiSettings.vue'
import { aiSession } from './services/aiSession'
import AppLayout from './components/AppLayout.vue'
import TopNavbar from './components/TopNavbar.vue'
import ArticleSidebar from './components/ArticleSidebar.vue'
import ReaderPanel from './components/ReaderPanel.vue'
import KnowledgeSidebar from './components/KnowledgeSidebar.vue'
import { articles } from './data/articles'
import { analyzeText, apiRequest, searchZhihu } from './services/api'
import { readStored, writeStored } from './services/storage'
const settings = ref(readStored('wenjian-settings', { theme: 'dark', fontSize: 22, engine: 'reference' }, d => d && ['dark','light'].includes(d.theme) && [18,20,22,24,26,28].includes(d.fontSize) && ['reference','ai'].includes(d.engine)))
settings.value.engine = 'reference'
settings.value.discussionMode = settings.value.discussionMode === 'mock' ? 'mock' : 'live'
const discussionSource = ref('zhihu')
const historyIds = readStored('wenjian-reading-history', [], d => Array.isArray(d) && d.every(x => typeof x === 'string'))
const currentArticle = ref(articles.find(a => a.id === historyIds[0]) || articles[0]), readingHistory = ref(historyIds.map(id => articles.find(a => a.id === id)).filter(Boolean))
const selectedText = ref(''), selectedMode = ref('knowledge'), selectedQuestion = ref(''), zhihuResults = ref([]), isLoading = ref(false), zhihuError = ref(''), error = ref(''), analysisResult = ref(null), isAnalyzing = ref(false), searchQuery = ref(''), layout = ref(null)
const deletedNote = ref(null)
const toast = ref(''), modal = ref(null), modalKind = ref('notes'), noteDraft = ref(''), noteQuote = ref(''), editingId = ref(null), noteArticleId = ref(currentArticle.value.id), serviceStatus = ref(null), checking = ref(false)
const notes = ref(readStored('wenjian-notes', [], d => Array.isArray(d) && d.every(n => n && typeof n.id === 'string' && typeof n.body === 'string' && typeof n.quote === 'string' && articles.some(a => a.id === n.articleId))))
const filteredArticles = computed(() => { const q = searchQuery.value.trim().toLowerCase(); return q ? articles.filter(a => `${a.title}${a.author}${a.dynasty}${a.content.join('')}`.toLowerCase().includes(q)) : articles })
const articleIndex = computed(() => articles.findIndex(a => a.id === currentArticle.value.id))
const currentNotes = computed(() => notes.value.filter(n => !searchQuery.value || `${n.title}${n.quote}${n.body}`.includes(searchQuery.value)))
let analysisController, zhihuController, requestId = 0, zhihuId = 0, toastTimer
function notify(message) { toast.value = message; clearTimeout(toastTimer); toastTimer = setTimeout(() => toast.value = '', 4000) }
function persist(key, value) { if (!writeStored(key, value)) notify('浏览器未能保存数据，请导出笔记备份。') }
function saveHistory(article) { readingHistory.value = [article, ...readingHistory.value.filter(a => a.id !== article.id)].slice(0, articles.length); persist('wenjian-reading-history', readingHistory.value.map(a => a.id)) }
async function loadZhihuContent() {
 zhihuController?.abort(); zhihuController = new AbortController(); const id = ++zhihuId
 isLoading.value = true; zhihuError.value = ''; zhihuResults.value = []
 try { const result = await searchZhihu(selectedText.value, currentArticle.value, zhihuController.signal, settings.value.discussionMode); if(id === zhihuId) { discussionSource.value = result.sourceMode; zhihuResults.value = result.items } }
 catch(e) { if(id === zhihuId && e.code !== 'ERR_CANCELED') zhihuError.value = e.message }
 finally { if(id === zhihuId) isLoading.value = false }
}
async function loadAnalysis(mode) {
 analysisController?.abort(); analysisController = new AbortController(); const id = ++requestId
 analysisResult.value = null; error.value = ''; isAnalyzing.value = true
 try { const result = await analyzeText(selectedText.value || currentArticle.value.content[0], mode, currentArticle.value.content.join('\n'), currentArticle.value, settings.value.engine, analysisController.signal); if(id === requestId) analysisResult.value = result }
 catch(e) { if(id === requestId && e.code !== 'ERR_CANCELED') error.value = e.message }
 finally { if(id === requestId) isAnalyzing.value = false }
}
function handleTool(mode) {
 if(mode === 'note') { openNote(); return }
 selectedMode.value = mode; error.value = ''; selectedQuestion.value = ''; layout.value?.openPanel('right')
 if(['word','grammar','translation','knowledge'].includes(mode)) loadAnalysis(mode)
 else { analysisController?.abort(); ++requestId; isAnalyzing.value = false }
 if(mode === 'zhihu') loadZhihuContent()
}
function selectArticle(article) {
 analysisController?.abort(); zhihuController?.abort(); ++requestId; ++zhihuId
 currentArticle.value = article; selectedText.value = ''; selectedQuestion.value = ''; selectedMode.value = 'knowledge'; zhihuResults.value = []; zhihuError.value = ''; isLoading.value = false; saveHistory(article); layout.value?.closePanel(); loadAnalysis('knowledge')
}
function navigateArticle(direction) { const a = articles[articleIndex.value + (direction === 'next' ? 1 : -1)]; if(a) selectArticle(a) }
function chooseQuestion(question) { selectedMode.value = 'chat'; selectedQuestion.value = question; if (!selectedText.value) selectedText.value = currentArticle.value.content[0]; layout.value?.openPanel('right') }
function selectText(text) { selectedText.value = text; selectedQuestion.value = '' }
async function showModal(kind) { modalKind.value = kind; await nextTick(); if(!modal.value.open) modal.value.showModal() }
function openNote(note) { editingId.value = note?.id || null; noteDraft.value = note?.body || ''; noteQuote.value = note?.quote ?? selectedText.value; noteArticleId.value = note?.articleId || currentArticle.value.id; showModal('edit') }
function saveNote() {
 if (!noteDraft.value.trim() && !noteQuote.value.trim()) return
 const article = articles.find(a => a.id === noteArticleId.value)
 const note = { id: editingId.value || crypto.randomUUID(), articleId: article.id, title: article.title, quote: noteQuote.value.trim(), body: noteDraft.value.trim(), updatedAt: new Date().toISOString() }
 notes.value = [note, ...notes.value.filter(n => n.id !== note.id)]; persist('wenjian-notes', notes.value); modalKind.value = 'notes'; notify('笔记已保存在此浏览器')
}
function removeNote(id) { deletedNote.value = notes.value.find(n => n.id===id); notes.value = notes.value.filter(n => n.id !== id); persist('wenjian-notes', notes.value); notify('笔记已删除') }
function restoreNote() { if(deletedNote.value) { notes.value = [deletedNote.value, ...notes.value]; persist('wenjian-notes', notes.value); deletedNote.value = null; notify('笔记已恢复') } }
function exportNotes() {
 const text = notes.value.map(n => `# ${n.title}\n\n> ${n.quote.replaceAll('\n','\n> ')}\n\n${n.body}\n\n${n.updatedAt.slice(0,10)}`).join('\n\n---\n\n')
 const url = URL.createObjectURL(new Blob([text], { type: 'text/markdown;charset=utf-8' })); const a = document.createElement('a'); a.href = url; a.download = '文鉴阅读笔记.md'; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000); notify('已导出阅读笔记')
}
async function checkServices() { checking.value = true; try { serviceStatus.value = await apiRequest('/api/health') } catch { serviceStatus.value = { unreachable: true } } finally { checking.value = false } }
function navigate(view) { if(view === 'notes') showModal('notes'); else if(view === 'settings') { showModal('settings'); checkServices() } else if(view === 'explore') handleTool('knowledge'); else { modal.value?.close(); layout.value?.closePanel() } }
watch(settings, value => { document.documentElement.dataset.theme = value.theme; document.documentElement.style.setProperty('--reader-font', `${value.fontSize}px`); persist('wenjian-settings', value) }, { deep: true, immediate: true })
watch(() => settings.value.discussionMode, () => { if(selectedMode.value === 'zhihu') loadZhihuContent() })
watch(() => settings.value.engine, () => { if(['word','grammar','translation','knowledge'].includes(selectedMode.value)) loadAnalysis(selectedMode.value) })
onMounted(() => { saveHistory(currentArticle.value); loadAnalysis('knowledge') })
</script>
<template>
<AppLayout ref="layout">
 <template #top><TopNavbar v-model="searchQuery" :search-results="filteredArticles" @navigate="navigate" @select="selectArticle($event); searchQuery=''" /></template>
 <template #left><ArticleSidebar :articles="filteredArticles" :history="readingHistory" :current-article="currentArticle" :searching="!!searchQuery.trim()" :note-count="notes.length" @select="selectArticle" @notes="showModal('notes')" /></template>
 <ReaderPanel :article="currentArticle" :previous-article="articles[articleIndex-1]" :next-article="articles[articleIndex+1]" :article-position="articleIndex+1" :article-total="articles.length" @select-text="selectText" @select-tool="handleTool" @navigate="navigateArticle" />
 <template #right><KnowledgeSidebar :selected-text="selectedText" :selected-mode="selectedMode" :selected-question="selectedQuestion" :analysis-result="analysisResult" :analyzing="isAnalyzing" :results="zhihuResults" :loading="isLoading" :error="error" :zhihu-error="zhihuError" :article="currentArticle" :engine="settings.engine" :discussion-source="discussionSource" @select-mode="handleTool" @select-question="chooseQuestion" @note="openNote()" @retry="handleTool(selectedMode)" /></template>
</AppLayout>
<Transition name="toast"><div v-if="toast" class="toast" role="status">{{ toast }}<button v-if="deletedNote && toast==='笔记已删除'" @click="restoreNote">撤销</button></div></Transition>
<dialog ref="modal" class="app-dialog" aria-labelledby="modal-title" @click="e => { if(e.target === modal) modal.close() }">
 <div class="dialog-head"><h2 id="modal-title">{{ modalKind === 'settings' ? '阅读设置' : modalKind === 'edit' ? (editingId ? '编辑笔记' : '记录此刻的理解') : '我的笔记' }}</h2><button class="icon-button" aria-label="关闭弹窗" @click="modal.close()">×</button></div>
 <template v-if="modalKind==='notes'">
  <p class="muted">笔记保存在当前浏览器，不会自动同步到其他设备。共 {{ notes.length }} 条。</p>
  <div class="dialog-actions"><button class="primary" @click="openNote()">＋ 新建笔记</button><button :disabled="!notes.length" @click="exportNotes">导出 Markdown</button></div>
  <div v-if="!currentNotes.length" class="empty-state"><span>✎</span><h3>{{ notes.length ? '没有匹配的笔记' : '留下你的第一条笔记' }}</h3><p>划选原文，或点击“新建笔记”，记录字词、疑问和感悟。</p></div>
  <article v-for="note in currentNotes" :key="note.id" class="note-card"><div class="note-meta"><b>{{ note.title }}</b><time>{{ new Date(note.updatedAt).toLocaleDateString('zh-CN') }}</time></div><blockquote v-if="note.quote">{{ note.quote }}</blockquote><p>{{ note.body }}</p><div class="note-actions"><button @click="selectArticle(articles.find(a=>a.id===note.articleId)); modal.close()">回到原文</button><button @click="openNote(note)">编辑</button><button @click="removeNote(note.id)">删除</button></div></article>
 </template>
 <form v-else-if="modalKind==='edit'" @submit.prevent="saveNote">
  <label class="field">篇目<select v-model="noteArticleId"><option v-for="article in articles" :key="article.id" :value="article.id">{{ article.title }}</option></select></label>
  <label class="field">原文摘录<textarea v-model="noteQuote" rows="3" maxlength="2000" placeholder="摘录你想记住的原文" /></label>
  <label class="field">我的理解<textarea v-model="noteDraft" rows="5" maxlength="10000" placeholder="写下理解、疑问或联想……" /></label>
  <div class="dialog-actions"><button class="primary" :disabled="!noteDraft.trim() && !noteQuote.trim()">保存笔记</button><button type="button" @click="modalKind='notes'">返回笔记</button></div>
 </form>
 <template v-else>
  <label class="field">外观<select v-model="settings.theme"><option value="dark">墨色 · 深色</option><option value="light">纸白 · 浅色</option></select></label>
  <label class="field">原文字号 <span>{{ settings.fontSize }} px</span><input v-model.number="settings.fontSize" type="range" min="18" max="28" step="2" /></label>
  <label class="field">分析与问答<select v-model="settings.engine"><option value="reference">篇目资料 · 无需外部服务</option><option value="ai" :disabled="!aiSession && !serviceStatus?.ai_available">AI 服务 {{ aiSession || serviceStatus?.ai_available ? '· 已配置' : '· 尚未就绪' }}</option></select></label>
  <AiSettings @enabled="settings.engine='ai'" @cleared="settings.engine='reference'" />
  <label class="field">讨论内容<select v-model="settings.discussionMode"><option value="live">知乎实时检索</option><option value="mock">演示数据 · 无需密钥</option></select></label>
  <p class="muted">篇目资料提供段落译文、重点字词、语法和主题问答。AI 模式用于更自由的问题。</p>
  <div class="service-status" role="status"><p>阅读与笔记：可用</p><p>AI：{{ aiSession ? '页面密钥已启用' : checking ? '正在检查…' : serviceStatus?.ai_available ? '已配置' : '未配置，当前使用篇目资料' }}</p><p>知乎：{{ checking ? '正在检查…' : serviceStatus?.zhihu_available ? '已配置，实际检索受服务配额限制' : '可通过搜索入口查看' }}</p><p v-if="serviceStatus?.unreachable">远程服务暂时不可达，本地阅读不受影响。</p><button @click="checkServices" :disabled="checking">重新检查</button></div>
 </template>
</dialog>
</template>
