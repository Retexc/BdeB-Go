<script setup>
import ActionButtons from "../components/ActionButtons.vue";
import ConsoleLog from "../components/ConsoleLog.vue";
import SideBar from "../components/SideBar.vue";
import ImagePicker from "../components/ImagePicker.vue";
import ImageSelectorField from "../components/ImageSelectorField.vue";
import DateSelectorField from "../components/DateSelectorField.vue";
import ConfirmButton from "../components/ConfirmButton.vue";
import { ref } from "vue";
const tabs = [
  { id: "gtfs", label: "GTFS" },
  { id: "update", label: "Mise à jour" },
  { id: "about", label: "À propos" },
];

// track which one is active
const active = ref("update");

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
      <div class="space-y-1 w-full">
        <h2 class="text-4xl font-bold text-white">Paramètres</h2>
        <p class="text-xl text-white">
          Modifier les paramètres de l'application
        </p>

        <!-- ───────── Tabs ───────── -->
        <div
          class="mt-2 text-sm font-medium text-center text-gray-500 border-b border-gray-200"
        >
          <ul class="flex flex-wrap -mb-px">
            <li v-for="tab in tabs" :key="tab.id" class="mr-2">
              <a
                href="#"
                @click.prevent="active = tab.id"
                :class="[
                  'inline-block p-4 border-b-2 rounded-t-lg',
                  active === tab.id
                    ? 'text-yellow-300 border-yellow-300'
                    : 'border-transparent hover:text-gray-600 hover:border-gray-300',
                ]"
              >
                {{ tab.label }}
              </a>
            </li>
          </ul>
        </div>
      </div>

      <!-- ───────── Tab Panels ───────── -->
      <div class="mt-4">
        <div v-if="active === 'gtfs'">
          <!-- your GTFS form -->
          <div class="bg-gray-900 rounded-lg p-6 mb-6 text-white space-y-4">
            <h3 class="text-xl font-semibold">
              Les fichiers GTFS contiennent les horaires et les informations des
              autobus et des trains Exo. Il est nécessaire de les mettre à jour
              régulièrement.
            </h3>
            <p>
              Vous pouvez utiliser les dates disponibles sur le site de la STM
              comme référence pour mettre à jour les fichiers.
            </p>
            <p>
              Pour télécharger les dernières versions des données GTFS,
              consultez :
            </p>
            <ul class="list-disc list-inside space-y-1">
              <li>
                <a
                  href="https://www.stm.info/fr/a-propos/developpeurs"
                  target="_blank"
                  class="text-white underline hover:text-yellow-300"
                >
                  STM : Développeurs | Société de transport de Montréal
                </a>
              </li>
              <li>
                <a
                  href="https://exo.quebec/fr/a-propos/donnees-ouvertes"
                  target="_blank"
                  class="text-white underline hover:text-yellow-300"
                >
                  Exo : Autobus, trains et transport adapté dans la région de
                  Montréal
                </a>
              </li>
            </ul>
          </div>
                <div class="flex">
        <img src="../assets/images/stm_logo.svg" alt="STM logo" class="gtfs-logo mb-3 h-10">
                  <hr class="border-t border-[#404040] mt-3" />
      </div>
        </div>
        <div v-else-if="active === 'update'">
          <!-- your Mise à jour form -->
          <p class="text-gray-300">🔄 Ici le contenu de mise à jour…</p>
        </div>
        <div v-else-if="active === 'about'">
          <!-- your À propos info -->
          <p class="text-gray-300">ℹ️ Ici la section À propos…</p>
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
