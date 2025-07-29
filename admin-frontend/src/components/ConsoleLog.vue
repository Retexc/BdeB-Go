<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'

const logs     = ref('')
let   logTimer = null

async function updateLogs() {
  try {
    const resp = await fetch('/admin/logs_data')
    const text = await resp.text()
    const wasAtBottom = (
      preEl.scrollHeight - preEl.scrollTop - preEl.clientHeight
    ) < 50

    logs.value = text

    // keep scrolled to bottom if we were already there
    if (wasAtBottom) {
      preEl.scrollTop = preEl.scrollHeight
    }
  } catch (e) {
    console.error('Error fetching logs:', e)
  }
}

// we need a ref to the <pre> so we can measure/scroll it:
let preEl = null
onMounted(() => {
  updateLogs()
  logTimer = setInterval(updateLogs, 2000)
})
onBeforeUnmount(() => {
  clearInterval(logTimer)
})
</script>

<template>
  <div class="logs-area overflow-auto bg-gray-800 text-green-400 p-4 rounded-lg">
    <pre ref="preEl" class="whitespace-pre-wrap">{{ logs }}</pre>
  </div>
</template>

<style scoped>
.logs-area { height: 700px; }
</style>
