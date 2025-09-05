<script setup>
import { ref, computed } from "vue";

const props = defineProps({
  train: {
    type: Object,
    required: true,
  },
});

// Quebec holidays
const quebecHolidays = computed(() => {
  const year = new Date().getFullYear();
  const holidays = [];

  // Fixed holidays
  holidays.push(`${year}-01-01`); // Jour de l'An
  holidays.push(`${year}-01-02`); // Lendemain du jour de l'An
  holidays.push(`${year}-06-24`); // Fête nationale du Québec
  holidays.push(`${year}-07-01`); // Fête du Canada
  holidays.push(`${year}-09-01`); // Fête du Travail (first Monday in September)
  holidays.push(`${year}-12-25`); // Jour de Noël
  holidays.push(`${year}-12-26`); // Lendemain de Noël

  // Calculate Easter-based holidays (Vendredi saint)
  const easter = calculateEaster(year);
  const goodFriday = new Date(easter);
  goodFriday.setDate(easter.getDate() - 2);
  holidays.push(goodFriday.toISOString().split("T")[0]);

  // Victoria Day (Journée nationale des patriotes) - Monday before May 25
  const victoriaDay = calculateVictoriaDay(year);
  holidays.push(victoriaDay.toISOString().split("T")[0]);

  // Thanksgiving (Action de grâces) - second Monday in October
  const thanksgiving = calculateThanksgiving(year);
  holidays.push(thanksgiving.toISOString().split("T")[0]);

  return holidays;
});

// Helper function to calculate Easter
function calculateEaster(year) {
  const f = Math.floor;
  const G = year % 19;
  const C = f(year / 100);
  const H = (C - f(C / 4) - f((8 * C + 13) / 25) + 19 * G + 15) % 30;
  const I = H - f(H / 28) * (1 - f(29 / (H + 1)) * f((21 - G) / 11));
  const J = (year + f(year / 4) + I + 2 - C + f(C / 4)) % 7;
  const L = I - J;
  const month = 3 + f((L + 40) / 44);
  const day = L + 28 - 31 * f(month / 4);
  return new Date(year, month - 1, day);
}

// Helper function to calculate Victoria Day (Monday before May 25)
function calculateVictoriaDay(year) {
  const may25 = new Date(year, 4, 25); // May 25
  const dayOfWeek = may25.getDay();
  const mondayBefore = new Date(may25);
  mondayBefore.setDate(25 - ((dayOfWeek + 6) % 7));
  return mondayBefore;
}

// Helper function to calculate Thanksgiving (second Monday in October)
function calculateThanksgiving(year) {
  const oct1 = new Date(year, 9, 1); // October 1
  const firstMonday = new Date(oct1);
  firstMonday.setDate(1 + ((7 - oct1.getDay() + 1) % 7));
  const secondMonday = new Date(firstMonday);
  secondMonday.setDate(firstMonday.getDate() + 7);
  return secondMonday;
}

// Check if today is a weekend or holiday
const isNoServiceDay = computed(() => {
  const today = new Date();
  const dayOfWeek = today.getDay();
  const todayString = today.toISOString().split("T")[0];

  // Check if weekend (Saturday = 6, Sunday = 0)
  const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;

  // Check if holiday
  const isHoliday = quebecHolidays.value.includes(todayString);

  return isWeekend || isHoliday;
});

const displayTime = computed(() => {
  if (isNoServiceDay.value) {
    return "Aucun service aujourd'hui";
  }
  return props.train.display_time;
});

const direction = computed(() => props.train.direction);
const location = computed(() => props.train.location);
const routeId = computed(() => {
  if (props.train.route_id === "4") return "SJ";
  if (props.train.route_id === "6") return "MA";
  return props.train.route_id;
});
const atStop = computed(() => props.train.at_stop);
const wheelchair = computed(() => props.train.wheelchair_accessible);
const bikesAllowed = computed(() => props.train.bikes_allowed);

const occupancyConfig = {
  NO_DATA: {
    count: 4,
    filledCount: 0,
    bgColor: "bg-gray-400",
    iconColor: "fill-gray-600",
  },
  UNKNOWN: {
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
  () => occupancyConfig[props.train.occupancy] || occupancyConfig.NO_DATA
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
    class="flex flex-row justify-between items-center ml-8 mr-8 py-6 border-b border-gray-300"
  >
    <div class="flex flex-row items-center gap-8">
      <span
        class="inline-flex items-center justify-center w-18 h-12 text-2xl font-black rounded-lg"
        :class="
          routeId === 'MA'
            ? 'bg-pink-500 text-black'
            : 'bg-amber-300 text-black'
        "
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
        <div
          class="flex flex-box text-black font-bold text-xl bg-white rounded-xl px-3 py-1"
        >
          {{ displayTime }}
          <svg
            v-if="!isNoServiceDay && displayTime.includes('min')"
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
        
        <!-- X icon for NO_DATA and Unknown -->
        <svg
          v-if="props.train.occupancy === 'NO_DATA' || props.train.occupancy === 'UNKNOWN'"
          width="22"
          height="22"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
          :class="currentOccupancy.iconColor"
        >
          <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
        </svg>
      </div>

      <img
        :src="wheelchairIcon"
        alt="Wheelchair"
        class="w-8 h-8"
        :class="
          props.train.wheelchair_accessible
            ? 'opacity-100 filter-none'
            : 'opacity-30 filter grayscale'
        "
      />
      <img
        :src="bikeIconUrl"
        alt="Bikes"
        class="w-8 h-8"
        :class="
          props.train.bikes_allowed
            ? 'opacity-100 filter-none'
            : 'opacity-30 filter grayscale'
        "
      />

      <img
        :src="trainIcon"
        alt="Train"
        class="w-8 h-8"
        :class="[
          props.train.at_stop
            ? 'opacity-100 filter-none animate-pulse [animation-duration: 1s]'
            : 'opacity-0',
        ]"
      />
    </div>
  </div>
</template>

<style scoped></style>
