<template>
  <!-- Fixed viewport window -->
  <div class="preview-viewport">
    <div class="preview-content">
      <!-- Exact copy of your Loading.vue template but with static values -->
      <div class="fixed inset-0 z-40 min-h-screen flex flex-row justify-center items-center pl-16 overflow-hidden gap-8"
           :style="{ fontFamily: 'AtlasGrotesk, sans-serif' }">
        
        <!-- 100% pill -->
        <div class=" flex justify-center bg-white px-14 py-6 rounded-2xl relative overflow-hidden">
          <h1 class="text-6xl md:text-8xl" :style="{ fontWeight: 900, color: pillTextColor }">
            {{ progressText }}
          </h1>

        </div>

        <!-- Animated Words Container -->
        <div class="relative h-screen overflow-hidden w-full flex items-center">
          <div 
            class="space-y-6"
            :style="{ transform: `translateY(0px)` }"
          >
            <h1 class="text-6xl md:text-9xl leading-tight opacity-60"
                :style="{ fontWeight: 900, color: secondaryTextColor }">
              Motivé.
            </h1>
            <h1 class="text-6xl md:text-9xl leading-tight opacity-60"
                :style="{ fontWeight: 900, color: secondaryTextColor }">
              Cavalier.
            </h1>
            <h1 class="text-6xl md:text-9xl leading-tight opacity-60"
                :style="{ fontWeight: 900, color: secondaryTextColor }">
              Fier.
            </h1>
            <h1 class="text-6xl md:text-9xl leading-tight opacity-100"
                :style="{ fontWeight: 900, color: primaryTextColor }">
              Ponctuel.
            </h1>
            <h1 class="text-6xl md:text-9xl leading-tight opacity-60"
                :style="{ fontWeight: 900, color: secondaryTextColor }">
              Ensemble.
            </h1>
                        <h1 class="text-6xl md:text-9xl leading-tight opacity-60"
                :style="{ fontWeight: 900, color: secondaryTextColor }">
              Heureux.
            </h1>
                        <h1 class="text-6xl md:text-9xl leading-tight opacity-60"
                :style="{ fontWeight: 900, color: secondaryTextColor }">
              BdeB.
            </h1>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  progressText: { type: String, default: '100%' },
  primaryTextColor: { type: String, default: '#ffffff' },
  secondaryTextColor: { type: String, default: '#9ca3af' },
  pillTextColor: { type: String, default: '#000000' },
  pillMaskColor: { type: String, default: '#000000' },
  backgroundColor: { type: String, default: '#000000' }
})
</script>

<style scoped>
.preview-viewport {
  width: 100%;
  height: 100%;
  overflow: hidden;
  position: relative;
  background: v-bind(backgroundColor);
}

.preview-content {
  width: 1920px; /* Fixed "screen" width */
  height: 1080px; /* Fixed "screen" height */
  transform: scale(0.3); /* Scale to fit container */
  transform-origin: top left;
  position: absolute;
  top: 0;
  left: 0;
}
</style>