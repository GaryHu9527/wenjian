<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import TextSelectionToolbar from './TextSelectionToolbar.vue'
const props = defineProps({ article: Object, previousArticle: Object, nextArticle: Object, articlePosition: Number, articleTotal: Number })
const emit = defineEmits(['select-text', 'select-tool', 'navigate', 'note'])
const toolbar = ref(false), position = ref({}), activeTab = ref('original'), readerEl = ref(null), bodyEl = ref(null)
const tabs = [['original','原文'], ['notes','注释'], ['translation','译文'], ['appreciation','赏析']]
const tabContent = computed(() => activeTab.value === 'notes' ? props.article.notes.map(n => `${n.text}：${n.meaning}`) : activeTab.value === 'translation' ? props.article.translation : activeTab.value === 'appreciation' ? [props.article.background, ...props.article.appreciation] : props.article.content)
function onSelect() {
  const s = window.getSelection()
  if (!s?.rangeCount || s.isCollapsed || !bodyEl.value?.contains(s.anchorNode) || !bodyEl.value?.contains(s.focusNode)) { toolbar.value = false; return }
  const text = s.toString().trim()
  if (!text || activeTab.value !== 'original') return
  const rect = s.getRangeAt(0).getBoundingClientRect(), width = Math.min(372, window.innerWidth - 24)
  emit('select-text', text.slice(0, 1000))
  position.value = { left: `${Math.max(12, Math.min(window.innerWidth - width - 12, rect.left + rect.width / 2 - width / 2))}px`, top: `${Math.max(80, Math.min(window.innerHeight - 90, rect.top - 74))}px`, width: `${width}px` }
  toolbar.value = true
}
function choose(mode) { emit('select-tool', mode); toolbar.value = false; window.getSelection()?.removeAllRanges() }
function analyzeParagraph(paragraph) { emit('select-text', paragraph); emit('select-tool', 'translation') }
function close(e) { if (e.key === 'Escape') toolbar.value = false }
function hideToolbar() { toolbar.value = false }
watch(() => props.article.id, async () => { activeTab.value = 'original'; toolbar.value = false; await nextTick(); readerEl.value?.scrollTo({ top: 0 }) })
watch(activeTab, hideToolbar)
onMounted(() => { document.addEventListener('selectionchange', onSelect); document.addEventListener('keydown', close); window.addEventListener('resize', hideToolbar) })
onBeforeUnmount(() => { document.removeEventListener('selectionchange', onSelect); document.removeEventListener('keydown', close); window.removeEventListener('resize', hideToolbar) })
</script>
<template>
<section ref="readerEl" class="reader" @scroll="hideToolbar">
 <div class="reader-inner">
  <div class="breadcrumb">经典选读 <span>/</span> {{ article.dynasty }} <span>/</span> {{ article.title }}</div>
  <div class="title-row"><h1>{{ article.title }}</h1><span class="edition">{{ article.edition }}</span></div>
  <div class="author">{{ article.author }} · {{ article.dynasty }}</div>
  <div class="reader-tabs" role="tablist" aria-label="阅读内容">
   <button v-for="[key,label] in tabs" :key="key" :id="`tab-${key}`" role="tab" :aria-selected="activeTab === key" aria-controls="reading-content" :class="{active:activeTab===key}" @click="activeTab=key" @keydown.right.prevent="activeTab=tabs[(tabs.findIndex(t=>t[0]===activeTab)+1)%tabs.length][0]; $nextTick(() => $el.querySelector('#tab-'+activeTab)?.focus())" @keydown.left.prevent="activeTab=tabs[(tabs.findIndex(t=>t[0]===activeTab)+tabs.length-1)%tabs.length][0]; $nextTick(() => $el.querySelector('#tab-'+activeTab)?.focus())">{{ label }}</button>
  </div>
  <p class="hint">{{ activeTab === 'original' ? '划选文字即可释义、翻译或提问，也可点击段落旁的“研读”。' : '译注为学习参考，可通过页末的原典链接核对文字。' }}</p>
  <Transition name="reading" mode="out-in">
   <article ref="bodyEl" id="reading-content" :key="article.id + activeTab" role="tabpanel" :aria-labelledby="`tab-${activeTab}`" :class="`article-${activeTab}`">
    <div v-for="(paragraph,index) in tabContent" :key="index" class="paragraph"><p>{{ paragraph }}</p><button v-if="activeTab==='original'" class="paragraph-tool" :aria-label="`研读第 ${index+1} 段`" @click="analyzeParagraph(paragraph)">研读 <span aria-hidden="true">↗</span></button></div>
   </article>
  </Transition>
  <div class="source-line"><a :href="article.source" target="_blank" rel="noopener noreferrer">查阅原典 ↗</a><span>古文原文 · 现代译注为本站整理</span></div>
  <footer class="article-pager"><button :disabled="!previousArticle" @click="emit('navigate','previous')">‹ 上一篇</button><span>{{ articlePosition }} / {{ articleTotal }}</span><button :disabled="!nextArticle" @click="emit('navigate','next')">下一篇 ›</button></footer>
 </div>
 <TextSelectionToolbar :visible="toolbar" :position="position" @tool="choose" />
</section>
</template>
