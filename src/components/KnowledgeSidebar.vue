<script setup>
import { computed, ref } from 'vue'
import ZhihuPanel from './ZhihuPanel.vue'
import WordPanel from './WordPanel.vue'
import GrammarPanel from './GrammarPanel.vue'
import TranslationPanel from './TranslationPanel.vue'
import KnowledgePanel from './KnowledgePanel.vue'
import { buildZhihuQuery } from '../services/discussion'
import ChatPanel from './ChatPanel.vue'
const props = defineProps({ selectedText:String, selectedMode:String, selectedQuestion:String, analysisResult:Object, analyzing:Boolean, results:Array, loading:Boolean, error:String, zhihuError:String, article:Object, engine:String, discussionSource:String })
defineEmits(['select-mode','select-question','note','retry'])
const category=ref('all'), tabs=[['word','释义'],['grammar','语法'],['translation','译文'],['knowledge','知识'],['chat','提问'],['zhihu','讨论']]
const categoryResults=computed(() => (props.results || []).filter(i => category.value==='all' || i.category===category.value || category.value==='question' && i.category==='question'))
</script>
<template><div class="knowledge-sidebar"><div class="study-head"><div><span class="eyebrow">读懂文字背后的世界</span><h2>研读与探索</h2></div><span class="engine-badge">{{ engine==='ai'?'AI 分析':'篇目资料' }}</span></div><div class="exploration"><span>{{ selectedText?'当前选文':'当前篇目' }}</span><blockquote>{{ selectedText || article.title }}</blockquote><button v-if="selectedText" class="text-button" @click="$emit('note')">＋ 存为笔记</button></div><div class="study-tabs" aria-label="研读工具"><button v-for="[key,label] in tabs" :key="key" :aria-pressed="selectedMode===key" :class="{active:selectedMode===key}" :disabled="!selectedText && ['word','grammar','translation','chat'].includes(key)" @click="$emit('select-mode',key)">{{ label }}</button></div><p v-if="!selectedText" class="hint">先划选原文，或点击段落旁的“研读”。</p>
<div v-if="analyzing" class="skeleton" role="status"><span class="spinner" /> 正在分析…<i/><i/><i/></div>
<div v-else-if="error && selectedMode!=='zhihu'" class="error-state" role="alert"><p>{{ error }}</p><button @click="$emit('retry')">重新尝试</button></div>
<Transition v-else name="panel" mode="out-in"><div :key="selectedMode">
<template v-if="selectedMode==='zhihu'"><div class="discussion-heading"><h3>知乎相关讨论</h3><select v-model="category" aria-label="讨论类型"><option value="all">全部内容</option><option value="discussion">相关讨论</option><option value="question">相关问题</option><option value="column">专栏文章</option><option value="person">人物主页</option></select></div><ZhihuPanel :results="categoryResults" :loading="loading" :error="zhihuError" :query="buildZhihuQuery(selectedText, article)" :source-mode="discussionSource" @retry="$emit('retry')" /></template>
<WordPanel v-else-if="selectedMode==='word'" :selected-text="selectedText" :result="analysisResult" />
<GrammarPanel v-else-if="selectedMode==='grammar'" :selected-text="selectedText" :result="analysisResult" />
<TranslationPanel v-else-if="selectedMode==='translation'" :selected-text="selectedText" :result="analysisResult" />
<ChatPanel v-else-if="selectedMode==='chat'" :selected-text="selectedText" :article="article" :engine="engine" :initial-question="selectedQuestion" />
<KnowledgePanel v-else :selected-text="selectedText" :result="analysisResult" />
</div></Transition>
<section v-if="selectedMode!=='chat'" class="questions"><h3>继续想一想</h3><button v-for="question in article.questions" :key="question" @click="$emit('select-question',question)">{{ question }} <span aria-hidden="true">↗</span></button></section><p class="sidebar-footnote">阅读资料用于辅助理解；遇到异文，请以原典和所用教材为准。</p></div></template>
