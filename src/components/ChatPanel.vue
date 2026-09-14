<script setup>
import { nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { chatAboutText } from '../services/api'
const props=defineProps({selectedText:String,article:Object,engine:String,initialQuestion:String})
const question=ref(''), messages=ref([]), loading=ref(false), error=ref(''), end=ref(null)
let controller, sequence=0
async function submit(value) {
 const q=(typeof value==='string'?value:question.value).trim()
 if(!props.selectedText || !q || loading.value) return
 controller?.abort(); controller=new AbortController(); const id=++sequence
 loading.value=true; error.value=''; question.value=''
 const user={role:'user',text:q}; messages.value.push(user)
 try { const data=await chatAboutText(q,props.selectedText,props.article.content.join('\n'),props.article,props.engine,controller.signal,messages.value.slice(-10,-1)); if(id===sequence) messages.value.push({role:'assistant',text:data.answer,source:data.source_label || 'AI 生成回答',related:data.related_questions}) }
 catch(e) { if(id===sequence && e.code!=='ERR_CANCELED') { error.value=e.message; question.value=q; messages.value=messages.value.filter(m=>m!==user) } }
 finally { if(id===sequence) { loading.value=false; await nextTick(); end.value?.scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'nearest'}) } }
}
watch(() => [props.article.id, props.selectedText, props.engine], () => { controller?.abort(); ++sequence; messages.value=[]; error.value=''; loading.value=false })
watch(() => props.initialQuestion, q => { if(q) { question.value=q; submit(q) } }, {immediate:true})
onBeforeUnmount(() => { controller?.abort(); ++sequence })
</script>
<template><section class="chat-panel"><h3>围绕原文提问</h3><p class="muted">{{ engine==='ai'?'结合选文与上下文展开讨论。':'可问译文、字词、句式、背景、主旨和结构。回答来自本篇资料。' }}</p><div class="chat-messages" aria-live="polite"><div v-for="(message,i) in messages" :key="i" class="chat-message" :class="message.role"><span>{{ message.role==='user'?'我的问题':message.source }}</span><p>{{ message.text }}</p></div><p v-if="loading" role="status"><span class="spinner"/> 正在整理回答…</p><div ref="end" /></div><form @submit.prevent="submit"><label class="field" for="chat-question">你的问题</label><textarea id="chat-question" v-model="question" :disabled="!selectedText || loading" maxlength="1000" rows="3" placeholder="例如：这句话是什么句式？" @keydown.meta.enter.prevent="submit" @keydown.ctrl.enter.prevent="submit"/><div class="chat-actions"><small>⌘ / Ctrl + Enter 发送</small><button class="primary" :disabled="!selectedText || !question.trim() || loading">{{ loading?'思考中…':'发送问题 ↑' }}</button></div></form><p v-if="error" role="alert" class="error-state">{{ error }}</p><div class="questions"><button v-for="q in article.questions" :key="q" :disabled="loading" @click="submit(q)">{{ q }} ↗</button></div></section></template>
