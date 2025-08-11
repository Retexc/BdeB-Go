<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from "vue";
import { motion } from "motion-v";
import BusRow from "../components/BusRow.vue";
import TrainRow from "../components/TrainRow.vue";
import MetroRow from "../components/MetroRow.vue";
import Header from "../components/Header.vue";
import AlertBanner from "../components/AlertBanner.vue";
import STMLogo from "../assets/icons/STM.png";
import ExoLogo from "../assets/icons/exo_white.png";

const buses = ref([])
const activeBackground = ref('')
const showBuses = ref(true) 
let viewInterval = null

// Configurable view switch timing (in milliseconds)
const VIEW_SWITCH_INTERVAL = 45000 // 45 seconds 

const metroLines = ref([])
const trains = ref([])

// Computed property to sort buses by arrival time (ascending)
const sortedBuses = computed(() => {
  return [...buses.value].sort((a, b) => {
    const timeA = a.arrival_time;
    const timeB = b.arrival_time;
    
    if (typeof timeA === 'number' && typeof timeB === 'number') {
      return timeA - timeB;
    }
    
    if (typeof timeA === 'string' && typeof timeB === 'string') {
      return timeA.localeCompare(timeB);
    }

    if (typeof timeA === 'number' && typeof timeB === 'string') {
      return -1;
    }
    
    if (typeof timeA === 'string' && typeof timeB === 'number') {
      return 1;
    }
    
    return 0;
  });
});

async function fetchData() {
  try {
    const res = await fetch('/api/data')
    const json = await res.json()
    
    // Update buses
    buses.value = json.buses.filter(b =>
      ['171','180','164'].includes(b.route_id)
    )
    
    if (json.next_trains && json.next_trains.length > 0) {
      trains.value = json.next_trains.slice(0, 3); 
    }
    
    if (json.metro_lines) {
      metroLines.value = json.metro_lines;
    }
    
  } catch (err) {
    console.error('Error fetching data:', err)
  }
}

async function applyActiveBackground() {
  try {
    const res = await fetch("http://127.0.0.1:5001/admin/backgrounds");
    if (!res.ok) return;
    const slots = await res.json();

    const now = new Date();
    const active = slots.find((s) => {
      if (!s?.path) return false;
      if (s.end && new Date(s.end) < now) return false;
      return true;
    });

    const bgPath =
      (active && active.path) ||
      "/static/assets/images/Printemps - Banner Big.png";
    
    activeBackground.value = `url(${bgPath})`;
  } catch (err) {
    console.warn("Could not apply active background", err);
    // Fallback to default background
    activeBackground.value = "url(/static/assets/images/Printemps - Banner Big.png)";
  }
}

function toggleView() {
  showBuses.value = !showBuses.value;
}

onMounted(() => {
  fetchData()
  applyActiveBackground()
  setInterval(fetchData, 30_000) 
  setInterval(applyActiveBackground, 15_000) // Update background every 15 seconds
  
  viewInterval = setInterval(toggleView, VIEW_SWITCH_INTERVAL)
})

onBeforeUnmount(() => {
  if (viewInterval) {
    clearInterval(viewInterval);
  }
})
</script>

<template>
<div class="display-container" :style="{ backgroundImage: activeBackground }">
<Header />

  <Transition name="view-fade" mode="out-in">
    <!-- STM Bus View -->
    <div v-if="showBuses" key="buses" class="view-container">
      <img :src="STMLogo" alt="STM logo" class="w-22 h-auto mt-4 ml-6"></img>
      <div class="flex flex-col">
        
        <TransitionGroup 
          name="bus-list" 
          tag="div" 
          class="flex flex-col"
          v-if="sortedBuses.length"
        >
          <BusRow
            v-for="bus in sortedBuses"
            :key="bus.trip_id"
            :bus="bus"
          />
        </TransitionGroup>
        <p v-if="buses.length === 0" class="text-gray-500">
          Aucun autobus à afficher…
        </p>
      </div>
    </div>

    <!-- Metro View -->
    <div v-else key="metro" class="view-container">
      <img :src="STMLogo" alt="STM logo" class="w-22 h-auto mt-4 ml-6"></img>
      <div class="flex flex-col">
        
        <TransitionGroup 
          name="metro-list" 
          tag="div" 
          class="flex flex-col"
        >
          <MetroRow
            v-for="line in metroLines"
            :key="line.id"
            :line="line"
          />
        </TransitionGroup>
      </div>

      <div class="mt-8"></div>
      <!-- Exo Logo and Train Rows -->
      <img :src="ExoLogo" alt="Exo logo" class="w-22 h-auto mt-4 ml-6"></img>
      <div class="flex flex-col">
        
        <TransitionGroup 
          name="train-list" 
          tag="div" 
          class="flex flex-col"
        >
          <TrainRow
            v-for="train in trains"
            :key="train.id"
            :train="train"
          />
        </TransitionGroup>
      </div>
    </div>
  </Transition>

  <!-- Alert Banner at bottom -->
  <AlertBanner />
</div>

</template>

<style scoped>
:host {
  display: block;
  height: 100%;
}

.display-container {
  min-height: 100vh;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  transition: background-image 0.5s ease-in-out;
  position: relative;
  overflow: hidden;
}


.display-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.65); /* 65% dark overlay */
  pointer-events: none; 
  z-index: 1;
}

.display-container > * {
  position: relative;
  z-index: 2;
}

.view-container {
  opacity: 1;
  width: 100%;
  overflow: hidden; 
}

.view-fade-enter-active,
.view-fade-leave-active {
  transition: all 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

.view-fade-enter-from {
  opacity: 0;
  transform: translateY(50px);
}

.view-fade-leave-to {
  opacity: 0;
}

.view-fade-leave-active {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  width: 100%;
}

.view-fade-enter-active {
  transition-delay: 0.1s;
  position: relative;
  z-index: 3;
}

.bus-list-move,
.bus-list-enter-active,
.bus-list-leave-active {
  transition: all 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.bus-list-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.bus-list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

.bus-list-leave-active {
  position: absolute;
  width: calc(100% - 4rem);
  left: 2rem;
}

/* Metro list animations */
.metro-list-move,
.metro-list-enter-active,
.metro-list-leave-active {
  transition: all 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.metro-list-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.metro-list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

.metro-list-leave-active {
  position: absolute;
  width: calc(100% - 4rem);
  left: 2rem;
}

/* Train list animations */
.train-list-move,
.train-list-enter-active,
.train-list-leave-active {
  transition: all 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.train-list-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.train-list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

.train-list-leave-active {
  position: absolute;
  width: calc(100% - 4rem);
  left: 2rem;
}

.bus-list-move,
.metro-list-move,
.train-list-move {
  transform-origin: center;
}

.bus-list-enter-active,
.metro-list-enter-active,
.train-list-enter-active {
  transition-delay: 0.1s;
}

body {
  overflow: hidden;
}

.display-container:not(.transitioning) {
  overflow: auto;
}
</style>