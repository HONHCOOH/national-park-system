import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useChatStore = defineStore('chat', () => {
  const messages = ref([])
  const loading = ref(false)

  function addMessage(role, content) {
    messages.value.push({
      role,
      content,
      time: new Date().toLocaleTimeString(),
    })
  }

  function clearMessages() {
    messages.value = []
  }

  return { messages, loading, addMessage, clearMessages }
})
