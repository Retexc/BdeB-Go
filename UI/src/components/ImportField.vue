<template>
  <div>
    <!-- Label -->

    <!-- Row: readonly text box + import button -->
    <div class="flex items-center gap-2">
      <label class="block text-lg font-bold text-white mb-2">
        Fichier GTFS (ZIP) :
      </label>
      <!-- shows the chosen file’s path/name -->
      <input
        ref="fileInput"
        type="file"
        accept=".zip"
        @change="onFileChange"
        placeholder="Aucune fichier sélectionnée"
        class="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none"
      />

      <!-- opens OS file picker -->
      <button
        type="button"
        @click="trigger"
        class="inline-flex items-center px-4 py-2 bg-blue-400 text-black rounded-lg hover:bg-blue-500 font-bold"
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
        Importer
      </button>

      <!-- hidden native file input -->

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  transport: { type: String, required: true }, // 'stm' or 'exo'
  placeholder: { type: String, default: 'Aucun fichier sélectionné' },
  uploadUrl: { type: String, default: '/admin/update_gtfs' },
})
const emit = defineEmits(['start', 'done', 'error'])

const fileInput = ref(null)
const selectedName = ref('')

function trigger() {
  fileInput.value?.click()
}

async function onFileChange(e) {
  const file = e.target.files?.[0]
  if (!file) return

  if (!file.name.toLowerCase().endsWith('.zip')) {
    emit('error', { transport: props.transport, message: 'Seuls les .zip sont acceptés' })
    return
  }

  selectedName.value = file.name
  emit('start', { transport: props.transport, filename: file.name })

  const form = new FormData()
  form.append('transport', props.transport)
  form.append('gtfs_zip', file)

  try {
    const res = await fetch(props.uploadUrl, {
      method: 'POST',
      body: form,
    })
    const body = await res.json()
    if (res.ok) {
      emit('done', { transport: props.transport, updated_at: body.updated_at, result: body })
    } else {
      emit('error', { transport: props.transport, message: body.error || 'Échec de l\'import' })
    }
  } catch (err) {
    emit('error', { transport: props.transport, message: err.message || 'Erreur réseau' })
  } finally {
    // allow re-selecting same file if needed
    if (fileInput.value) fileInput.value.value = ''
  }
}
</script>

<style scoped>
/* All styling via Tailwind utilities */
</style>
