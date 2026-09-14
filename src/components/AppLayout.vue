<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
const panel = ref('')
let previousFocus
function openPanel(value) { if(window.innerWidth < 1180) panel.value = value }
function closePanel() { panel.value = '' }
function resize() { if(window.innerWidth>=1180 || panel.value==='left' && window.innerWidth>=800) closePanel() }
function trap(event) {
 if(!panel.value || event.key!=='Tab') return
 const el=document.querySelector(panel.value==='left'?'#article-directory':'#study-sidebar')
 const items=[...el.querySelectorAll('button:not(:disabled),a[href],input,textarea,select,summary')].filter(e=>e.getClientRects().length && getComputedStyle(e).visibility!=='hidden')
 const first=items[0],last=items.at(-1)
 if(event.shiftKey && document.activeElement===first) {event.preventDefault();last?.focus()}
 else if(!event.shiftKey && document.activeElement===last) {event.preventDefault();first?.focus()}
}
watch(panel,async(value,old)=>{if(value){if(!old) previousFocus=document.activeElement;await nextTick();document.querySelector(`${value==='left'?'#article-directory':'#study-sidebar'} .drawer-head button`)?.focus({preventScroll:true})}else{await nextTick();previousFocus?.focus({preventScroll:true})}})
onMounted(()=>window.addEventListener('resize',resize));onBeforeUnmount(()=>window.removeEventListener('resize',resize))
defineExpose({openPanel,closePanel})
</script>
<template><div class="app-layout" @keydown.esc="closePanel" @keydown="trap"><header><slot name="top" /><div class="mobile-actions"><button :aria-expanded="panel==='left'" aria-controls="article-directory" @click="panel=panel==='left'?'':'left'">目录</button><button :aria-expanded="panel==='right'" aria-controls="study-sidebar" @click="panel=panel==='right'?'':'right'">研读</button></div></header><Transition name="shade"><button v-if="panel" class="panel-shade" aria-label="关闭侧栏" tabindex="-1" @click="closePanel" /></Transition><aside id="article-directory" class="left" :class="{mobileOpen:panel==='left'}" :inert="panel==='right'"><div class="drawer-head"><b>篇目目录</b><button aria-label="关闭目录" @click="closePanel">×</button></div><slot name="left" /></aside><main :inert="!!panel"><slot /></main><aside id="study-sidebar" class="right" :class="{mobileOpen:panel==='right'}" :inert="panel==='left'"><div class="drawer-head"><b>研读与探索</b><button aria-label="关闭研读侧栏" @click="closePanel">×</button></div><slot name="right" /></aside></div></template>
