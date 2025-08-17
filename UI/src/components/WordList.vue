<template>
  <div class="text-white font-sans w-full">
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
  initialWords: {
    type: Array,
    default: () => ['Motivé', 'Cavalier', 'Fier', 'Réussite', 'Ponctuel', 'Heureux', 'BdeB', 'Ensemble']
  },
  maxWords: {
    type: Number,
    default: 8
  },
  crownPosition: {
    type: Number,
    default: 4 
  }
})

const words = ref([...props.initialWords])
const newWord = ref('')
const draggedIndex = ref(null)
const dragOverIndex = ref(null)

const isLimitReached = computed(() => words.value.length >= props.maxWords)
const principalWord = computed(() => words.value[props.crownPosition] || null)

const removeWord = (index) => {
  words.value.splice(index, 1)
}

const addWord = (word) => {
  if (words.value.length < props.maxWords && !words.value.includes(word.trim()) && word.trim()) {
    words.value.push(word.trim())
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
    const draggedWord = words.value[draggedIndex.value]
    words.value.splice(draggedIndex.value, 1)
    words.value.splice(dropIndex, 0, draggedWord)
  }
  
  draggedIndex.value = null
  dragOverIndex.value = null
}

const onDragEnd = () => {
  draggedIndex.value = null
  dragOverIndex.value = null
}

defineExpose({
  addWord,
  removeWord,
  words: words,
  isLimitReached,
  principalWord
})
</script>

<style scoped>
.word-list-container {
  background-color: transparent;
  color: white;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  width: 100%;
}

.header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.title-section {
  margin-right: 12px;
}

.crown-icon {
  width: 24px;
  height: 24px;
  color: #fbbf24;
}

.title {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: white;
}

.words-container {
  display: flex;
  align-items: flex-end;
  gap: 16px;
  flex-wrap: nowrap;
  width: 100%;
}

.word-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  flex: 1;
  min-width: 0;
  align-items: flex-end;
}

.word-wrapper {
  position: relative;
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  cursor: move;
  user-select: none;
  margin-top: 24px; /* Space for crown */
}

.word-wrapper.dragging {
  opacity: 0.5;
  transform: rotate(5deg);
  z-index: 1000;
}

.word-wrapper.drag-over {
  transform: translateY(-2px);
}

.crown-top {
  position: absolute;
  top: -22px;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 20px;
  color: #fbbf24;
  z-index: 10;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.3));
}

.word-tag {
  display: inline-flex;
  align-items: center;
  background-color: #fbbf24;
  color: #1a1a1a;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  gap: 6px;
  transition: all 0.2s ease;
}

.word-tag:hover {
  background-color: #f59e0b;
  transform: translateY(-1px);
}

.word-wrapper.drag-over .word-tag {
  box-shadow: 0 4px 12px rgba(251, 191, 36, 0.4);
}

.word-tag.crowned,
.word-tag.crown-position {
  background-color: #fcd34d;
  border: 2px solid #f59e0b;
  font-weight: 600;
}

.crown-small {
  width: 16px;
  height: 16px;
  color: #1a1a1a;
  flex-shrink: 0;
}

.word-text {
  white-space: nowrap;
}

.remove-btn {
  background: none;
  border: none;
  color: #1a1a1a;
  font-size: 18px;
  font-weight: bold;
  cursor: pointer;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s ease;
}

.remove-btn:hover {
  background-color: rgba(0, 0, 0, 0.1);
}

.limit-indicator {
  color: #9ca3af;
  font-size: 14px;
  font-style: italic;
  padding: 8px 12px;
  border: 1px dashed #4b5563;
  border-radius: 4px;
  white-space: nowrap;
  flex-shrink: 0;
}

.input-container {
  margin-top: 16px;
  width: 100%;
}

.input-wrapper {
  display: flex;
  gap: 8px;
  width: 100%;
  max-width: 400px;
}

.word-input {
  flex: 1;
  background-color: #2a2a2a;
  border: 1px solid #404040;
  border-radius: 6px;
  padding: 8px 12px;
  color: white;
  font-size: 14px;
  transition: border-color 0.2s ease, background-color 0.2s ease;
}

.word-input:focus {
  outline: none;
  border-color: #fbbf24;
  background-color: #333333;
}

.word-input::placeholder {
  color: #9ca3af;
}

.word-input.disabled {
  background-color: #1a1a1a;
  border-color: #2a2a2a;
  color: #666666;
  cursor: not-allowed;
}

.word-input.disabled::placeholder {
  color: #666666;
}

.add-btn {
  background-color: #fbbf24;
  color: #1a1a1a;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease, transform 0.2s ease;
  white-space: nowrap;
}

.add-btn:hover:not(.disabled) {
  background-color: #f59e0b;
  transform: translateY(-1px);
}

.add-btn.disabled {
  background-color: #404040;
  color: #666666;
  cursor: not-allowed;
  transform: none;
}

/* Responsive design */
@media (max-width: 640px) {
  .word-list-container {
    padding: 12px;
  }
  
  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .words-container {
    flex-direction: column;
    align-items: stretch;
  }
  
  .word-tags {
    justify-content: center;
  }

  .input-wrapper {
    flex-direction: column;
    max-width: none;
  }
}
</style>