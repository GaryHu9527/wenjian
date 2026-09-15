import { shallowRef } from 'vue'
export const aiSession = shallowRef(null)
export function setAiSession(config) { aiSession.value = config ? { ...config } : null }
export function aiHeaders(config = aiSession.value) {
  return config ? { 'X-AI-Key': config.key, 'X-AI-Provider': config.provider, 'X-AI-Model': config.model } : {}
}
