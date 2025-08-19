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
const overlayOpacity = ref(0.65) 
const showBuses = ref(true) 
let viewInterval = null

// Configurable view switch timing
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

const overlayStyle = computed(() => ({
  background: `rgba(0, 0, 0, ${overlayOpacity.value})`
}));

const backgroundStyle = computed(() => ({
  backgroundImage: activeBackground.value
}));

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
    const data = await res.json();

    let slots;
    if (Array.isArray(data)) {
      slots = data;
    } else {
      slots = data.slots || [];
      if (data.overlay !== undefined) {
        overlayOpacity.value = data.overlay;
      }
    }

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

async function fetchOverlayOpacity() {
  try {
    const storedOpacity = localStorage.getItem('backgroundOverlayOpacity');
    if (storedOpacity) {
      overlayOpacity.value = JSON.parse(storedOpacity);
      return;
    }
    
    const res = await fetch("http://127.0.0.1:5001/admin/backgrounds/overlay");
    if (res.ok) {
      const data = await res.json();
      if (data.opacity !== undefined) {
        overlayOpacity.value = data.opacity;
      }
    }
  } catch (err) {
    console.warn("Could not fetch overlay opacity", err);
    // Keep default value
  }
}

function toggleView() {
  showBuses.value = !showBuses.value;
}

onMounted(() => {
  fetchData()
  applyActiveBackground()
  fetchOverlayOpacity()
  setInterval(fetchData, 30_000) 
  setInterval(applyActiveBackground, 15_000) // Update background every 15 seconds
  setInterval(fetchOverlayOpacity, 15_000) // Update overlay every 15 seconds
  
  viewInterval = setInterval(toggleView, VIEW_SWITCH_INTERVAL)
})

onBeforeUnmount(() => {
  if (viewInterval) {
    clearInterval(viewInterval);
  }
})
</script>

<template>
<div 
  class="min-h-screen bg-cover bg-center bg-no-repeat relative overflow-hidden transition-all duration-500 ease-in-out"
  :style="backgroundStyle"
>
  <!-- Overlay -->
  <div 
    class="absolute inset-0 pointer-events-none z-10 transition-all duration-300 ease-in-out"
    :style="overlayStyle"
  ></div>

  <!-- Content -->
  <div class="relative z-20">
    <Header />

    <!-- Main content area with fixed positioning for transitions -->
    <div class="relative min-h-[calc(100vh-120px)] overflow-hidden">
      <Transition 
        name="view-transition" 
        mode="out-in"
        enter-active-class="transition-all duration-700 ease-out"
        leave-active-class="transition-all duration-700 ease-out absolute top-0 left-0 right-0 w-full"
        enter-from-class="opacity-0 translate-y-8"
        leave-to-class="opacity-0 -translate-y-8"
      >
        <!-- STM Bus View -->
        <div v-if="showBuses" key="buses" class="w-full">
          <img :src="STMLogo" alt="STM logo" class="w-22 h-auto mt-4 ml-6"></img>
          <div class="flex flex-col">
            
            <TransitionGroup 
              name="bus-list" 
              tag="div" 
              class="flex flex-col"
              v-if="sortedBuses.length"
              move-class="transition-all duration-600 ease-out origin-center"
              enter-active-class="transition-all duration-600 ease-out delay-100"
              leave-active-class="transition-all duration-600 ease-out absolute left-8 w-[calc(100%-4rem)]"
              enter-from-class="opacity-0 -translate-x-8"
              leave-to-class="opacity-0 translate-x-8"
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
        <div v-else key="metro" class="w-full">
          <img :src="STMLogo" alt="STM logo" class="w-22 h-auto mt-4 ml-6"></img>
          <div class="flex flex-col">
            
            <TransitionGroup 
              name="metro-list" 
              tag="div" 
              class="flex flex-col"
              move-class="transition-all duration-600 ease-out origin-center"
              enter-active-class="transition-all duration-600 ease-out delay-100"
              leave-active-class="transition-all duration-600 ease-out absolute left-8 w-[calc(100%-4rem)]"
              enter-from-class="opacity-0 -translate-x-8"
              leave-to-class="opacity-0 translate-x-8"
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
              move-class="transition-all duration-600 ease-out origin-center"
              enter-active-class="transition-all duration-600 ease-out delay-100"
              leave-active-class="transition-all duration-600 ease-out absolute left-8 w-[calc(100%-4rem)]"
              enter-from-class="opacity-0 -translate-x-8"
              leave-to-class="opacity-0 translate-x-8"
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
    </div>
  </div>

  <!-- Alert Banner at bottom -->
  <AlertBanner />
</div>
</template>