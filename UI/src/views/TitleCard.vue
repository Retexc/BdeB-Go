<script setup>
import { ref, watch, onMounted, computed } from "vue";
import { motion } from "motion-v";
import ImageSelectorField from "../components/ImageSelectorField.vue";
import placeholderBg from "../assets/images/background.png";
import Loading from "./Loading.vue";
import LoadingPreview from "../components/LoadingPreview.vue";
import EndCardPreview from "../components/EndCardPreview.vue";
import WordList from "../components/WordList.vue";
import ColorPicker from "../components/ColorPicker.vue";

const active = ref('text');

// Default values 
const defaultWords = ['Motivé', 'Cavalier', 'Fier', 'Réussite', 'Ponctuel', 'Heureux', 'BdeB', 'Ensemble'];
const defaultColors = {
  principalTextColor: '#FFFFFF',  // "Couleur texte principal" - Principal word (Ponctuel)
  secondaryTextColor: '#6B7280',  // "Couleur texte secondaire" - Other grayed words
  backgroundColor: '#000000',     // "Couleur d'arrière-plan" - Page background
  pillColor: '#FFFFFF' ,          // "Couleur de la pillule" - 100% pill background
  pillTextColor: '#000000'       // "Couleur du texte de la pillule" - Pill text
};

const loadData = () => {
  try {
    const savedWords = localStorage.getItem('titleCard-words');
    const savedColors = localStorage.getItem('titleCard-colors');
    
    return {
      words: savedWords ? JSON.parse(savedWords) : defaultWords,
      colors: savedColors ? JSON.parse(savedColors) : defaultColors
    };
  } catch (error) {
    console.error('Error loading saved data:', error);
    return {
      words: defaultWords,
      colors: defaultColors
    };
  }
};

// Initialize with saved data
const savedData = loadData();

const words = ref(savedData.words);
const principalTextColor = ref(savedData.colors.principalTextColor);  
const secondaryTextColor = ref(savedData.colors.secondaryTextColor); 
const backgroundColor = ref(savedData.colors.backgroundColor);         
const pillColor = ref(savedData.colors.pillColor);                   
const pillTextColor = ref(savedData.colors.pillTextColor);           

const principalWord = computed(() => words.value[4] || words.value[0] || '');

const tabs = [
  { id: "text", label: "Texte" },
  { id: "looks", label: "Apparence" },
];

// Save functions
const saveWords = () => {
  try {
    localStorage.setItem('titleCard-words', JSON.stringify(words.value));
  } catch (error) {
    console.error('Error saving words:', error);
  }
};

const saveColors = () => {
  try {
    const colors = {
      principalTextColor: principalTextColor.value,
      secondaryTextColor: secondaryTextColor.value,
      backgroundColor: backgroundColor.value,
      pillColor: pillColor.value,
      pillTextColor: pillTextColor.value
    };
    localStorage.setItem('titleCard-colors', JSON.stringify(colors));
  } catch (error) {
    console.error('Error saving colors:', error);
  }
};

// Watch for changes and save
watch(words, () => {
  saveWords();
  console.log('Words saved:', words.value);
}, { deep: true });

watch([principalTextColor, secondaryTextColor, backgroundColor, pillColor, pillTextColor], () => {
  saveColors();
  console.log('Colors saved:', {
    principalTextColor: principalTextColor.value,
    secondaryTextColor: secondaryTextColor.value,
    backgroundColor: backgroundColor.value,
    pillColor: pillColor.value,
    pillTextColor: pillTextColor.value  
  });
});

// CLEAR Color change handlers
const onPrincipalTextColorChange = (color) => {
  console.log('Principal text color changed:', color);
};

const onSecondaryTextColorChange = (color) => {
  console.log('Secondary text color changed:', color);
};

const onBackgroundColorChange = (color) => {
  console.log('Background color changed:', color);
};

const onPillColorChange = (color) => {
  console.log('Pill color changed:', color);
};

const onPillTextColorChange = (color) => {
  console.log('Text Pill color changed:', color);
};

// Handle principal word changes
const onPrincipalChanged = () => {
  console.log('Principal word changed to:', principalWord.value);
};

onMounted(async () => {
  console.log('TitleCard mounted with saved data:', {
    words: words.value,
    principalWord: principalWord.value,
    colors: {
      principalTextColor: principalTextColor.value,
      secondaryTextColor: secondaryTextColor.value,
      backgroundColor: backgroundColor.value,
      pillColor: pillColor.value,
      pillTextColor: pillTextColor.value
    }
  });
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
      <!-- Header -->
      <div class="flex items-center justify-between w-full">
        <div class="space-y-1 w-full">
          <h2 class="text-4xl font-bold text-white">Écran-titre</h2>
          <p class="text-xl text-white">
            Modifier l'apparence de l'écran-titre
          </p>
          <hr class="border-t border-[#404040] mt-3" />
        </div>
      </div>

      <!-- Preview + Recents -->
      <div class="flex flex-col gap-4">
        <h2 class="text-2xl font-bold text-white">Aperçu</h2>
        <div class="flex flex-row gap-6 justify-between">
          <!-- Loading Preview -->
          <div
            class="w-150 h-86 border-2 border-[#404040] rounded-lg overflow-hidden bg-black"
          >
            <LoadingPreview 
              :principal-text-color="principalTextColor"
              :secondary-text-color="secondaryTextColor"
              :background-color="backgroundColor"
              :pill-color="pillColor"
              :pill-text-color="pillTextColor"
            />
          </div>
          <div
            class="w-150 h-86 border-2 border-[#404040] rounded-lg overflow-hidden bg-black"
          >
            <EndCardPreview />
          </div>
        </div>
      </div>

      <!-- Settings -->
      <div class="flex flex-col gap-4">
        <h2 class="text-2xl font-bold text-white">Paramètres</h2>
        <div
          class="mt-2 text-sm font-medium text-center text-gray-500 border-b border-gray-200"
        >
          <ul class="flex flex-wrap -mb-px">
            <li v-for="tab in tabs" :key="tab.id" class="mr-2">
              <a href="#"
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

        <!-- TAB CONTENT -->
        <div class="mb-6 w-full">
          <div v-if="active === 'text'" class="w-full">
            <WordList 
              v-model="words"
              @principal-changed="onPrincipalChanged"
            />
          </div>
          
          <!-- Appearance Tab -->
          <div v-else-if="active === 'looks'" class="w-full">
            <div class="grid grid-cols-2 gap-6 max-w-8xl">
              <!-- Left Column -->
              <div class="space-y-2">
                <ColorPicker 
                  v-model="principalTextColor"
                  title="Couleur texte principal"
                  @change="onPrincipalTextColorChange"
                />
                
                <ColorPicker 
                  v-model="secondaryTextColor"
                  title="Couleur texte secondaire"
                  @change="onSecondaryTextColorChange"
                />
                <ColorPicker 
                  v-model="pillTextColor"
                  title="Couleur texte de la pillule"
                  @change="onPillTextColorChange"
                />

              </div>
              
              <!-- Right Column -->
              <div class="space-y-2">
                <ColorPicker 
                  v-model="backgroundColor"
                  title="Couleur d'arrière-plan"
                  @change="onBackgroundColorChange"
                />
                
                <ColorPicker 
                  v-model="pillColor"
                  title="Couleur de la pillule"
                  @change="onPillColorChange"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </motion.div>
</template>