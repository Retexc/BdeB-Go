<script setup>
import { ref } from "vue";
import noDataIcon             from '../assets/icons/NO_DATA.svg'
import manySeatsIcon          from '../assets/icons/MANY_SEATS_AVAILABLE.svg'
import fewSeatsIcon           from '../assets/icons/FEW_SEATS_AVAILABLE.svg'
import standingRoomOnlyIcon   from '../assets/icons/STANDING_ROOM_ONLY.svg'
import fullIcon               from '../assets/icons/FULL.svg'
import bikeIcon               from '../assets/icons/bike.svg'
import wheelchairIcon         from '../assets/icons/wheelchair.svg'
import busIcon                from '../assets/icons/bus.svg'
import trainIcon              from '../assets/icons/train.svg'
</script>

<template>
  <div class="flex flex-row justify-between items-center ml-8 mr-8 border-b border-gray-300">
    <!-- fixed-size square -->

    <div class="flex flex-row items-center gap-8">
    <span
      class="inline-flex items-center justify-center w-18 h-12 bg-amber-300 text-black text-2xl font-black rounded-lg"
    >
      SJ
    </span>

    <div class="flex flex-col text-white font-bold ">
      <div class="flex flex-row items-center gap-2">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="#ffffff"
          stroke-width="2.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <circle cx="12" cy="12" r="10" />
          <path d="M12 8l4 4-4 4M8 12h7" />
        </svg>
       <h1 class="text-2xl">Saint-Jérôme</h1>       
      </div>

      <h1 class="text-xl">Gare de Bois-de-Boulogne</h1>
    </div>

    </div>

    <div class="flex flex-row items-center gap-8">
    <h1 class="text-green-400 font-bold text-2xl">0:00 AM</h1>
    <img :src="noDataIcon" alt="No data" class="w-24 h-24"></img>
        <img :src="wheelchairIcon" alt="No data" class="w-8 h-8"></img>
                <img :src="trainIcon" alt="No data" class="w-8 h-8"></img>
    </div>

    
  </div>
</template>

<style scoped>
/* All styling via Tailwind utilities */
</style>
