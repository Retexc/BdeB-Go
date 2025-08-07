<script setup>
import { ref } from "vue";
import greenLine from '../assets/icons/green-line.svg'
import yellowLine from '../assets/icons/yellow-line.svg'
import blueLine from '../assets/icons/blue-line.svg'
import orangeLine from '../assets/icons/orange-line.svg'
</script>

<template>
  <div class="flex flex-row justify-between items-center ml-8 mr-8 border-b border-gray-300">
    <!-- fixed-size square -->

    <div class="flex flex-row items-center gap-8">
<img :src="greenLine" alt="Green line" class="w-18 h-18 mt-4"></img>

    <div class="flex flex-col text-white font-bold ">
      <div class="flex flex-row items-center gap-2">

       <h1 class="text-2xl">Ligne 1</h1>       
      </div>

      <h1 class="text-xl">Verte</h1>
    </div>

    </div>

    <div class="flex flex-row items-center gap-8">
    <h1 class="text-green-400 font-bold text-2xl">Service normal du métro</h1>

    </div>

    
  </div>
</template>

<style scoped>
/* All styling via Tailwind utilities */
</style>
