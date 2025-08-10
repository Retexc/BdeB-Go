<template>
  <div class="min-h-screen bg-black flex flex-row justify-center items-center pl-16 overflow-hidden" :style="{ fontFamily: 'AtlasGrotesk, sans-serif' }">
    
    <!-- 100% Badge -->
    <div class="bg-white px-8 py-4 rounded-2xl mb-12">
      <h1 class="text-black text-6xl md:text-7xl" :style="{ fontWeight: 900 }">100%</h1>
    </div>
    
    <!-- Animated Words Container -->
    <div class="relative h-full overflow-hidden w-full">
      <!-- Word Stack - animates upward -->
      <div 
        class="transition-transform duration-1000 ease-in-out space-y-6"
        :style="{ 
          transform: `translateY(${-currentIndex * 140}px)`,
        }"
      >
        <!-- Add extra words at the beginning for smooth entry -->
        <h1 class="text-6xl md:text-7xl leading-tight opacity-0" :style="{ fontWeight: 900 }">.</h1>
        <h1 class="text-6xl md:text-7xl leading-tight opacity-0" :style="{ fontWeight: 900 }">.</h1>
        <h1 class="text-6xl md:text-7xl leading-tight opacity-0" :style="{ fontWeight: 900 }">.</h1>
        
        <h1 
          v-for="(word, index) in words" 
          :key="index"
          class="text-6xl md:text-7xl leading-tight transition-opacity duration-500"
          :class="getWordClass(index)"
          :style="{ fontWeight: 900 }"
        >
          {{ word }}
        </h1>
        
        <!-- Add extra words at the end for smooth exit -->
        <h1 class="text-6xl md:text-7xl leading-tight opacity-0" :style="{ fontWeight: 900 }">.</h1>
        <h1 class="text-6xl md:text-7xl leading-tight opacity-0" :style="{ fontWeight: 900 }">.</h1>
        <h1 class="text-6xl md:text-7xl leading-tight opacity-0" :style="{ fontWeight: 900 }">.</h1>
      </div>
    </div>

  </div>
</template>

<script>
export default {
  data() {
    return {
      words: ['Réussite.', 'Fier.', 'Cavalier.', 'Motivé.', 'Transport.', 'Ensemble.', 'Heureux.', 'BdeB.', 'Vous.'],
      currentIndex: 0,
      timeoutId: null,
      targetWordIndex: 4 // Index of "Transport." in the array
    }
  },
  mounted() {
    this.startSmoothAnimation()
  },
  beforeUnmount() {
    if (this.timeoutId) {
      clearTimeout(this.timeoutId)
    }
  },
  methods: {
    startSmoothAnimation() {
      // Wait 1 second, then smoothly animate to Transport
      this.timeoutId = setTimeout(() => {
        this.currentIndex = this.targetWordIndex // This will trigger the CSS transition
      }, 1000)
    },
    getWordClass(index) {
      const position = index - this.currentIndex
      
      if (position === 0) {
        return 'text-white opacity-100' // Current word - fully visible
      } else if (position === 1) {
        return 'text-gray-400 opacity-60' // Next word - medium opacity
      } else if (position === 2) {
        return 'text-gray-500 opacity-30' // Word after - low opacity
      } else {
        return 'text-gray-600 opacity-10' // Other words - barely visible
      }
    }
  }
}
</script>