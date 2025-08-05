<script setup>
import { ref, watch, onMounted } from "vue";
import { motion } from "motion-v";
import ImageSelectorField from "../components/ImageSelectorField.vue";
import placeholderBg from '../assets/images/background.png';

const previewImage = ref('');
const recentImages = ref([]);
const slots = ref([]);
const MAX_RECENTS = 4;
const defaultBackground = '../assets/images/background.png';

function onPreviewError(e) {
  e.target.src = defaultBackground;
}

function addToRecent(url) {
  if (!url) return;
  if (url.startsWith('blob:')) return;

  recentImages.value = recentImages.value.filter(i => i !== url);
  recentImages.value.unshift(url);
  if (recentImages.value.length > MAX_RECENTS) {
    recentImages.value.length = MAX_RECENTS;
  }
}


watch(
  recentImages,
  v => {
    try {
      localStorage.setItem('recentBgImages', JSON.stringify(v.slice(0, MAX_RECENTS)));
    } catch {}
  },
  { deep: true }
);

onMounted(async () => {
  try {
    const stored = localStorage.getItem('recentBgImages');
    if (stored) {
      recentImages.value = JSON.parse(stored).slice(0, MAX_RECENTS);
    }
  } catch (e) {
    console.warn('failed to load recentImages', e);
  }

  try {
    const r = await fetch('/admin/backgrounds');
    if (r.ok) {
      const data = await r.json();
      slots.value = Array.isArray(data) ? data : [];
      if (slots.value[0] && slots.value[0].path) {
        previewImage.value = slots.value[0].path;
      }
    }
  } catch (e) {
    console.warn('failed to load slots', e);
  }
});

async function handleFileUpload(e) {
  const file = e.target.files[0];
  if (!file) return;

  const blobUrl = URL.createObjectURL(file);
  previewImage.value = blobUrl;

  // send to server
  const form = new FormData();
  form.append("image", file);

  try {
    const res = await fetch("/admin/backgrounds/import", {
      method: "POST",
      body: form
    });
    const data = await res.json();

    if (data.status === "success") {
      // now switch preview to the permanent URL
      previewImage.value = data.url;
      // update slots
      slots.value = data.slots;
      // store only the real URL in recents
      addToRecent(data.url);
    } else {
      console.error("upload failed", data);
    }
  } catch (err) {
    console.error("background import error", err);
  }
}


async function selectRecent(url) {
  if (!url || url === previewImage.value) return;
  if (previewImage.value) addToRecent(previewImage.value);
  recentImages.value = recentImages.value.filter(i => i !== url);
  previewImage.value = url;
  const today = new Date().toISOString().slice(0, 10);
  const newSlot = { path: url, start: today, end: null };
  slots.value = [newSlot, ...(slots.value.slice(1) || [])].slice(0, 4);
  try {
    await fetch('/admin/backgrounds', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ slots: slots.value })
    });
  } catch (err) {
    console.error('persist slot error', err);
  }
}
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
          <h2 class="text-4xl font-bold text-white">Fond d'écran</h2>
          <p class="text-xl text-white">
            Modifier l’arrière-plan du tableau d’affichage
          </p>
          <hr class="border-t border-[#404040] mt-3" />
        </div>
      </div>

      <!-- Preview + Recents -->
      <div class="flex items-end space-x-6 ">
        <!-- big preview -->
        <img
          v-if="previewImage"
          :src="previewImage"
          alt="background"
          class="h-74 object-cover rounded-lg"
        />
        <img
          v-else
          :src="previewImage || defaultBackground"
          alt="background"
          class="h-74 object-cover rounded-lg"
        />

        <!-- recent images + import button -->
        <div class="flex-1 flex flex-col space-y-2 gap-4 bg-gray-700 rounded p-6">
          <h2 class="text-2xl font-bold text-white">Images récentes</h2>

          <!-- if there are recent images, show them -->
          <div
            v-if="recentImages.length"
            class="flex space-x-12 overflow-x-auto py-2"
          >
            <img
              v-for="img in recentImages"
              :key="img"
              :src="img"
              alt="thumbnail"
              class="w-36 h-24 object-cover rounded-lg cursor-pointer"
              @click="selectRecent(img)"
            />
          </div>

          <!-- otherwise show the dashed placeholder -->
          <div
            v-else
            class="rounded border-2 border-dashed border-gray-600 text-gray-400 font-bold justify-center items-center flex flex-col py-12 p-2"
          >
            <h3>Les images les plus récentes s'afficheront ici</h3>
          </div>

          
        </div>
      </div>

      <!-- Settings -->
      <div class="flex flex-col gap-4">
        <h2 class="text-2xl font-bold text-white">Paramètres</h2>
        <hr class="border-t border-[#404040] mt-3" />

        <ImageSelectorField
          type="file"
          accept="image/*"
          @change="handleFileUpload"
        />

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
