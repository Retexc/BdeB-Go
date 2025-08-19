<script setup>
import { ref, watch, onMounted, computed } from "vue";
import { motion } from "motion-v";
import ImageSelectorField from "../components/ImageSelectorField.vue";
import placeholderBg from '../assets/images/background.png';

const previewImage = ref('');
const recentImages = ref([]);
const slots = ref([]);
const overlayOpacity = ref(0.65); // Default 65% overlay
const MAX_RECENTS = 4;
const defaultBackground = '../assets/images/background.png';

// Computed style for preview image overlay
const previewOverlayStyle = computed(() => ({
  backgroundColor: `rgba(0, 0, 0, ${overlayOpacity.value})`
}));

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

// Watch overlay opacity changes and persist to localStorage
watch(overlayOpacity, (newValue) => {
  try {
    localStorage.setItem('backgroundOverlayOpacity', JSON.stringify(newValue));
    // Also send to server to update the display overlay
    updateServerOverlay(newValue);
  } catch (e) {
    console.warn('failed to save overlay opacity', e);
  }
}, { immediate: false });

watch(
  recentImages,
  v => {
    try {
      localStorage.setItem('recentBgImages', JSON.stringify(v.slice(0, MAX_RECENTS)));
    } catch {}
  },
  { deep: true }
);

async function updateServerOverlay(opacity) {
  try {
    // Try multiple endpoints to ensure compatibility
    const promises = [
      fetch('/admin/backgrounds/overlay', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ opacity })
      }),
      fetch('http://127.0.0.1:5001/admin/backgrounds/overlay', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ opacity })
      })
    ];
    
    await Promise.allSettled(promises);
  } catch (err) {
    console.error('Failed to update server overlay', err);
  }
}

onMounted(async () => {
  try {
    const stored = localStorage.getItem('recentBgImages');
    if (stored) {
      recentImages.value = JSON.parse(stored).slice(0, MAX_RECENTS);
    }
  } catch (e) {
    console.warn('failed to load recentImages', e);
  }

  // Load saved overlay opacity
  try {
    const storedOpacity = localStorage.getItem('backgroundOverlayOpacity');
    if (storedOpacity) {
      overlayOpacity.value = JSON.parse(storedOpacity);
    }
  } catch (e) {
    console.warn('failed to load overlay opacity', e);
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

function handleOverlayChange(e) {
  overlayOpacity.value = parseFloat(e.target.value);
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
            Modifier l'arrière-plan du tableau d'affichage
          </p>
          <hr class="border-t border-[#404040] mt-3" />
        </div>
      </div>

      <!-- Preview + Recents -->
      <div class="flex items-end space-x-6 ">
        <!-- big preview with overlay -->
        <div class="relative">
          <img
            v-if="previewImage"
            :src="previewImage"
            alt="background"
            class="h-74 object-cover rounded-lg"
            @error="onPreviewError"
          />
          <img
            v-else
            :src="previewImage || defaultBackground"
            alt="background"
            class="h-74 object-cover rounded-lg"
            @error="onPreviewError"
          />
          <!-- Dark overlay -->
          <div 
            class="absolute inset-0 rounded-lg"
            :style="previewOverlayStyle"
          ></div>
          
          <!-- Overlay percentage indicator -->
          <div class="absolute bottom-2 right-2 bg-black bg-opacity-50 text-white text-sm px-2 py-1 rounded">
            {{ Math.round(overlayOpacity * 100) }}%
          </div>
        </div>

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

        <!-- Dark Overlay Control -->
        <div class="flex flex-col gap-2">
          <label class="text-white font-medium">Superposition sombre</label>
          <div class="flex items-center gap-4">
            <span class="text-white text-sm">0%</span>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              :value="overlayOpacity"
              @input="handleOverlayChange"
              class="flex-1 h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer
                     [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:h-5 [&::-webkit-slider-thumb]:w-5 
                     [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-blue-500 
                     [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:border-2 
                     [&::-webkit-slider-thumb]:border-blue-800
                     [&::-moz-range-thumb]:h-5 [&::-moz-range-thumb]:w-5 [&::-moz-range-thumb]:rounded-full 
                     [&::-moz-range-thumb]:bg-blue-500 [&::-moz-range-thumb]:cursor-pointer 
                     [&::-moz-range-thumb]:border-2 [&::-moz-range-thumb]:border-blue-800
                     [&::-webkit-slider-track]:bg-gray-600 [&::-webkit-slider-track]:h-2 [&::-webkit-slider-track]:rounded
                     [&::-moz-range-track]:bg-gray-600 [&::-moz-range-track]:h-2 [&::-moz-range-track]:rounded"
            />
            <span class="text-white text-sm">100%</span>
            <div class="text-white text-sm font-medium min-w-[3rem]">
              {{ Math.round(overlayOpacity * 100) }}%
            </div>
          </div>
          <p class="text-gray-400 text-sm">
            Ajustez l'opacité de la superposition sombre appliquée au fond d'écran
          </p>
        </div>

      </div>
    </div>

  </motion.div>
</template>