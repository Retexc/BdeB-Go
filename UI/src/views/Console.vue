<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from "vue";
import { motion } from "motion-v";
import ConsoleLog from "../components/ConsoleLog.vue";
import playIcon from "../assets/icons/play.svg";
import stopIcon from "../assets/icons/stop-circle.svg";

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

function goToExternal() {
   window.open('http://localhost:5174/display', '_blank', 'noopener')
}
// **Mark async** so we can `await` the fetch
async function toggleApp() {
    console.log('🔘 button clicked, running =', running.value)
  const url = running.value ? '/admin/stop' : '/admin/start'
  try {
    const resp = await fetch(url, { method: 'POST' })
    console.log(await resp.json())
  } catch (e) {
    console.error('Error toggling app:', e)
  }
  updateStatus()
}

// now only **one** of each computed
const btnLabel       = computed(() => running.value ? 'Arrêter'   : 'Démarrer')
const btnIcon        = computed(() => running.value ? stopIcon    : playIcon)
const btnClass       = computed(() =>
  running.value
    ? 'bg-red-400 hover:bg-red-500 rounded-lg'
    : 'bg-blue-400 hover:bg-blue-500 rounded-lg'
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
        <span class="text-white font-bold">État :</span>
        <span :class="running ? 'text-green-400' : 'text-red-400'">
          {{ running ? " En cours" : " Arrêté" }}
        </span>
      </div>
      <div class="flex space-x-2">
        <button
          v-if="running"
          @click="goToExternal"
          class="btn btn-link bg-blue-400 font-black rounded-lg p-2"
        >
          Accéder au tableau
        </button>

        <button
          @click="toggleApp"
          :disabled="loading"
          :class="['px-4 py-2 text-black rounded font-bold', btnClass]"
        >
          <img
            :src="btnIcon"
            class="inline w-4 h-4.5 mr-1 align-text-bottom"
            alt=""
          />
          {{ running ? "Arrêter" : "Démarrer" }}
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
        transition: { duration: 0.6 },
      }"
      class="flex-1"
    >
      <ConsoleLog />
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
