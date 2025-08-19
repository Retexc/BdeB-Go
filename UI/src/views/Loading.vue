<template>
  <!-- Double slide transition -->
  <div
    class="fixed inset-0 z-50 overflow-hidden pointer-events-none loading-overlay"
    :class="{ 'fade-out': overlayComplete }"
  >
    <div
      class="absolute h-full w-full bg-white transition-transform duration-1200 ease-in-out"
      :style="{ transform: `translateX(${yellowSlide}%)` }"
    ></div>
    <div
      class="absolute h-full w-full bg-white transition-transform duration-1200 ease-in-out"
      :style="{ transform: `translateX(${whiteSlide}%)`,
       backgroundColor: backgroundColor, 
       }"
    ></div>
  </div>

  <div
    class="fixed inset-0 z-40 min-h-screen flex flex-row justify-center items-center pl-16 overflow-hidden gap-8 loading-content"
    :class="{ 'fade-out': isComplete }"
    :style="{
      fontFamily: 'AtlasGrotesk, sans-serif',
      backgroundColor: backgroundColor,
    }"
  >
<!-- 100% pill -->
<div class="px-12 py-6 rounded-2xl" :style="{ backgroundColor: pillColor }">
  <h1
    class="text-6xl md:text-9xl"
    :style="{
      fontWeight: 900,
      color: pillTextColor,  
    }"
  >
    100%
  </h1>
  <div
    class="absolute inset-0 transition-transform duration-1800 ease-in-out"
    :style="{
      transform: `translateX(${maskPosition}%)`,
      backgroundColor: backgroundColor,
    }"
  ></div>
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
            color:
              word === principalWord ? principalTextColor : secondaryTextColor,
            opacity: word === principalWord ? '1' : '0.6',
          }"
        >
          {{ word }}.
        </h1>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  emits: ["loading-complete"],
  data() {
    return {
      scrollPosition: 1500,
      maskPosition: 0,
      yellowSlide: -100,
      whiteSlide: -120,
      isComplete: false,
      overlayComplete: false,
      // Default words and colors if localStorage is empty
      defaultWords: [
        "Motivé",
        "Cavalier",
        "Fier",
        "Réussite",
        "Ponctuel",
        "Heureux",
        "BdeB",
        "Ensemble",
      ],
      defaultColors: {
        principalTextColor: "#FFFFFF",
        secondaryTextColor: "#6B7280",
        backgroundColor: "#000000",
        pillColor: "#FFFFFF",
        pillTextColor: "#000000",
      },
    };
  },
  computed: {
    // Load words from localStorage
    wordsFromStorage() {
      try {
        const savedWords = localStorage.getItem("titleCard-words");
        return savedWords ? JSON.parse(savedWords) : this.defaultWords;
      } catch (error) {
        console.error("Error loading words from localStorage:", error);
        return this.defaultWords;
      }
    },

    // Load colors from localStorage
    colorsFromStorage() {
      try {
        const savedColors = localStorage.getItem("titleCard-colors");
        return savedColors ? JSON.parse(savedColors) : this.defaultColors;
      } catch (error) {
        console.error("Error loading colors from localStorage:", error);
        return this.defaultColors;
      }
    },

    // Individual color computed properties
    principalTextColor() {
      return this.colorsFromStorage.principalTextColor;
    },

    secondaryTextColor() {
      return this.colorsFromStorage.secondaryTextColor;
    },

    backgroundColor() {
      return this.colorsFromStorage.backgroundColor;
    },

    pillColor() {
      return this.colorsFromStorage.pillColor;
    },

    pillTextColor() {
      return this.colorsFromStorage.pillTextColor;
    },

    principalWord() {
      return this.wordsFromStorage[4] || this.wordsFromStorage[0] || "Ponctuel";
    },

    displayWords() {
      const wordsToShow = [...this.wordsFromStorage];
      while (wordsToShow.length < 9) {
        wordsToShow.push("Vous");
      }
      return wordsToShow;
    },
  },
  mounted() {
    console.log("Loading component mounted");

    setTimeout(() => {
      this.maskPosition = 100;
      console.log("Mask animation started");
    }, 200);

    setTimeout(() => {
      this.scrollPosition = 0;
      console.log("Scroll animation started");
    }, 700);

    setTimeout(() => {
      this.startDoubleSlide();
      console.log("Double slide started");
    }, 3000);

    setTimeout(() => {
      console.log("Slides covering screen - hiding content");
      this.isComplete = true;
    }, 3600);

    setTimeout(() => {
      console.log("Starting overlay fade out");
      this.overlayComplete = true;
    }, 4200);

    setTimeout(() => {
      console.log("Emitting loading-complete event");
      this.$emit("loading-complete");
    }, 5000);
  },
  methods: {
    startDoubleSlide() {
      this.yellowSlide = 100;
      this.whiteSlide = 0;
    },
  },
};
</script>

<style scoped>
.loading-overlay,
.loading-content {
  transition: opacity 0.8s ease-in-out;
}

.loading-overlay.fade-out,
.loading-content.fade-out {
  opacity: 0;
  pointer-events: none;
}
</style>
