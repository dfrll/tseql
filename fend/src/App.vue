<script setup>
import { ref } from 'vue'

const messages = ref([])
const input = ref('')
const isSending = ref(false)

function getConversationId() {
  let id = localStorage.getItem('conversation_id')

  if (!id) {
    id = crypto.randomUUID()
    localStorage.setItem('conversation_id', id)
  }

  return id
}

async function send() {
  const text = input.value.trim()

  if (!text || isSending.value) return

  messages.value.push({
    id: crypto.randomUUID(),
    type: 'text',
    text,
    from: 'user',
  })

  input.value = ''
  isSending.value = true

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        conversation_id: getConversationId(),
        text,
      }),
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.error || `Server error: ${response.status}`)
    }

    if (data.reply) {
      messages.value.push({
        id: crypto.randomUUID(),
        type: 'text',
        text: data.reply,
        from: 'system',
      })
    }

    if (data.table) {
      messages.value.push({
        id: crypto.randomUUID(),
        type: 'table',
        from: 'system',
        table: data.table,
      })
    }
  } catch (error) {
    console.error('Send failed:', error)

    messages.value.push({
      id: crypto.randomUUID(),
      type: 'text',
      text: error.message || 'Something went wrong while sending the message.',
      from: 'system',
    })
  } finally {
    isSending.value = false
  }
}
</script>

<template>
  <div class="container">
    <aside class="side-list">
      <p></p>
    </aside>

    <main class="chat-container">
      <div class="chat-scroll">
        <div class="chat-column">
          <div class="chat-messages">
            <div v-for="msg in messages" :key="msg.id" class="bubble" :class="msg.from">
              <!-- Text message -->
              <template v-if="msg.type === 'text'">
                {{ msg.text }}
              </template>

              <!-- Table message -->
              <template v-else-if="msg.type === 'table' && msg.table">
                <div class="table-container">
                  <div class="table-scroll-inner">
                    <table>
                      <thead>
                        <tr>
                          <th v-for="column in msg.table.columns" :key="column">
                            {{ column }}
                          </th>
                        </tr>
                      </thead>

                      <tbody>
                        <tr v-for="(row, rowIndex) in msg.table.rows" :key="rowIndex">
                          <td v-for="column in msg.table.columns" :key="column">
                            {{ row[column] }}
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>

                  <p class="row-count">
                    Showing {{ msg.table.preview_count }}
                    of {{ msg.table.row_count }} rows
                  </p>
                </div>
              </template>
            </div>
          </div>
        </div>
      </div>

      <input v-model="input" class="chat-input" type="text" placeholder="Message..." :disabled="isSending"
        @keydown.enter.prevent="send" />
    </main>
  </div>
</template>



<style>
:root {
  --primary: #3a76f0;
  --primary-soft: #e8effe;
  --primary-glow: rgba(58, 118, 240, 0.35);

  /* Backgrounds */
  --bg-main: #f6f7fb;
  --surface: #ffffff;

  /* Bubbles */
  --bubble-system: #eef0f4;
  --bubble-user: #e6efff;
  --bubble-border: #d7dbe6;

  /* Text */
  --text-system: #1f2937;
  --text-user: #0f172a;
  --text-muted: #6b7280;

  /* Tables */
  --table-border: #d1d5db;
  --table-header: #f3f4f6;
  --table-row-even: #fafafa;

  /* Input */
  --input-bg: #ffffff;
  --input-border: #d1d5db;
  --input-focus: var(--primary);

  --font-size: 12px;
}

/* --- Layout --- */
.container {
  display: flex;
  margin: 20px auto;
  height: 90vh;
  color: var(--text-system);
}

.side-list {
  width: 20%;
  flex-shrink: 0;
}

.chat-container {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;

  background: var(--bg-main);
  border: 1px solid var(--bubble-border);
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
}

.chat-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.chat-column {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* --- Chat messages --- */
.chat-messages {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* --- Chat bubbles --- */
.bubble {
  max-width: 60%;
  padding: 14px 18px;
  border-radius: 16px;
  line-height: 1.5;
  word-wrap: break-word;
  font-size: var(--font-size);
}

.bubble.system {
  align-self: flex-start;
  background: var(--bubble-system);
  border: 1px solid var(--bubble-border);
  color: var(--text-system);
}

.bubble.user {
  align-self: flex-end;
  background: var(--bubble-user);
  color: var(--text-user);
  border: 1px solid rgba(58, 118, 240, 0.25);
}

/* --- Table --- */
.table-container {
  max-width: 100%;
  overflow-x: auto;
  padding: 20px;
  border-radius: 16px;
  background: var(--surface);
  border: 1px solid var(--table-border);
}

.table-scroll-inner {
  min-width: 100%;
}

.table-container table {
  width: max-content;
  border-collapse: collapse;
}

.table-container th,
.table-container td {
  border: 1px solid var(--table-border);
  padding: 8px 12px;
  text-align: left;
  font-size: var(--font-size);
}

.table-container th {
  background-color: var(--table-header);
  font-weight: 600;
}

.table-container tbody tr:nth-child(even) {
  background-color: var(--table-row-even);
}

.row-count {
  margin-top: 6px;
  font-size: 0.8em;
  color: #666;
}

/* --- Chat input --- */
.chat-input {
  height: 60px;
  padding: 14px 16px;

  outline: none;
  box-shadow: 0 0 12px rgba(56, 189, 248, 0.35);

  border: 0px;
  border-radius: 16px;
  font-size: var(--font-size);
  box-sizing: border-box;
}
</style>