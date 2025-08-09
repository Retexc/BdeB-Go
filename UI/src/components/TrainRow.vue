<script setup>
import { ref, computed } from "vue";
import bikeIcon from "../assets/icons/bike.svg";
import noDataIcon from "../assets/icons/NO_DATA.svg";
import manySeatsIcon from "../assets/icons/MANY_SEATS_AVAILABLE.svg";
import fewSeatsIcon from "../assets/icons/FEW_SEATS_AVAILABLE.svg";
import standingRoomOnlyIcon from "../assets/icons/STANDING_ROOM_ONLY.svg";
import fullIcon from "../assets/icons/FULL.svg";

const props = defineProps({
  train: {
    type: Object,
    required: true,
  },
});

// Use the correct API data structure for trains
const displayTime = computed(() => props.train.display_time); // "12 min" or "07:12 AM"
const direction = computed(() => props.train.direction); // "Saint-Jérôme", "Mascouche", etc
const location = computed(() => props.train.location); // "Gare Bois-de-Boulogne"
const routeId = computed(() => {
  // Convert route_id to display format: "4" -> "SJ", "6" -> "MA"
  if (props.train.route_id === "4") return "SJ";
  if (props.train.route_id === "6") return "MA";
  return props.train.route_id;
});
const atStop = computed(() => props.train.at_stop); 
const wheelchair = computed(() => props.train.wheelchair_accessible); 
const bikesAllowed = computed(() => props.train.bikes_allowed); 

const occupancyIcons = {
  NO_DATA: noDataIcon,
  UNKNOWN: noDataIcon, // Handle "UNKNOWN" from API
  Unknown: noDataIcon,
  MANY_SEATS_AVAILABLE: manySeatsIcon,
  FEW_SEATS_AVAILABLE: fewSeatsIcon,
  STANDING_ROOM_ONLY: standingRoomOnlyIcon,
  FULL: fullIcon,
};

const iconSrc = computed(
  () => occupancyIcons[props.train.occupancy] || occupancyIcons.NO_DATA
);
const wheelchairIcon = new URL(
  "../assets/icons/wheelchair.svg",
  import.meta.url
).href;

const bikeIconUrl = new URL("../assets/icons/bike.svg", import.meta.url).href;
const trainIcon = new URL("../assets/icons/train.svg", import.meta.url).href;
</script>

<template>
  <div
    class="flex flex-row justify-between items-center ml-8 mr-8 border-b border-gray-300"
  >
    <div class="flex flex-row items-center gap-8">
      <span
        class="inline-flex items-center justify-center w-18 h-12 text-2xl font-black rounded-lg"
        :class="routeId === 'MA' ? 'bg-pink-500 text-black' : 'bg-amber-300 text-black'"
      >
        {{ routeId }}
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
          <span class="font-bold text-2xl">{{ props.train.direction }}</span>
        </div>

        <div class="text-xl">{{ props.train.location }}</div>
      </div>
    </div>

    <div class="flex flex-row items-center gap-8">
      <div class="flex flex-row gap-1">
        <span class="text-green-400 font-bold text-xl mt-2"
          >{{ displayTime }}</span
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
          v-if="displayTime.includes('min')"
        >
          <path d="M4 11a9 9 0 0 1 9 9"></path>
          <path d="M4 4a16 16 0 0 1 16 16"></path>
          <circle cx="5" cy="19" r="1"></circle>
        </svg>
      </div>

      <img :src="iconSrc" alt="Occupancy" class="w-24 h-24" />
      
      <div class="flex flex-col gap-1">
        <img
          :src="wheelchairIcon"
          alt="Wheelchair"
          class="w-6 h-6"
          :class="
            props.train.wheelchair_accessible
              ? 'opacity-100 filter-none'
              : 'opacity-30 filter grayscale'
          "
        />
        <img
          :src="bikeIconUrl"
          alt="Bikes"
          class="w-6 h-6"
          :class="
            props.train.bikes_allowed
              ? 'opacity-100 filter-none'
              : 'opacity-30 filter grayscale'
          "
        />
      </div>
      <img
        :src="trainIcon"
        alt="Train"
        class="w-6 h-6"
        :class="[
          props.train.at_stop
            ? 'opacity-100 filter-none animate-pulse [animation-duration: 1s]'
            : 'opacity-0',
        ]"
      />
    </div>
  </div>
</template>

<style scoped>
</style>