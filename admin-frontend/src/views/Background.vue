<script setup>
import ActionButtons from "../components/ActionButtons.vue";
import ConsoleLog from "../components/ConsoleLog.vue";
import SideBar from "../components/SideBar.vue";
import ImagePicker from "../components/ImagePicker.vue";
import ImageSelectorField from "../components/ImageSelectorField.vue";
import DateSelectorField from "../components/DateSelectorField.vue";
import ConfirmButton from "../components/ConfirmButton.vue";
function goToTableau() {
  // e.g. this.$router.push('/tableau')
}

function startProcess() {
  // your start logic...
}
</script>

<template>
  <div class="flex max-h-screen bg-[#0f0f0f]">
    <side-bar />

    <div class="flex-1 flex flex-col p-6 space-y-6 mt-18 ml-5 mr-5">
      <div class="flex items-center justify-between w-full">
        <div class="space-y-1 w-full">
          <h2 class="text-4xl font-bold text-white">Fond d'écran</h2>
          <p class="text-xl text-white">
            Modifier l’arrière-plan du tableau d’affichage
          </p>
          <hr class="border-t border-[#404040] mt-3" />
        </div>
      </div>

      <div class="flex items-end space-x-6 justify-between">
        <!-- big preview fixed at 16rem high -->
        <img
          src="../assets/images/background.png"
          alt="background"
          class="h-74 object-cover rounded-lg"
        />

        <!-- auto‑height column, bottom‑aligned by the parent -->
        <div class="flex flex-col space-y-2 gap-4">
          <h2 class="text-2xl font-bold text-white">Images récentes</h2>
          <ImagePicker />
        </div>
      </div>
      <div class="flex flex-col gap-4">
        <h2 class="text-2xl font-bold text-white">Paramètres</h2>
        <hr class="border-t border-[#404040] mt-3" />
        <image-selector-field />
        <label class="inline-flex items-center space-x-2">
          <span class="text-white font-bold">
            Définir cette image comme image par défaut ?</span
          >
          <input
            type="checkbox"
            v-model="remember"
            class="h-5 w-5 border-gray-600 rounded bg-gray-800 checked:bg-yellow-400 checked:border-yellow-400 focus:ring-2 focus:ring-yellow-500"
          />
        </label>
        <div class="flex items-end space-x-2 justify-between">
          <date-selector-field />
          <confirm-button>
            <template #icon>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke-width="1.5"
                stroke="currentColor"
                class="size-6 mr-1"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"
                />
              </svg>
            </template>
          </confirm-button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-page {
  padding: 2rem;
  text-align: center;
}
</style>
