<template>
  <div>
    <!-- Label -->
    <label class="block text-lg font-bold text-white mb-2 ">
      Image
    </label>

    <!-- Row: readonly text box + import button -->
    <div class="flex items-center gap-2">
      <!-- shows the chosen file’s path/name -->
      <input
        v-model="fileName"
        type="text"
        readonly
        placeholder="Aucune image sélectionnée"
        class="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none"
      />

      <!-- opens OS file picker -->
      <button
        type="button"
        @click="pickFile"
        class="inline-flex items-center px-4 py-2 bg-yellow-400 text-black rounded-lg hover:bg-yellow-500 font-bold"
      >
        <!-- upload icon -->
        <svg
          class="w-5 h-5 mr-1"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1M12 12V4m0 0l-3 3m3-3l3 3"
          />
        </svg>
        Importer une image
      </button>

      <!-- hidden native file input -->
      <input
        ref="uploader"
        type="file"
        accept="image/*"
        class="hidden"
        @change="onFileSelected"
      />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const fileName = ref('')
const uploader = ref(null)

function pickFile() {
  uploader.value.click()
}

function onFileSelected(ev) {
  const file = ev.target.files[0]
  if (file) {
    // file.name is just the filename;
    // ev.target.value might give the full path in some browsers
    fileName.value = file.name
    // If you need to preview or upload:
    // const reader = new FileReader()
    // reader.onload = () => { previewSrc.value = reader.result }
    // reader.readAsDataURL(file)
  }
}
</script>

<style scoped>
/* All styling via Tailwind utilities */
</style>
