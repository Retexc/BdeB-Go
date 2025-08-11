<template>
  <!-- Double slide transition -->
  <div 
    class="fixed inset-0 z-50 overflow-hidden pointer-events-none loading-overlay"
    :class="{ 'fade-out': overlayComplete }"
  >
    <div 
      class="absolute h-full w-full bg-[#FFCF25] transition-transform duration-1200 ease-in-out"
      :style="{ transform: `translateX(${yellowSlide}%)` }"
    ></div>
    <div 
      class="absolute h-full w-full bg-white transition-transform duration-1200 ease-in-out"
      :style="{ transform: `translateX(${whiteSlide}%)` }"
    ></div>
  </div>

  <div
    class="fixed inset-0 z-40 min-h-screen bg-black flex flex-row justify-center items-center pl-16 overflow-hidden gap-8 loading-content"
    :class="{ 'fade-out': isComplete }"
    :style="{ fontFamily: 'AtlasGrotesk, sans-serif' }"
  >

    <!-- 100% pill -->
    <div class="bg-white px-12 py-6 rounded-2xl ">
      <h1 class="text-black text-6xl md:text-9xl" :style="{ fontWeight: 900 }">
        100%
      </h1>
      <div 
        class="absolute inset-0 bg-black transition-transform duration-1800 ease-in-out"
        :style="{ transform: `translateX(${maskPosition}%)` }"
      ></div>
    </div>

    <!-- Animated Words Container -->
    <div class="relative h-screen overflow-hidden w-full flex items-center">
      <div 
        class="space-y-6 transition-transform duration-2000 ease-in-out"
        :style="{ transform: `translateY(${scrollPosition}px)` }"
      >
        <h1
          class="text-6xl md:text-9xl leading-tight text-gray-400 opacity-60"
          :style="{ fontWeight: 900 }"
        >
          Motivé.
        </h1>
        <h1
          class="text-6xl md:text-9xl leading-tight text-gray-400 opacity-60"
          :style="{ fontWeight: 900 }"
        >
          Cavalier.
        </h1>
        <h1
          class="text-6xl md:text-9xl leading-tight text-gray-400 opacity-60"
          :style="{ fontWeight: 900 }"
        >
          Fier.
        </h1>
        <h1
          class="text-6xl md:text-9xl leading-tight text-gray-400 opacity-60"
          :style="{ fontWeight: 900 }"
        >
          Réussite.
        </h1>

        <h1
          class="text-6xl md:text-9xl leading-tight text-white opacity-100"
          :style="{ fontWeight: 900 }"
        >
          Ponctuel.
        </h1>

        <h1
          class="text-6xl md:text-9xl leading-tight text-gray-400 opacity-60"
          :style="{ fontWeight: 900 }"
        >
          Ensemble.
        </h1>
        <h1
          class="text-6xl md:text-9xl leading-tight text-gray-400 opacity-60"
          :style="{ fontWeight: 900 }"
        >
          Heureux.
        </h1>
        <h1
          class="text-6xl md:text-9xl leading-tight text-gray-400 opacity-60"
          :style="{ fontWeight: 900 }"
        >
          BdeB.
        </h1>
        <h1
          class="text-6xl md:text-9xl leading-tight text-gray-400 opacity-60"
          :style="{ fontWeight: 900 }"
        >
          Vous.
        </h1>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  emits: ['loading-complete'],
  data() {
    return {
      scrollPosition: 1500, 
      maskPosition: 0,   
      yellowSlide: -100, 
      whiteSlide: -120,
      isComplete: false, 
      overlayComplete: false 
    };
  },
  mounted() {
    console.log('Loading component mounted')
    
    setTimeout(() => {
      this.maskPosition = 100; 
      console.log('Mask animation started')
    }, 200);
    
    setTimeout(() => {
      this.scrollPosition = 0;
      console.log('Scroll animation started')
    }, 700);
    
    setTimeout(() => {
      this.startDoubleSlide();
      console.log('Double slide started')
    }, 3000); 
    
    // Hide content when slides have covered the screen (mid-animation)
    setTimeout(() => {
      console.log('Slides covering screen - hiding content')
      this.isComplete = true;
    }, 3600);
    
    setTimeout(() => {
      console.log('Starting overlay fade out')
      this.overlayComplete = true;
    }, 4200);
    
    setTimeout(() => {
      console.log('Emitting loading-complete event')
      this.$emit('loading-complete');
    }, 5000);
  },
  methods: {
    startDoubleSlide() {
      this.yellowSlide = 100;
      this.whiteSlide = 0; 
    }
  }
};
</script>

<style scoped>
.loading-overlay,
.loading-content {
  transition: opacity 0.8s ease-in-out;
}

.loading-overlay.fade-out,
.loading-content.fade-out {
  opacity: 0;
  pointer-events: none;
}
</style>