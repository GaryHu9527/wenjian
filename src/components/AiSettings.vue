<script setup>
import { ref, onBeforeUnmount } from 'vue'
import { aiSession, aiHeaders, setAiSession } from '../services/aiSession'
import { apiRequest } from '../services/api'
const emit = defineEmits(['enabled', 'cleared'])
const provider = ref(aiSession.value?.provider || 'deepseek'), model = ref(aiSession.value?.model || ''), key = ref('')
const visible = ref(false), busy = ref(false), message = ref(''), failed = ref(false)
let controller
async function connect() {
  message.value = ''; failed.value = false; busy.value = true
  controller = new AbortController()
  const config = { provider: provider.value, model: model.value.trim(), key: key.value.trim() }
  try {
    await apiRequest('/api/chat', { engine: 'ai', question: '仅回答“连接成功”。', selected_text: '学而时习之', context: '' }, controller.signal, aiHeaders(config))
    setAiSession(config); key.value = ''; visible.value = false
    message.value = '连接测试通过，已启用当前页面的 AI。'; emit('enabled')
  } catch (e) { if(e.code !== 'ERR_CANCELED') { failed.value = true; message.value = e.message } }
  finally { busy.value = false }
}
function clear() { controller?.abort(); setAiSession(null); key.value = ''; visible.value = false; message.value = '页面密钥已清除，已切回篇目资料。'; failed.value = false; emit('cleared') }
onBeforeUnmount(() => { controller?.abort(); key.value = '' })
</script>
<template>
<section class="ai-settings" aria-labelledby="ai-settings-title">
<h3 id="ai-settings-title">AI API Key 配置</h3>
<p class="muted">填写你自己的服务密钥。密钥仅保留在当前页面内存，刷新后需重新填写。请求经文鉴后端转发至所选服务商，不写入服务器配置或日志。测试会发起一次可能计费的 AI 请求。</p>
<p v-if="aiSession" class="muted">当前已启用：{{ aiSession.provider }} · {{ aiSession.model }}</p>
<form @submit.prevent="connect">
<fieldset :disabled="busy">
<label class="field">服务商<select v-model="provider"><option value="deepseek">DeepSeek</option><option value="openai">OpenAI</option></select></label>
<p class="muted">服务地址：{{ provider === 'deepseek' ? 'https://api.deepseek.com' : 'https://api.openai.com/v1' }}</p>
<label class="field">模型名称<input v-model="model" required maxlength="128" placeholder="填写服务商控制台中的模型 ID" autocomplete="off" spellcheck="false" /></label>
<label class="field">API Key<input v-model="key" :type="visible ? 'text' : 'password'" required maxlength="512" autocomplete="off" spellcheck="false" placeholder="粘贴该服务商的 API Key" /></label>
<button type="button" :aria-pressed="visible" @click="visible = !visible">{{ visible ? '隐藏密钥' : '显示密钥' }}</button>
<div class="dialog-actions"><button class="primary" :disabled="!key.trim() || !model.trim()">{{ busy ? '正在测试…' : '测试连接并启用' }}</button></div>
</fieldset>
<button type="button" :disabled="!aiSession && !key && !busy" @click="clear">清除页面密钥</button>
</form>
<p v-if="message" :role="failed ? 'alert' : 'status'" class="muted">{{ message }}</p>
</section>
</template>
<style scoped>
.ai-settings{margin:24px 0;padding-top:16px;border-top:1px solid var(--line)}
fieldset{border:0;padding:0;margin:0;min-width:0}
.field input{width:100%;min-width:0;border:1px solid var(--line);border-radius:8px;background:var(--surface);color:var(--ink);padding:11px}
</style>
