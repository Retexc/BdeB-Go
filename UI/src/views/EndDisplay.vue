<template>
  <div
    class="fixed inset-0 z-40 min-h-screen flex flex-row justify-center items-center pl-16 overflow-hidden gap-8"
    :style="{ 
      fontFamily: 'AtlasGrotesk, sans-serif',
      backgroundColor: backgroundColor
    }"
  >
    <div class="relative h-screen overflow-hidden w-full flex items-center">
      <div 
        class="space-y-6 transition-transform duration-2000 ease-in-out"
      >
        <h1
          class="text-6xl md:text-9xl leading-tight transition-all delay-300 duration-700 ease-in-out"
          :class="isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'"
          :style="{ 
            fontWeight: 900,
            color: textColor 
          }"
          v-html="displayMessage"
        >
        </h1>
      </div>
      
      <img 
        id="fadeInElement" 
        src="../assets/icons/bdeb.svg" 
        alt="" 
        class="fixed bottom-0 right-0 my-18 mr-18 transition-all delay-1500 duration-700 ease-in-out w-72 h-auto"
        :class="isVisible ? 'opacity-100' : 'opacity-0'"
      />

      <img 
        src="../assets/images/pink_b.svg" 
        alt="" 
        class="fixed bottom-0 left-0 w-76 h-auto transition-all delay-600 duration-700 ease-in-out"
        :class="isVisible ? 'translate-y-0' : 'translate-y-70'"
      />

      <img 
        src="../assets/images/purple_b.svg" 
        alt="" 
        class="fixed bottom-0 left-25 w-52 h-auto transition-all delay-900 duration-700 ease-in-out"
        :class="isVisible ? 'translate-y-0' : 'translate-y-28'"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'

const isVisible = ref(false)

// Load end card data from localStorage
const displayMessage = computed(() => {
  try {
    const savedEndCard = localStorage.getItem('titleCard-endcard')
    if (savedEndCard) {
      const endCardData = JSON.parse(savedEndCard)
      return endCardData.message.replace(/\n/g, '<br>')
    }
  } catch (error) {
    console.error('Error loading end card data:', error)
  }
  // Default message fallback
  return 'Passez une bonne<br>rentrée !'
})


const textColor = computed(() => {
  try {
    const savedEndCard = localStorage.getItem('titleCard-endcard')
    if (savedEndCard) {
      const endCardData = JSON.parse(savedEndCard)
      return endCardData.textColor
    }
  } catch (error) {
    console.error('Error loading end card colors:', error)
  }
  // Default fallback
  return '#FFFFFF'
})

// Load background color from localStorage
const backgroundColor = computed(() => {
  try {
    const savedEndCard = localStorage.getItem('titleCard-endcard')
    if (savedEndCard) {
      const endCardData = JSON.parse(savedEndCard)
      return endCardData.backgroundColor
    }
  } catch (error) {
    console.error('Error loading end card colors:', error)
  }
  // Default color fallback
  return '#000000'
})

onMounted(() => {
  setTimeout(() => {
    isVisible.value = true
  }, 100)
})

window.addEventListener('load', () => {
  const element = document.getElementById('fadeInElement')
  if (element) {
    element.classList.add('opacity-100')
  }
})
</script>