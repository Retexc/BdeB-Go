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
import TextInput from "../components/TextInput.vue";

const active = ref("text");
const selectedCard = ref("loading");

const defaultWords = [
  "Motivé",
  "Cavalier",
  "Fier",
  "Réussite",
  "Ponctuel",
  "Heureux",
  "BdeB",
  "Ensemble",
];
const defaultColors = {
  principalTextColor: "#FFFFFF",
  secondaryTextColor: "#6B7280",
  backgroundColor: "#000000",
  pillColor: "#FFFFFF",
  pillTextColor: "#000000",
};

const defaultEndCardData = {
  message: "Passez une bonne journée !",
  backgroundColor: "#000000",
  textColor: "#FFFFFF",
};

// Default values for timing
const defaultSwitchInterval = 45; // seconds
const defaultTotalDisplayTime = 10; // minutes

const loadData = () => {
  try {
    const savedWords = localStorage.getItem("titleCard-words");
    const savedColors = localStorage.getItem("titleCard-colors");
    const savedEndCard = localStorage.getItem("titleCard-endcard");
    const savedSwitchInterval = localStorage.getItem(
      "titleCard-switchInterval"
    );
    const savedTotalDisplayTime = localStorage.getItem(
      "titleCard-totalDisplayTime"
    );

    return {
      words: savedWords ? JSON.parse(savedWords) : defaultWords,
      colors: savedColors ? JSON.parse(savedColors) : defaultColors,
      endCard: savedEndCard ? JSON.parse(savedEndCard) : defaultEndCardData,
      switchInterval: savedSwitchInterval
        ? JSON.parse(savedSwitchInterval)
        : defaultSwitchInterval,
      totalDisplayTime: savedTotalDisplayTime
        ? JSON.parse(savedTotalDisplayTime)
        : defaultTotalDisplayTime,
    };
  } catch (error) {
    console.error("Error loading saved data:", error);
    return {
      words: defaultWords,
      colors: defaultColors,
      endCard: defaultEndCardData,
      switchInterval: defaultSwitchInterval,
      totalDisplayTime: defaultTotalDisplayTime,
    };
  }
};

const savedData = loadData();

// Loading card data
const words = ref(savedData.words);
const principalTextColor = ref(savedData.colors.principalTextColor);
const secondaryTextColor = ref(savedData.colors.secondaryTextColor);
const backgroundColor = ref(savedData.colors.backgroundColor);
const pillColor = ref(savedData.colors.pillColor);
const pillTextColor = ref(savedData.colors.pillTextColor);

// End card data
const endCardMessage = ref(savedData.endCard.message);
const endCardBackgroundColor = ref(savedData.endCard.backgroundColor);
const endCardTextColor = ref(savedData.endCard.textColor);

// Timing data
const switchInterval = ref(savedData.switchInterval);
const totalDisplayTime = ref(savedData.totalDisplayTime);

const principalWord = computed(() => words.value[4] || words.value[0] || "");

const formattedEndCardMessage = computed(() => {
  const formatted = endCardMessage.value.replace(/\n/g, "<br>");
  return formatted;
});

const tabs = [
  { id: "text", label: "Texte" },
  { id: "looks", label: "Apparence" },
  { id: "switch_interval", label: "Intervalle de changement" },
];

const saveWords = () => {
  try {
    localStorage.setItem("titleCard-words", JSON.stringify(words.value));
  } catch (error) {
    console.error("Error saving words:", error);
  }
};

const saveColors = () => {
  try {
    const colors = {
      principalTextColor: principalTextColor.value,
      secondaryTextColor: secondaryTextColor.value,
      backgroundColor: backgroundColor.value,
      pillColor: pillColor.value,
      pillTextColor: pillTextColor.value,
    };
    localStorage.setItem("titleCard-colors", JSON.stringify(colors));
  } catch (error) {
    console.error("Error saving colors:", error);
  }
};

const saveEndCard = () => {
  try {
    const endCardData = {
      message: endCardMessage.value,
      backgroundColor: endCardBackgroundColor.value,
      textColor: endCardTextColor.value,
    };
    localStorage.setItem("titleCard-endcard", JSON.stringify(endCardData));
  } catch (error) {
    console.error("Error saving end card data:", error);
  }
};

const saveSwitchInterval = () => {
  try {
    localStorage.setItem(
      "titleCard-switchInterval",
      JSON.stringify(switchInterval.value)
    );
  } catch (error) {
    console.error("Error saving switch interval:", error);
  }
};

const saveTotalDisplayTime = () => {
  try {
    localStorage.setItem(
      "titleCard-totalDisplayTime",
      JSON.stringify(totalDisplayTime.value)
    );
  } catch (error) {
    console.error("Error saving total display time:", error);
  }
};

watch(
  words,
  () => {
    saveWords();
  },
  { deep: true }
);

watch(
  [
    principalTextColor,
    secondaryTextColor,
    backgroundColor,
    pillColor,
    pillTextColor,
  ],
  () => {
    saveColors();
  }
);

