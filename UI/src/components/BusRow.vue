<script setup>
import { ref, computed } from "vue";

const props = defineProps({
  bus: {
    type: Object,
    required: true,
  },
});

// Handle both number (minutes) and string (time) formats
const displayTime = computed(() => {
  const arrivalTime = props.bus.arrival_time;
  if (typeof arrivalTime === "number") {
    return `${Math.round(arrivalTime)} min`;
  }
  return arrivalTime; // Already a formatted time string like "05:39 AM"
});

// Only show pulse animation for minute-based times
const showPulse = computed(() => {
  return typeof props.bus.arrival_time === "number";
});

const direction = computed(() => props.bus.direction); // "Est" / "Ouest"
const location = computed(() => props.bus.location); // stop name
const routeId = computed(() => props.bus.route_id); // "171", "180", etc
const atStop = computed(() => props.bus.at_stop); // boolean
const wheelchair = computed(() => props.bus.wheelchair_accessible); // boolean
const delay = computed(() => props.bus.delayed_text);

const occupancyConfig = {
  NO_DATA: {
    count: 4,
    filledCount: 0,
    bgColor: "bg-gray-400",
    iconColor: "fill-gray-600",
  },
  Unknown: {
    count: 4,
    filledCount: 0,
    bgColor: "bg-gray-400",
    iconColor: "fill-gray-600",
  },
  MANY_SEATS_AVAILABLE: {
    count: 4,
    filledCount: 1,
    bgColor: "bg-green-400",
    iconColor: "fill-black",
  },
  FEW_SEATS_AVAILABLE: {
    count: 4,
    filledCount: 2,
    bgColor: "bg-green-400",
    iconColor: "fill-black",
  },
  STANDING_ROOM_ONLY: {
    count: 4,
    filledCount: 3,
    bgColor: "bg-orange-400",
    iconColor: "fill-black",
  },
  FULL: {
    count: 4,
    filledCount: 4,
    bgColor: "bg-red-500",
    iconColor: "fill-black",
  },
};

const currentOccupancy = computed(
  () => occupancyConfig[props.bus.occupancy] || occupancyConfig.NO_DATA
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
    class="flex flex-row justify-between items-center ml-8 mr-8 py-6 border-b border-gray-300"
  >
    <div class="flex flex-row items-center gap-8">
      <span
        class="inline-flex items-center justify-center w-22 h-16 text-2xl font-black rounded-lg"
        :class="
          props.bus.route_id === '171'
            ? 'bg-[#FF5BB2] text-black'
            : 'bg-[#2151BA] text-white'
        "
      >
        {{ props.bus.route_id }}
      </span>

      <div
        class="flex flex-col text-black font-bold bg-[#F8F8F8] opacity-90 rounded-xl w-100 px-4 py-1"
      >
        <div class="flex flex-row items-center gap-2">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#000000"
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
      <div
        v-if="props.bus.delayed_text"
        class="flex flex-row items-center gap-8 bg-[#FF6063] text-black rounded-xl px-3 py-1 font-black"
      >
        {{ props.bus.delayed_text }}
      </div>
      <div class="flex flex-row gap-1">
        <div
          class="flex flex-box text-black font-bold text-xl bg-white rounded-xl px-3 py-1"
        >
          {{ displayTime }}
          <svg
            v-if="showPulse"
            class="animate-pulse [animation-duration: 1s]"
            width="16"
            height="16"
            viewBox="0 0 16 16"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M13.0909 15.6417C13.0909 13.9107 12.7654 12.2943 12.1144 10.7926C11.4634 9.29094 10.5757 7.97788 9.45132 6.85346C8.3269 5.72904 7.01384 4.84133 5.51215 4.19035C4.01046 3.53937 2.3941 3.21388 0.663086 3.21388V0.550781C2.76398 0.550781 4.72432 0.942849 6.5441 1.72698C8.36389 2.51112 9.96175 3.59116 11.3377 4.96709C12.7136 6.34303 13.7937 7.94089 14.5778 9.76068C15.3619 11.5805 15.754 13.5408 15.754 15.6417H13.0909ZM7.76469 15.6417C7.76469 14.6504 7.57975 13.7294 7.20988 12.8787C6.84 12.028 6.32958 11.2772 5.6786 10.6262C5.02761 9.9752 4.27677 9.46478 3.42605 9.0949C2.57534 8.72503 1.65435 8.54009 0.663086 8.54009V5.87699C2.02423 5.87699 3.2929 6.1322 4.4691 6.64263C5.64531 7.15306 6.67726 7.85212 7.56496 8.73982C8.45266 9.62752 9.15172 10.6595 9.66215 11.8357C10.1726 13.0119 10.4278 14.2806 10.4278 15.6417H7.76469Z"
              fill="black"
            />
          </svg>
        </div>
      </div>
      <div
        class="flex flex-row rounded-xl px-3 py-2 gap-1 w-32 justify-center"
        :class="currentOccupancy.bgColor"
      >
        <svg
          v-for="i in currentOccupancy.count"
          :key="i"
          width="22"
          height="22"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
          :class="[
            i <= currentOccupancy.filledCount
              ? currentOccupancy.iconColor
              : 'fill-black/30',
          ]"
        >
          <path
            d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"
          />
        </svg>

        <svg
          v-if="
            props.bus.occupancy === 'NO_DATA' ||
            props.bus.occupancy === 'Unknown'
          "
          width="22"
          height="22"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
          :class="currentOccupancy.iconColor"
        >
          <path
            d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"
          />
        </svg>
      </div>

      <!-- wheelchair icon -->
      <img
        :src="wheelchairIcon"
        alt="Fauteuil roulant"
        class="w-8 h-8"
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
        class="w-8 h-8"
        :class="[
          props.bus.at_stop
            ? 'opacity-100 filter-none animate-pulse [animation-duration: 1s]'
            : 'opacity-0',
        ]"
      />
    </div>
  </div>
</template>

<style scoped></style>
