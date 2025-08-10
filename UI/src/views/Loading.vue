<template>
  <div
    class="min-h-screen bg-black flex flex-row justify-center items-center pl-16 overflow-hidden gap-8"
    :style="{ fontFamily: 'AtlasGrotesk, sans-serif' }"
  >
    <!-- 100% Badge -->
    <div class="bg-white px-12 py-6 rounded-2xl">
      <h1 class="text-black text-6xl md:text-9xl" :style="{ fontWeight: 900 }">
        100%
      </h1>
    </div>

    <!-- Animated Words Container -->
    <div class="relative h-screen overflow-hidden w-full flex items-center">
      <!-- Word Stack - animates from bottom to center "Ponctuel." -->
      <div 
        class="space-y-6 transition-transform duration-2000 ease-out"
        :style="{ transform: `translateY(${scrollPosition}px)` }"
      >
        <!-- Words above Ponctuel -->
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

        <!-- Ponctuel - Always in the center -->
        <h1
          class="text-6xl md:text-9xl leading-tight text-white opacity-100"
          :style="{ fontWeight: 900 }"
        >
          Ponctuel.
        </h1>

        <!-- Words below Ponctuel -->
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
  data() {
    return {
      scrollPosition: 1300, // Start below the visible area (bottom)
    };
  },
  mounted() {
    // Wait 1 second, then scroll up to center "Ponctuel."
    setTimeout(() => {
      this.scrollPosition = 0; // Move up to center "Ponctuel." (4 words × 140px)
    }, 1000);
    
    console.log('Loading animation ready - Words will scroll from bottom!');
  },
};
</script>