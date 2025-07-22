<template>
    <div class="grid grid-cols-4 gap-4">
    <img
      v-for="(img, i) in images"
      :key="i"
      :src="img"
      class="w-48 rounded-lg shadow-lg"
      alt="Preview"
    />        
    </div>
</template>
<script setup>
const images = [
  './assets/images/background.png',
  './assets/images/background.png',
  './assets/images/background.png',
  './assets/images/background.png',
]
</script>