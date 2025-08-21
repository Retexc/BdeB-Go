<template>
  <div class="preview-viewport" :style="{ background: backgroundColor }">
    <div class="preview-content">
      <div
        class="fixed inset-0 z-40 min-h-screen flex flex-row justify-center items-center pl-16 overflow-hidden gap-8"
        :style="{ 
          fontFamily: 'AtlasGrotesk, sans-serif',
          backgroundColor: backgroundColor 
        }"
      >
        <!-- 100% pill -->
        <div
          class="flex justify-center px-14 py-6 rounded-2xl relative overflow-hidden"
          :style="{ backgroundColor: pillColor }"
        >
          <h1
            class="text-6xl md:text-8xl"
            :style="{ 
              fontWeight: 900, 
              color: pillTextColor 
            }"
          >
            {{ progressText }}
          </h1>
        </div>

        <!-- Animated Words Container -->
        <div class="relative h-screen overflow-hidden w-full flex items-center">
          <div
            class="space-y-6 transition-transform duration-2000 ease-in-out"
            :style="{ transform: `translateY(${scrollPosition}px)` }"
          >
            <h1
              v-for="(word, index) in displayWords"
              :key="`word-${index}`"
              class="text-6xl md:text-9xl leading-tight transition-colors duration-500"
              :style="{ 
                fontWeight: 900,
                color: word === principalWord ? principalTextColor : secondaryTextColor,
                opacity: word === principalWord ? '1' : '0.6'
              }"
            >
              {{ word }}.
            </h1>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps({
  progressText: { type: String, default: "100%" },
  principalTextColor: { type: String, default: "#FFFFFF" },  // Principal word color (Ponctuel)
  secondaryTextColor: { type: String, default: "#6B7280" },  // Other words color (grayed out)
  backgroundColor: { type: String, default: "#000000" },     // Page background color
  pillColor: { type: String, default: "#FFFFFF" },          // 100% pill background color
});

// Default values if localStorage is empty
const defaultWords = ['Motivé', 'Cavalier', 'Fier', 'Réussite', 'Ponctuel', 'Heureux', 'BdeB', 'Ensemble'];
const defaultColors = {
  principalTextColor: '#FFFFFF',
  secondaryTextColor: '#6B7280',
  backgroundColor: '#000000',
  pillColor: '#FFFFFF',
  pillTextColor: '#000000'
};


const scrollPosition = ref(0);


const wordsFromStorage = ref([]);
const colorsFromStorage = ref({});


const loadData = () => {
  try {
    // Load words
    const savedWords = localStorage.getItem('titleCard-words');
    const words = savedWords ? JSON.parse(savedWords) : defaultWords;
    wordsFromStorage.value = words;
    
    // Load colors
    const savedColors = localStorage.getItem('titleCard-colors');
    const colors = savedColors ? JSON.parse(savedColors) : defaultColors;
    colorsFromStorage.value = colors;
    
    console.log('LoadingPreview: Data loaded from localStorage:', { words, colors });
    return { words, colors };
  } catch (error) {
    console.error('Error loading data from localStorage:', error);
    wordsFromStorage.value = defaultWords;
    colorsFromStorage.value = defaultColors;
    return { words: defaultWords, colors: defaultColors };
  }
};

// Use colors from localStorage instead of props (for real-time updates)
const principalTextColor = computed(() => colorsFromStorage.value.principalTextColor || defaultColors.principalTextColor);
const secondaryTextColor = computed(() => colorsFromStorage.value.secondaryTextColor || defaultColors.secondaryTextColor);
const backgroundColor = computed(() => colorsFromStorage.value.backgroundColor || defaultColors.backgroundColor);
const pillColor = computed(() => colorsFromStorage.value.pillColor || defaultColors.pillColor);
const pillTextColor = computed(() => colorsFromStorage.value.pillTextColor || defaultColors.pillTextColor);

const principalWord = computed(() => {
  return wordsFromStorage.value[4] || wordsFromStorage.value[0] || 'Ponctuel';
});


const displayWords = computed(() => {
  const wordsToShow = [...wordsFromStorage.value];
  while (wordsToShow.length < 9) {
    wordsToShow.push('Vous');
  }
  return wordsToShow;
});

// Check for localStorage changes periodically
let intervalId = null;

const checkForUpdates = () => {
  try {
    // Check for word changes
    const savedWords = localStorage.getItem('titleCard-words');
    const currentWords = savedWords ? JSON.parse(savedWords) : defaultWords;
    
    // Check for color changes
    const savedColors = localStorage.getItem('titleCard-colors');
    const currentColors = savedColors ? JSON.parse(savedColors) : defaultColors;
    
    // Update words if changed
    if (JSON.stringify(currentWords) !== JSON.stringify(wordsFromStorage.value)) {
      console.log('LoadingPreview: Detected word change in localStorage, updating...');
      wordsFromStorage.value = currentWords;
    }
    
    // Update colors if changed
    if (JSON.stringify(currentColors) !== JSON.stringify(colorsFromStorage.value)) {
      console.log('LoadingPreview: Detected color change in localStorage, updating...');
      colorsFromStorage.value = currentColors;
    }
  } catch (error) {
    console.error('Error checking localStorage updates:', error);
  }
};

onMounted(() => {
  loadData();
  
  console.log('LoadingPreview mounted with data:', {
    words: wordsFromStorage.value,
    colors: colorsFromStorage.value,
    principalWord: principalWord.value
  });
  
  // Start polling for changes every 100ms
  intervalId = setInterval(checkForUpdates, 100);
});

onUnmounted(() => {
  if (intervalId) {
    clearInterval(intervalId);
  }
});


watch(wordsFromStorage, (newWords) => {
  console.log('LoadingPreview: Words changed to:', newWords);
  console.log('LoadingPreview: Principal word is now:', principalWord.value);
}, { deep: true });

watch(colorsFromStorage, (newColors) => {
  console.log('LoadingPreview: Colors changed to:', newColors);
}, { deep: true });
</script>

<style scoped>
.preview-viewport {
  width: 100%;
  height: 100%;
  overflow: hidden;
  position: relative;
  background: v-bind(backgroundColor);
}

.preview-content {
  width: 1920px; /* Fixed "screen" width */
  height: 1080px; /* Fixed "screen" height */
  transform: scale(0.31); /* Scale to fit container */
  transform-origin: top left;
  position: absolute;
  top: 0;
  left: 0;
}
</style>