<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { motion } from 'motion-v'
import ConsoleLog from '../components/ConsoleLog.vue'
import playIcon  from '../assets/images/play_arrow.svg'
import stopIcon  from '../assets/images/stop.svg'

const running     = ref(false)
let   statusTimer = null

async function updateStatus() {
  try {
    const resp = await fetch('/admin/status')
    const { running: isUp } = await resp.json()
    running.value = isUp
  } catch (e) {
    console.error('Error fetching status:', e)
  }
}

async function toggleApp() {
  const url = running.value ? '/admin/stop' : '/admin/start'
  try {
    const resp = await fetch(url, { method: 'POST' })
    console.log(await resp.json())
  } catch (e) {
    console.error('Error toggling app:', e)
  }
  updateStatus()
}

const btnLabel       = computed(() => running.value ? 'Arrêter' : 'Démarrer')
const btnIcon        = computed(() => running.value ? stopIcon  : playIcon)
const btnClass       = computed(() =>
  running.value
    ? 'bg-red-600 hover:bg-red-700'
    : 'bg-blue-600 hover:bg-blue-700'
)
const statusText     = computed(() =>
  running.value ? 'État : Actif' : 'État : Arrêté'
)
const statusTextColor= computed(() =>
  running.value ? 'text-green-400' : 'text-red-500'
)

onMounted(() => {
  updateStatus()
  statusTimer = setInterval(updateStatus, 2000)
})
onBeforeUnmount(() => {
  clearInterval(statusTimer)
})
</script>

<template>
  <div class="p-6 flex flex-col h-full">
    <!-- ─── Header + Buttons ─── -->
    <div class="flex items-center justify-between mb-4 mt-20">
      <div>
        <h1 class="text-2xl font-bold text-white">
          Tableau d’affichage en temps réel
        </h1>
        <h3 :class="['mt-1', statusTextColor]">
          {{ statusText }}
        </h3>
      </div>
      <div class="flex space-x-2">
        <a
          href="http://127.0.0.1:5000"
          target="_blank"
          class="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
        >
          Accéder au tableau
        </a>
        <button
          @click="toggleApp"
          :class="['px-4 py-2 text-white rounded', btnClass]"
        >
          <img
            :src="btnIcon"
            class="inline w-4 h-4 mr-1 align-text-bottom"
            alt=""
          />
          {{ btnLabel }}
        </button>
      </div>
      
    </div>

    <!-- ─── Animated Console Section ─── -->
    <motion.div
      :initial="{ opacity: 0, y: 20, filter: 'blur(10px)' }"
      :animate="{
        opacity: 1,
        y: 0,
        filter: 'blur(0px)',
        transition: { duration: 0.6 }
      }"
      class="flex-1 "
    >      <ConsoleLog />
    </motion.div>
  </div>
</template>

<style scoped>
/* ensure full‐height so motion has space */
:host {
  display: block;
  height: 100%;
}
</style>
