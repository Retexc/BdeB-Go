<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";
import Bdeblogo from '../assets/icons/bdeb.svg'

const currentTime = ref('');
const weather = ref({
  icon: '',
  text: '',
  temp: ''
});

let timeInterval = null;
let weatherInterval = null;

const updateTime = () => {
  const now = new Date();
  
  currentTime.value = now.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  });
};

const fetchWeatherData = async () => {
  try {
    const response = await fetch('/api/data');
    const data = await response.json();
    
    // Update weather data from API response
    if (data.weather) {
      weather.value = {
        icon: data.weather.icon || '',
        text: data.weather.text || '',
        temp: data.weather.temp || ''
      };
    }
  } catch (error) {
    console.error('Error fetching weather data:', error);
  }
};

onMounted(() => {
  updateTime();
  timeInterval = setInterval(updateTime, 1000);
  
  fetchWeatherData();
  weatherInterval = setInterval(fetchWeatherData, 30000); // Update every 30 seconds
});

onBeforeUnmount(() => {
  if (timeInterval) {
    clearInterval(timeInterval);
  }
  if (weatherInterval) {
    clearInterval(weatherInterval);
  }
});
</script>

<template>
  <div class="flex flex-row justify-between items-center bg-black p-2">
    <img src="../assets/icons/bdeb.svg" alt="Bdeblogo" class="w-52 h-12 ml-6"></img>
    
    <div class="flex flex-row items-center gap-4 mr-6">
      <!-- Weather section -->
      <div v-if="weather.icon" class="flex flex-row items-center gap-2">
        <img :src="weather.icon" :alt="weather.text" class="w-8 h-8" />
        <span class="text-white font-bold text-xl">
          {{ weather.temp }}°C {{ weather.text }}
        </span>
      </div>
      
      <!-- Clock -->
      <h1 class="text-white font-bold text-3xl">{{ currentTime }}</h1>
    </div>
  </div>
</template>

<style scoped>
</style>