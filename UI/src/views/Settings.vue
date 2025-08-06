<script setup>
import { motion } from "motion-v";
import ImportField from "../components/ImportField.vue";
import ConfirmButton from "../components/ConfirmButton.vue";
import { ref, watch, onMounted, onBeforeUnmount } from "vue";
import { Linkedin } from "lucide-vue-next";
import { Github } from "lucide-vue-next";
const tabs = [
  { id: "gtfs", label: "GTFS" },
  { id: "update", label: "Mise à jour" },
  { id: "about", label: "À propos" },
];
const active = ref("gtfs");

const stmLastUpdate = ref("N/A");
const exoLastUpdate = ref("N/A");

const updateState = ref("idle"); // "idle" | "checking" | "up_to_date" | "available" | "updating" | "error"
const lastChecked = ref("N/A");
const updateMessage = ref("");
const localHash = ref("");
const remoteHash = ref("");

const icons = {
  idle: new URL("../assets/icons/status_good.png", import.meta.url).href,
  checking: new URL("../assets/icons/status_updating.png", import.meta.url)
    .href,
  up_to_date: new URL("../assets/icons/status_good.png", import.meta.url).href,
  available: new URL("../assets/icons/status_important.png", import.meta.url)
    .href,
  updating: new URL("../assets/icons/status_updating.png", import.meta.url)
    .href,
  error: new URL("../assets/icons/status_warning.png", import.meta.url).href,
};

// --- Settings + scheduler state ---
const settings = ref({
  autoUpdateTime: "02:00",
});
let updateTimeout = null;

function scheduleNextUpdate() {
  if (updateTimeout !== null) {
    console.log("[Scheduler] Clearing previous timeout:", updateTimeout);
    clearTimeout(updateTimeout);
    updateTimeout = null;
  }

  const time = settings.value.autoUpdateTime;
  console.log("[Scheduler] User-selected time is:", time);
  if (!time) {
    console.warn("[Scheduler] No time chosen, skipping scheduling");
    return;
  }

  const [hour, minute] = time.split(":").map((s) => parseInt(s, 10));
  const now = new Date();
  let next = new Date(
    now.getFullYear(),
    now.getMonth(),
    now.getDate(),
    hour,
    minute,
    0,
    0
  );

  if (next.getTime() <= now.getTime()) {
    next.setDate(next.getDate() + 1);
  }

  const msUntilNext = next.getTime() - now.getTime();
  console.log(
    `[Scheduler] Scheduling next update at ${next.toLocaleString()} ` +
      `(in ${Math.round(msUntilNext / 1000)}s)`
  );
  updateTimeout = setTimeout(async () => {
    console.log("[Scheduler] ⏰ Timeout fired! Running update check now.");
    await checkForUpdates();
    await performUpdate();
    scheduleNextUpdate(); // schedule tomorrow
  }, msUntilNext);
}
async function checkForUpdates() {
  updateState.value = "checking";
  try {
    const res = await fetch("/admin/check_update");
    const body = await res.json();
    if (!res.ok) {
      updateState.value = "error";
      updateMessage.value = body.error || "Erreur inconnue";
      return;
    }
    if (body.up_to_date) {
      updateState.value = "up_to_date";
    } else {
      updateState.value = "available";
    }
  } catch (e) {
    updateState.value = "error";
    updateMessage.value = e.message;
  }
}

async function performUpdate() {
  if (updateState.value !== "available") return;
  updateState.value = "updating";
  try {
    const res = await fetch("/admin/app_update", { method: "POST" });
    const body = await res.json();
    if (res.ok && body.status === "success") {
      updateState.value = "up_to_date";
      updateMessage.value = body.message;
      lastChecked.value = new Date().toLocaleString();
    } else {
      updateState.value = "error";
      updateMessage.value = body.message || "Échec de la mise à jour";
    }
  } catch (e) {
    updateState.value = "error";
    updateMessage.value = e.message;
  }
}

