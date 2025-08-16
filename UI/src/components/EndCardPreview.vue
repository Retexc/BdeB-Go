<template>
  <div class="preview-viewport">
    <div class="preview-content">
      <!-- Exact copy of your EndDisplay.vue template -->
      <div
        class="fixed inset-0 z-40 min-h-screen flex flex-row justify-center items-center pl-16 overflow-hidden gap-8"
        :style="{
          fontFamily: 'AtlasGrotesk, sans-serif',
          backgroundColor: backgroundColor,
        }"
      >
        <div class="relative h-screen overflow-hidden w-full flex items-center">
          <div class="space-y-6 transition-transform duration-2000 ease-in-out">
            <h1
              class="text-6xl md:text-9xl leading-tight transition-all duration-700 ease-in-out opacity-100 translate-y-0"
              :style="{ fontWeight: 900, color: textColor }"
              v-html="mainText"
            ></h1>
          </div>

          <!-- Logo -->
          <img
            :src="logoSrc"
            alt=""
            class="fixed bottom-0 right-0 my-18 mr-18 w-116 h-auto opacity-100"
          />

          <img
            src="../assets/images/pink_b.svg"
            alt=""
            class="fixed -bottom-6 left-0 w-76 h-auto"
          />

          <img
            src="../assets/images/purple_b.svg"
            alt=""
            class="fixed -bottom-6 left-20 w-52 h-auto"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  mainText: { type: String, default: "Passez une bonne<br />rentrée !" },
  textColor: { type: String, default: "#ffffff" },
  backgroundColor: { type: String, default: "#000000" },
  logoSrc: { type: String, default: "../assets/icons/bdeb.svg" },
  pinkImageSrc: { type: String, default: "../assets/images/pink_b.svg" },
  purpleImageSrc: { type: String, default: "../assets/images/purple_b.svg" },
});
</script>

<style scoped>
.preview-viewport {
  width: 100%;
  height: 100%;
  overflow: hidden;
  position: relative;
}

.preview-content {
  width: 1920px;
  height: 1080px;
  transform: scale(0.31);
  transform-origin: top left;
  position: absolute;
  top: 0;
  left: 0;
}
</style>
