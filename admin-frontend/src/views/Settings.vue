<script setup>
import { motion } from "motion-v";
import ImportField from "../components/ImportField.vue";
import ConfirmButton from "../components/ConfirmButton.vue";
import { ref, onMounted } from "vue";
const tabs = [
  { id: "gtfs", label: "GTFS" },
  { id: "update", label: "Mise à jour" },
  { id: "about", label: "À propos" },
];

const active = ref("gtfs");

const stmLastUpdate = ref("N/A");
const exoLastUpdate = ref("N/A");

async function uploadGTFS(transport, file) {
  if (!file) return;
  const formData = new FormData();
  formData.append("transport", transport);
  formData.append("gtfs_zip", file);

  try {
    const res = await fetch("/admin/update_gtfs", {
      method: "POST",
      body: formData,
    });
    const body = await res.json();
    if (!res.ok) {
      console.error("Upload error:", body.error);
      // show error to user as needed
      return;
    }
    // success: update the displayed last update
    if (transport === "stm") {
      stmLastUpdate.value = body.updated_at;
    } else {
      exoLastUpdate.value = body.updated_at;
    }
  } catch (e) {
    console.error("Network error uploading GTFS:", e);
  }
}

async function fetchLastUpdates() {
  try {
    const res = await fetch("/admin/gtfs_update_info");
    if (res.ok) {
      const data = await res.json();
      stmLastUpdate.value = data.stm || "N/A";
      exoLastUpdate.value = data.exo || "N/A";
    }
  } catch (e) {
    console.warn("Failed to load GTFS info:", e);
  }
}

function onStmFileChange(e) {
  const file = e.target.files[0];
  uploadGTFS("stm", file);
}

function onExoFileChange(e) {
  const file = e.target.files[0];
  uploadGTFS("exo", file);
}

onMounted(() => {
  fetchLastUpdates();
});
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
          <div class="flex flex-col space-y-6">
            <img
              src="../assets/images/stm_logo.svg"
              alt="STM logo"
              class="gtfs-logo mb-3 h-10 self-start"
            />
            <hr class="border-t border-[#404040] mt-3" />
            <div class="flex flex-col space-y-2">
              <ImportField
                transport="stm"
                placeholder="GTFS STM (.zip)"
                @done="(file) => uploadGTFS('stm', file)"
                @error="(err) => console.error('STM import error', err)"
              />
              <p class="text-sm text-white">
                Dernière mise à jour : {{ stmLastUpdate }}
              </p>
            </div>

            <img
              src="../assets/images/exo.svg"
              alt="Exo logo"
              class="gtfs-logo mb-3 h-8 self-start"
            />
            <hr class="border-t border-[#404040] mt-3" />
            <div class="flex flex-col space-y-2">
              <ImportField
                transport="exo"
                placeholder="GTFS EXO (.zip)"
                @done="(file) => uploadGTFS('exo', file)"
                @error="(err) => console.error('EXO import error', err)"
              />
              <p class="text-sm text-white">
                Dernière mise à jour : {{ exoLastUpdate }}
              </p>
            </div>
          </div>
        </div>
        <div v-else-if="active === 'update'">
          <div
            class="bg-gray-900 rounded-lg p-6 mb-6 text-white space-y-4 flex flex-row items-center justify-between"
          >
            <div class="flex flex-row items-center gap-2 mb-0">
              <img
                src="../assets/images/check_circle.svg"
                alt="check"
                class="h-18 self-start"
              />
              <div class="flex flex-col">
                <h3 class="text-2xl font-bold">Tout est à jour !</h3>
                <p class="text-xl text-white">Dernière vérification : N/A</p>
              </div>
            </div>

            <confirm-button> Rechercher des mises à jour </confirm-button>
          </div>
        </div>
        <div v-else-if="active === 'about'">
          <p class="text-gray-300">ℹ️ Ici la section À propos…</p>
        </div>
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
