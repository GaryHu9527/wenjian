<script setup>
import { computed, onMounted, ref } from 'vue'
import AppLayout from './components/AppLayout.vue'
import TopNavbar from './components/TopNavbar.vue'
import ArticleSidebar from './components/ArticleSidebar.vue'
import ReaderPanel from './components/ReaderPanel.vue'
import KnowledgeSidebar from './components/KnowledgeSidebar.vue'
import { articles } from './data/articles'
import { analyzeText, searchZhihu } from './services/api'
const currentArticle = ref(articles[0]), selectedText = ref(''), selectedMode = ref('zhihu'), selectedQuestion = ref(''), zhihuResults = ref([]), relatedQuestions = ref([]), isLoading = ref(false), error = ref(''), analysisResult = ref(null), isAnalyzing = ref(false)
const readingHistory = ref([])
const searchQuery = ref('')
const explorationText = computed(() => selectedText.value || '')
const filteredArticles = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()
  return query ? articles.filter(article => `${article.title}${article.author}${article.dynasty}`.toLowerCase().includes(query)) : articles
})
const articleIndex = computed(() => articles.findIndex(article => article.id === currentArticle.value.id))
const previousArticle = computed(() => articles[articleIndex.value - 1] || null)
const nextArticle = computed(() => articles[articleIndex.value + 1] || null)
async function loadZhihuContent(text = selectedText.value) { isLoading.value = true; error.value = ''; try { const result = await searchZhihu(text, currentArticle.value); zhihuResults.value = result.items; relatedQuestions.value = result.relatedQuestions } catch { error.value = '知识内容暂时无法加载，请稍后重试。' } finally { isLoading.value = false } }
async function loadAnalysis(mode) { if (!selectedText.value) return; isAnalyzing.value = true; error.value = ''; try { analysisResult.value = await analyzeText(selectedText.value, mode, '', { title: currentArticle.value.title, author: currentArticle.value.author, dynasty: currentArticle.value.dynasty }) } catch { error.value = '文本分析暂时无法加载，请稍后重试。' } finally { isAnalyzing.value = false } }
function handleTool(mode) { selectedMode.value = mode; analysisResult.value = null; if (['word', 'grammar', 'translation', 'knowledge'].includes(mode)) loadAnalysis(mode); if (mode === 'knowledge' || mode === 'zhihu') loadZhihuContent() }
function saveHistory(article) { readingHistory.value = [article, ...readingHistory.value.filter(item => item.id !== article.id)].slice(0, 5); localStorage.setItem('wenjian-reading-history', JSON.stringify(readingHistory.value.map(item => item.id))) }
function selectArticle(article) { currentArticle.value = article; selectedText.value = ''; selectedQuestion.value = ''; selectedMode.value = 'zhihu'; saveHistory(article); loadZhihuContent(article.title) }
function navigateArticle(direction) { const article = direction === 'next' ? nextArticle.value : previousArticle.value; if (article) selectArticle(article) }
function chooseQuestion(question) { selectedQuestion.value = question; selectedMode.value = 'zhihu'; loadZhihuContent(question) }
onMounted(() => { const ids = JSON.parse(localStorage.getItem('wenjian-reading-history') || '[]'); readingHistory.value = ids.map(id => articles.find(article => article.id === id)).filter(Boolean); saveHistory(currentArticle.value); loadZhihuContent() })
</script>
<template><AppLayout><template #top><TopNavbar v-model="searchQuery" /></template><template #left><ArticleSidebar :articles="filteredArticles" :history="readingHistory" :current-article="currentArticle" @select="selectArticle" /></template><ReaderPanel :article="currentArticle" :previous-article="previousArticle" :next-article="nextArticle" :article-position="articleIndex + 1" :article-total="articles.length" @select-text="selectedText = $event" @select-tool="handleTool" @navigate="navigateArticle" /><template #right><KnowledgeSidebar :selected-text="explorationText" :selected-mode="selectedMode" :selected-question="selectedQuestion" :analysis-result="analysisResult" :analyzing="isAnalyzing" :results="zhihuResults" :related-questions="relatedQuestions" :loading="isLoading" :error="error" :article="currentArticle" @select-mode="handleTool" @select-question="chooseQuestion" /></template></AppLayout></template>
<style>.reader-tabs button{border:0;background:transparent;cursor:pointer}.reader-tabs button.active{background:#292929;color:#fff;border-left:2px solid #eee}.article-notes p{font-family:inherit;font-size:16px;letter-spacing:0;line-height:1.7;text-indent:0;padding:12px 15px;margin:10px 0;background:#171717;border-left:2px solid #ddd;border-radius:0 5px 5px 0}.article-translation p,.article-appreciation p{font-family:inherit;font-size:17px;letter-spacing:.2px;line-height:1.85;text-indent:0;color:#ccc}.no-article{padding:16px;color:#888;font-size:13px}.question-selected{margin-top:12px;padding:9px 11px;border-left:2px solid #ddd;background:#181818;color:#ccc;font-size:13px;line-height:1.45}.questions button.selected{color:#fff}</style>
