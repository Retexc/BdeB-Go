<script setup>
import { ref, watch, onMounted } from "vue";
import { motion } from "motion-v";
import ImageSelectorField from "../components/ImageSelectorField.vue";
import placeholderBg from "../assets/images/background.png";
import Loading from "./Loading.vue";
import LoadingPreview from "../components/LoadingPreview.vue";
import EndCardPreview from "../components/EndCardPreview.vue";
onMounted(async () => {});
</script>

<template>
  <motion.div
    class="flex max-h-screen bg-[#0f0f0f]"
    :initial="{ opacity: 0, y: 20, filter: 'blur(10px)' }"
    :animate="{
      opacity: 1,
      y: 0,
      filter: 'blur(0px)',
      transition: { duration: 0.5 },
    }"
  >
    <div class="flex-1 flex flex-col p-6 space-y-6 mt-18 ml-5 mr-5">
      <!-- Header -->
      <div class="flex items-center justify-between w-full">
        <div class="space-y-1 w-full">
          <h2 class="text-4xl font-bold text-white">Écran-titre</h2>
          <p class="text-xl text-white">
            Modifier l'apparence de l'écran-titre
          </p>
          <hr class="border-t border-[#404040] mt-3" />
        </div>
      </div>

      <!-- Preview + Recents -->
      <div class="flex flex-col gap-4">
        <h2 class="text-2xl font-bold text-white">Aperçu</h2>
        <div class="flex flex-row gap-6 justify-between">
          <!-- Loading Preview -->
          <div
            class="w-150 h-86 border-2 border-[#404040] rounded-lg overflow-hidden bg-black"
          >
            <LoadingPreview />
          </div>
          <div
            class="w-150 h-86 border-2 border-[#404040] rounded-lg overflow-hidden bg-black"
          >
            <EndCardPreview />
          </div>
        </div>
      </div>

      <!-- Settings -->
      <div class="flex flex-col gap-4">
        <h2 class="text-2xl font-bold text-white">Paramètres</h2>
        <hr class="border-t border-[#404040] mt-3" />


      </div>
    </div>
  </motion.div>
</template>

<style scoped>
.home-page {
  padding: 2rem;
  text-align: center;
}
</style>
