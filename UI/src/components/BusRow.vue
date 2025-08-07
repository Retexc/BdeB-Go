<script setup>
import { ref, computed } from "vue";
import bikeIcon from "../assets/icons/bike.svg";
import noDataIcon from "../assets/icons/NO_DATA.svg";
import manySeatsIcon from "../assets/icons/MANY_SEATS_AVAILABLE.svg";
import fewSeatsIcon from "../assets/icons/FEW_SEATS_AVAILABLE.svg";
import standingRoomOnlyIcon from "../assets/icons/STANDING_ROOM_ONLY.svg";
import fullIcon from "../assets/icons/FULL.svg";

// 1) Only *one* defineProps call!
const props = defineProps({
  bus: {
    type: Object,
    required: true,
  },
});

// 2) Compute minutes until arrival
const minutes = computed(() => props.bus.arrival_time); // the number of minutes
const direction = computed(() => props.bus.direction); // "Est" / "Ouest"
const location = computed(() => props.bus.location); // stop name
const routeId = computed(() => props.bus.route_id); // "171", "180", etc
const atStop = computed(() => props.bus.at_stop); // boolean
const wheelchair = computed(() => props.bus.wheelchair_accessible); // boolean

const occupancyIcons = {
  NO_DATA: noDataIcon,
  MANY_SEATS_AVAILABLE: manySeatsIcon,
  FEW_SEATS_AVAILABLE: fewSeatsIcon,
  STANDING_ROOM_ONLY: standingRoomOnlyIcon,
  FULL: fullIcon,
};

const iconSrc = computed(
  () => occupancyIcons[props.bus.occupancy] || occupancyIcons.NO_DATA
);
const wheelchairIcon = new URL(
  "../assets/icons/wheelchair.svg",
  import.meta.url
).href;

const busIcon = new URL("../assets/icons/bus.svg", import.meta.url).href;
const trainIcon = new URL("../assets/icons/train.svg", import.meta.url).href;
</script>

<template>
  <div
    class="flex flex-row justify-between items-center ml-8 mr-8 border-b border-gray-300"
  >
    <!-- fixed-size square -->

    <div class="flex flex-row items-center gap-8">
      <span
        class="inline-flex items-center justify-center w-18 h-12 bg-pink-500 text-white text-2xl font-black rounded-lg"
        :class="routeId === '171' ? 'bg-pink-500' : 'bg-blue-600'"
      >
        {{ props.bus.route_id }}
      </span>

      <div class="flex flex-col text-white font-bold">
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
          <span class="font-bold text-2xl">{{ props.bus.direction }}</span>
        </div>

        <div class="text-xl">{{ props.bus.location }}</div>
      </div>
    </div>

    <div class="flex flex-row items-center gap-8">
      <div class="flex flex-row gap-1">
      <span class="text-green-400 font-bold text-xl mt-2">{{ minutes }} min</span
      ><svg
        xmlns="http://www.w3.org/2000/svg"
        width="18"
        height="18"
        viewBox="0 0 24 24"
        fill="none"
        stroke="#05df55"
        stroke-width="3"
        stroke-linecap="round"
        stroke-linejoin="round"
        class="animate-pulse [animation-duration: 1s]"
      >
        <path d="M4 11a9 9 0 0 1 9 9"></path>
        <path d="M4 4a16 16 0 0 1 16 16"></path>
        <circle cx="5" cy="19" r="1"></circle>
      </svg>        
      </div>

      <img :src="iconSrc" alt="No data" class="w-24 h-24" />
      <!-- wheelchair icon -->
      <img
        :src="wheelchairIcon"
        alt="Fauteuil roulant"
        class="w-6 h-6"
        :class="
          props.bus.wheelchair_accessible
            ? 'opacity-100 filter-none'
            : 'opacity-30 filter grayscale'
        "
      />

      <!-- bus icon -->
      <img
        :src="busIcon"
        alt="Bus"
        class="w-6 h-6"
        :class="[
          props.bus.at_stop
            ? 'opacity-100 filter-none animate-pulse [animation-duration: 1s]'
            : 'opacity-0',
        ]"
      />
    </div>
  </div>
</template>

<style scoped>
/* All styling via Tailwind utilities */
</style>
