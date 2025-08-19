<template>
  <div class="text-white font-sans w-full">
    <!-- Header with title and crown icon -->
    <div class="flex items-center mb-4">
      <div class="mr-3">
        <svg class="w-6 h-6 text-yellow-400" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M5 16L3 7L5.5 9.5L8 7L10.5 9.5L13 7L15.5 9.5L18 7L21 16H5Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M5 16V20H19V16" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <h2 class="text-lg font-semibold text-white m-0">Liste des mots</h2>
    </div>

    <!-- Word tags container -->
    <div class="flex items-end gap-4 w-full">
      <div class="flex flex-wrap gap-2 flex-1 min-w-0 items-end">
        <div 
          v-for="(word, index) in words" 
          :key="`${word}-${index}`"
          class="relative inline-flex flex-col items-center cursor-move select-none mt-6 transition-all duration-200"
          :class="{
            'opacity-50 rotate-1 z-50': draggedIndex === index,
            '-translate-y-0.5 shadow-lg shadow-yellow-400/40': dragOverIndex === index
          }"
          draggable="true"
          @dragstart="onDragStart(index)"
          @dragover="onDragOver($event, index)"
          @dragleave="onDragLeave"
          @drop="onDrop($event, index)"
          @dragend="onDragEnd"
        >
          <svg 
            v-if="index === props.crownPosition" 
            class="absolute -top-5 left-1/2 transform -translate-x-1/2 w-5 h-5 text-yellow-400 z-10 drop-shadow-sm"
            viewBox="0 0 24 24" 
            fill="none" 
            xmlns="http://www.w3.org/2000/svg"
          >
            <path d="M5 16L3 7L5.5 9.5L8 7L10.5 9.5L13 7L15.5 9.5L18 7L21 16H5Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M5 16V20H19V16" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <div 
            class="inline-flex items-center bg-yellow-400 text-gray-900 px-3 py-1.5 rounded-full text-sm font-medium gap-1.5 transition-all duration-200 hover:bg-yellow-500 hover:-translate-y-0.5"
            :class="{
              'bg-yellow-300 border-2 border-yellow-500 font-semibold shadow-lg shadow-yellow-400/40': index === props.crownPosition
            }"
          >
            <span class="whitespace-nowrap">{{ word }}</span>
            <button 
              @click="removeWord(index)"
              class="flex items-center justify-center w-5 h-5 text-gray-900 text-lg font-bold rounded-full transition-colors duration-200 hover:bg-black hover:bg-opacity-10"
              :aria-label="`Remove ${word}`"
            >
              ×
            </button>
          </div>
        </div>
      </div>

      <!-- Limit reached indicator -->
      <div v-if="isLimitReached" class="text-gray-400 text-sm italic px-3 py-2 border border-dashed border-gray-600 rounded whitespace-nowrap flex-shrink-0">
        Limite atteinte
      </div>
    </div>

    <!-- Input field for adding new words -->
    <div class="mt-4 w-full">
      <div class="flex gap-2 w-full max-w-md">
        <input 
          v-model="newWord"
          @keyup.enter="handleAddWord"
          :disabled="isLimitReached"
          :placeholder="isLimitReached ? 'Limite atteinte' : 'Ajouter un mot...'"
          class="flex-1 bg-gray-800 border border-gray-600 rounded-md px-3 py-2 text-white text-sm transition-all duration-200 focus:outline-none focus:border-yellow-400 focus:bg-gray-700 disabled:bg-gray-900 disabled:border-gray-700 disabled:text-gray-500 disabled:cursor-not-allowed placeholder:text-gray-400"
        />
        <button 
          @click="handleAddWord"
          :disabled="isLimitReached || !newWord.trim()"
          class="bg-yellow-400 text-gray-900 border-0 rounded-md px-4 py-2 text-sm font-medium cursor-pointer transition-all duration-200 whitespace-nowrap hover:bg-yellow-500 hover:-translate-y-0.5 disabled:bg-gray-600 disabled:text-gray-500 disabled:cursor-not-allowed disabled:transform-none"
        >
          Ajouter
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// Props
const props = defineProps({
  modelValue: {
    type: Array,
    default: () => ['Motivé', 'Cavalier', 'Fier', 'Réussite', 'Ponctuel', 'Heureux', 'BdeB', 'Ensemble']
  },
  maxWords: {
    type: Number,
    default: 8
  },
  crownPosition: {
    type: Number,
    default: 4 // 5th position (0-indexed)
  }
})

// Reactive data
const words = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})
const newWord = ref('')
const draggedIndex = ref(null)
const dragOverIndex = ref(null)

// Emits
const emit = defineEmits(['update:modelValue', 'principal-changed'])

// Computed properties
const isLimitReached = computed(() => words.value.length >= props.maxWords)
const principalWord = computed(() => words.value[props.crownPosition] || null)

// Methods
const removeWord = (index) => {
  const newWords = [...words.value]
  newWords.splice(index, 1)
  words.value = newWords
  if (index === props.crownPosition) {
    emit('principal-changed')
  }
}

const addWord = (word) => {
  if (words.value.length < props.maxWords && !words.value.includes(word.trim()) && word.trim()) {
    const newWords = [...words.value, word.trim()]
    words.value = newWords
    return true
  }
  return false
}

const handleAddWord = () => {
  if (newWord.value.trim() && addWord(newWord.value)) {
    newWord.value = ''
  }
}

// Drag and drop methods
const onDragStart = (index) => {
  draggedIndex.value = index
}

const onDragOver = (event, index) => {
  event.preventDefault()
  dragOverIndex.value = index
}

const onDragLeave = () => {
  dragOverIndex.value = null
}

const onDrop = (event, dropIndex) => {
  event.preventDefault()
  
  if (draggedIndex.value !== null && draggedIndex.value !== dropIndex) {
    const newWords = [...words.value]
    const draggedWord = newWords[draggedIndex.value]
    newWords.splice(draggedIndex.value, 1)
    newWords.splice(dropIndex, 0, draggedWord)
    words.value = newWords
    emit('principal-changed') // Always emit since the principal word position might change
  }
  
  draggedIndex.value = null
  dragOverIndex.value = null
}

const onDragEnd = () => {
  draggedIndex.value = null
  dragOverIndex.value = null
}

// Expose methods for parent component
defineExpose({
  addWord,
  removeWord,
  words: words,
  isLimitReached,
  principalWord
})
</script>