async function uploadGTFS(transport, file) {
  const formData = new FormData();
  formData.append("file", file);
  try {
    const res = await fetch("/admin/update_gtfs", {
      method: "POST",
      body: formData,
    });
    const body = await res.json();
    if (!res.ok) {
      console.error("Upload error:", body.error);
      return;
    }
    if (transport === "stm") {
      stmLastUpdate.value = body.updated_at;
    } else {
      exoLastUpdate.value = body.updated_at;
    }
  } catch (e) {
    console.error("Network error uploading GTFS:", e);
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

onMounted(() => {
  checkForUpdates();
  fetchLastUpdates();
  scheduleNextUpdate();
});

watch(
  () => settings.value.autoUpdateTime,
  (newTime, oldTime) => {
    console.log(
      `[Watcher] autoUpdateTime changed from ${oldTime} to ${newTime}`
    );
    scheduleNextUpdate();
  }
);

onBeforeUnmount(() => {
  if (updateTimeout !== null) {
    clearTimeout(updateTimeout);
  }
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
                    ? 'text-blue-400 border-blue-400'
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
                  class="text-white underline hover:text-blue-400"
                >
                  STM : Développeurs | Société de transport de Montréal
                </a>
              </li>
              <li>
                <a
                  href="https://exo.quebec/fr/a-propos/donnees-ouvertes"
                  target="_blank"
                  class="text-white underline hover:text-blue-400"
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
                :src="icons[updateState] ?? icons.idle"
                alt="status"
                class="h-18 self-start"
              />

              <div class="flex flex-col">
                <h3 class="text-2xl font-bold">
                  <template v-if="updateState === 'available'"
                    >Mise à jour disponible</template
                  >
                  <template v-else-if="updateState === 'up_to_date'"
                    >Tout est à jour !</template
                  >
                  <template v-else-if="updateState === 'checking'"
                    >Vérification en cours...</template
                  >
                  <template v-else-if="updateState === 'updating'"
                    >Mise à jour en cours...</template
                  >
                  <template v-else-if="updateState === 'error'"
                    >Erreur</template
                  >
                  <template v-else>Statut inconnu</template>
                </h3>
                <p class="text-xl text-white">
                  Dernière vérification : {{ lastChecked }}
                  <span v-if="updateState === 'available'"
                    >(nouvelle version disponible)</span
                  >
                  <span v-if="updateState === 'error'"
                    >- {{ updateMessage }}</span
                  >
                </p>
              </div>
            </div>
            <div>
              <button
                v-if="updateState === 'idle' || updateState === 'up_to_date'"
                @click="checkForUpdates"
                class="inline-flex items-center px-4 py-2 bg-blue-400 text-black rounded-lg hover:bg-blue-500 font-bold"
              >
                Rechercher des mises à jour
              </button>
              <button
                v-else-if="updateState === 'available'"
                @click="performUpdate"
                class="inline-flex items-center px-4 py-2 bg-blue-400 text-black rounded-lg hover:bg-blue-500 font-bold"
              >
                Mettre à jour
              </button>
              <button
                v-else-if="
                  updateState === 'checking' || updateState === 'updating'
                "
                disabled
                class="inline-flex items-center px-4 py-2 bg-blue-400 text-black rounded-lg hover:bg-blue-500 font-bold opacity-50"
              >
                <span v-if="updateState === 'checking'">Vérification…</span>
                <span v-else>Mise à jour…</span>
              </button>
              <button
                v-else-if="updateState === 'error'"
                @click="checkForUpdates"
                class="inline-flex items-center px-4 py-2 bg-blue-400 text-black rounded-lg hover:bg-blue-500 font-bold"
              >
                Réessayer
              </button>
            </div>
          </div>
          <div class="flex flex-row items-center gap-2 mb-0 justify-between">
            <div class="flex flex-col">
              <h3 class="text-2xl font-bold text-white">
                Mise à jour automatique
              </h3>
              <p class="text-xl text-white">
                Heure durant laquelle l'application sera mise à jour
                automatiquement tout les jours.
              </p>
            </div>
            <input
              type="time"
              v-model="settings.autoUpdateTime"
              class="h-10 w-1/10 rounded border-gray-300 text-white font-bold focus:ring-2 focus:ring-offset-2 focus:ring-amber-500 bg-gray-600 px-5"
            />
          </div>
        </div>
        <div v-else-if="active === 'about'">
          
<div class="bg-gray-900 rounded-2xl p-10 flex flex-row items-center justify-between space-x-8">
    <!-- left column: text info -->
    <div class="space-y-2">
      <h2 class="text-2xl font-bold text-white">Higher Pierre</h2>
      <p class="text-xl text-white">Designer graphique UX/UI</p>
      <p class="text-xl text-white">Créateur de contenu multimédia</p>
      <p class="text-xl text-white flex items-center">
        Fait avec
        <span class="ml-2 text-red-500">❤️</span>
      </p>
    </div>

    <!-- right column: avatar + buttons -->
    <div class="flex flex-col items-center space-y-4">
      <!-- circular profile picture -->
      <img
        src="../assets/images/hp.jpg"
        alt="Mon profil"
        class="w-32 h-32 rounded-full object-cover shadow-lg"
      />

      <!-- social buttons -->
      <div class="flex space-x-2">
        <a
          href="https://www.linkedin.com/in/higherpierre/"
          target="_blank"
          rel="noopener"
          class="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition"
        >
          <Linkedin class="w-5 h-5" />
          <span class="ml-2 font-medium">LinkedIn</span>
        </a>

        <a
          href="https://github.com/Retexc"
          target="_blank"
          rel="noopener"
          class="flex items-center px-4 py-2 bg-gray-800 hover:bg-gray-900 text-white rounded-lg transition"
        >
          <Github class="w-5 h-5" />
          <span class="ml-2 font-medium">GitHub</span>
        </a>
      </div>
    </div>
  </div>
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
