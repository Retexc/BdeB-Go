<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import Loading from './Loading.vue'
import Display from './Display.vue'
import EndDisplay from './EndDisplay.vue'

const showLoading = ref(true)
const showEndDisplay = ref(false)
const isTransitioning = ref(false)

// Slide animation states
const yellowSlide = ref(-100)
const whiteSlide = ref(-120)
const overlayComplete = ref(false)

let displayTimer = null

// Default fallback colors
const defaultColors = {
  principalTextColor: "#FFFFFF",
  secondaryTextColor: "#6B7280",
  backgroundColor: "#000000",
  pillColor: "#FFFFFF",
  pillTextColor: "#000000",
}

// Load colors from localStorage
const colorsFromStorage = computed(() => {
  try {
    const savedColors = localStorage.getItem("titleCard-colors")
    return savedColors ? JSON.parse(savedColors) : defaultColors
  } catch (error) {
    console.error("Error loading colors from localStorage:", error)
    return defaultColors
  }
})

// Background color only
const backgroundColor = computed(() => colorsFromStorage.value.backgroundColor)

const handleLoadingComplete = () => {
  console.log('Loading complete event received!')
  showLoading.value = false
  
  // Start timer for transition to EndDisplay after 60 seconds
  displayTimer = setTimeout(() => {
    startTransitionToEnd()
  }, 60000)
}

const startTransitionToEnd = () => {
  console.log('Starting transition to EndDisplay')
  isTransitioning.value = true
  overlayComplete.value = false // Reset overlay state

  yellowSlide.value = -100
  whiteSlide.value = -120
  
  setTimeout(() => {
    yellowSlide.value = 100
    whiteSlide.value = 0
  }, 50)
  
  // Switch to EndDisplay when slides cover the screen
  setTimeout(() => {
    console.log('Slides covering screen - switching to EndDisplay')
    showEndDisplay.value = true
  }, 650) 
  
  // Fade out overlay
  setTimeout(() => {
    console.log('Starting overlay fade out')
    overlayComplete.value = true
  }, 1250)
  
  // Complete transition
  setTimeout(() => {
    console.log('Transition complete')
    isTransitioning.value = false
    yellowSlide.value = -100
    whiteSlide.value = -120
  }, 2050)
}

onMounted(() => {
  console.log('MainDisplay mounted')
})

onBeforeUnmount(() => {
  if (displayTimer) {
    clearTimeout(displayTimer)
  }
})
</script>


<template>
  <div class="app-container">
    <Display v-if="!showEndDisplay" />
    <EndDisplay v-else />
    <Loading 
      v-if="showLoading" 
      @loading-complete="handleLoadingComplete"
    />
    
    <!-- Transition slides -->
    <div 
      v-if="isTransitioning"
      class="fixed inset-0 z-50 overflow-hidden pointer-events-none transition-overlay"
      :class="{ 'fade-out': overlayComplete }"
    >
      <div 
        class="absolute h-full w-full bg-white transition-transform duration-1200 ease-in-out"
        :style="{ transform: `translateX(${yellowSlide}%)` }"
      ></div>
      <div 
        class="absolute h-full w-full bg-white transition-transform duration-1200 ease-in-out"
        :style="{ transform: `translateX(${whiteSlide}%)`,
          backgroundColor: backgroundColor,
         }"
      ></div>
    </div>
  </div>
</template>

<style scoped>
.app-container {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

.transition-overlay {
  transition: opacity 0.8s ease-in-out;
}

.transition-overlay.fade-out {
  opacity: 0;
  pointer-events: none;
}
</style>