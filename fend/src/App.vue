<script setup>
import { ref } from 'vue'

const messages = ref([])
const input = ref("")

async function send() {
  if (!input.value.trim()) return

  const userMsg = input.value
  messages.value.push({ role: 'user', text: userMsg })

  input.value = ''

  function getConversationId() {
    let id = localStorage.getItem("conversation_id");
    if (!id) {
      id = crypto.randomUUID();
      localStorage.setItem("conversation_id", id);
    }
    return id;
  }

  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      conversation_id: getConversationId(),
      text: userMsg
    })
  })

  const data = await res.json()

  messages.value.push({
    role: 'assistant',
    text: data.reply
  })
}
</script>

<template>
  <div>
    <div v-for="(m, i) in messages" :key="i">
      <b>{{ m.role }}:</b> {{ m.text }}
    </div>

    <input v-model="input" @keyup.enter="send" />
    <button @click="send">Send</button>
  </div>
</template>