watch(
  [endCardMessage, endCardBackgroundColor, endCardTextColor],
  () => {
    saveEndCard();
  },
  { deep: true }
);

watch(switchInterval, () => {
  saveSwitchInterval();
});

watch(totalDisplayTime, () => {
  saveTotalDisplayTime();
});

const onPrincipalTextColorChange = (color) => {
  console.log("Principal text color changed:", color);
};

const onSecondaryTextColorChange = (color) => {
  console.log("Secondary text color changed:", color);
};

const onBackgroundColorChange = (color) => {
  console.log("Background color changed:", color);
};

const onPillColorChange = (color) => {
  console.log("Pill color changed:", color);
};

const onPillTextColorChange = (color) => {
  console.log("Text Pill color changed:", color);
};

const onEndCardBackgroundColorChange = (color) => {
  console.log("End card background color changed:", color);
};

const onEndCardTextColorChange = (color) => {
  console.log("End card text color changed:", color);
};

const onPrincipalChanged = () => {
  console.log("Principal word changed to:", principalWord.value);
};

const selectCard = (cardType) => {
  selectedCard.value = cardType;
  console.log("Card selected:", cardType);
};

onMounted(() => {
  console.log("TitleCard mounted with saved data");
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
    <div class="flex-1 flex flex-col p-6 space-y-2 mt-6 ml-5 mr-5">
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
            @click="selectCard('loading')"
            :class="[
              'w-150 h-86 border-2 rounded-lg overflow-hidden bg-black cursor-pointer transition-all duration-200',
              selectedCard === 'loading'
                ? 'border-blue-400 border-4'
                : 'border-[#404040] hover:border-gray-500',
            ]"
          >
            <LoadingPreview
              :principal-text-color="principalTextColor"
              :secondary-text-color="secondaryTextColor"
              :background-color="backgroundColor"
              :pill-color="pillColor"
              :pill-text-color="pillTextColor"
            />
          </div>

          <!-- End Card Preview -->
          <div
            @click="selectCard('endcard')"
            :class="[
              'w-150 h-86 border-2 rounded-lg overflow-hidden bg-black cursor-pointer transition-all duration-200',
              selectedCard === 'endcard'
                ? 'border-blue-400 border-4'
                : 'border-[#404040] hover:border-gray-500',
            ]"
          >
            <EndCardPreview
              :message="formattedEndCardMessage"
              :textColor="endCardTextColor"
              :backgroundColor="endCardBackgroundColor"
            />
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

        <!-- TAB CONTENT -->
        <div class="mb-6 w-full">
          <!-- Loading Card Settings -->
          <div v-if="selectedCard === 'loading'">
            <div v-if="active === 'text'" class="w-full">
              <WordList
                v-model="words"
                @principal-changed="onPrincipalChanged"
              />
            </div>

            <!-- Loading Card Appearance Tab -->
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

            <!-- Timing Tab -->
            <div
              v-else-if="active === 'switch_interval'"
              class="w-full space-y-4"
            >
              <TextInput
                v-model="totalDisplayTime"
                title="Temps d'affichage total (minutes)"
              />
              <TextInput
                v-model="switchInterval"
                title="Intervalle de changement d'écran STM/Exo (secondes)"
              />
            </div>
          </div>

          <!-- End Card Settings -->
          <div v-else-if="selectedCard === 'endcard'">
            <div v-if="active === 'text'" class="w-full">
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-white mb-2">
                    Message de fin
                  </label>
                  <textarea
                    v-model="endCardMessage"
                    rows="3"
                    class="w-full px-3 py-2 bg-[#1f1f1f] border border-[#404040] rounded-md text-white focus:outline-none focus:border-blue-500 resize-vertical"
                    placeholder="Entrez votre message... (utilisez une nouvelle ligne pour séparer les lignes)"
                  ></textarea>
                  <p class="text-xs text-gray-400 mt-1">
                    Astuce: Appuyez sur Entrée pour créer une nouvelle ligne
                  </p>
                </div>
              </div>
            </div>

            <!-- End Card Appearance Tab -->
            <div v-else-if="active === 'looks'" class="w-full">
              <div class="grid grid-cols-2 gap-6 max-w-8xl">
                <!-- Left Column -->
                <div class="space-y-2">
                  <ColorPicker
                    v-model="endCardTextColor"
                    title="Couleur du texte"
                    @change="onEndCardTextColorChange"
                  />
                </div>

                <!-- Right Column -->
                <div class="space-y-2">
                  <ColorPicker
                    v-model="endCardBackgroundColor"
                    title="Couleur d'arrière-plan"
                    @change="onEndCardBackgroundColorChange"
                  />
                </div>
              </div>
            </div>
            <div
              v-else-if="active === 'switch_interval'"
              class="w-full space-y-4"
            >
              <TextInput
                v-model="totalDisplayTime"
                title="Temps d'affichage total (minutes)"
              />
              <TextInput
                v-model="switchInterval"
                title="Intervalle de changement d'écran STM/Exo (secondes)"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </motion.div>
</template>
