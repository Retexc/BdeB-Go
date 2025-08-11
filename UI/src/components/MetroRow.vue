<script setup>
import { ref, computed } from "vue";
import greenLine from '../assets/icons/green-line.svg'
import yellowLine from '../assets/icons/yellow-line.svg'
import blueLine from '../assets/icons/blue-line.svg'
import orangeLine from '../assets/icons/orange-line.svg'

const props = defineProps({
  line: {
    type: Object,
    required: true,
  }
});

const iconMap = {
  'green-line': greenLine,
  'yellow-line': yellowLine,
  'blue-line': blueLine,
  'orange-line': orangeLine
};

const lineIcon = computed(() => iconMap[props.line.icon] || greenLine);

const cleanStatus = computed(() => {
  if (!props.line.status) return "Information non disponible";
  
  // Remove HTML tags using regex
  let cleanText = props.line.status.replace(/<[^>]*>/g, '');
  
  // Decode HTML entities
  const tempDiv = document.createElement('div');
  tempDiv.innerHTML = cleanText;
  cleanText = tempDiv.textContent || tempDiv.innerText || '';
  
  // Limit length for display (optional)
  if (cleanText.length > 80) {
    cleanText = cleanText.substring(0, 77) + '...';
  }
  
  return cleanText;
});

// Determine status color based on content and is_normal flag
const statusColor = computed(() => {
  // First check if we have an explicit statusColor from API
  if (props.line.statusColor) {
    return props.line.statusColor;
  }
  
  // Fallback logic based on is_normal flag or status text
  if (props.line.is_normal === false) {
    return "text-red-400";
  }
  
  if (props.line.is_normal === true) {
    return "text-green-400";
  }
  
  // Final fallback: check status text content
  const statusLower = (props.line.status || '').toLowerCase();
  if (statusLower.includes('service normal') || statusLower.includes('normal service')) {
    return "text-green-400";
  }
  
  // Default to red for any other status
  return "text-red-400";
});
</script>

<template>
  <div class="flex flex-row justify-between items-center ml-8 mr-8 border-b border-gray-300">
    <div class="flex flex-row items-center gap-8">
      <img :src="lineIcon" :alt="`${props.line.color} line`" class="w-18 h-18 mt-4"></img>

      <div class="flex flex-col text-white font-bold">
        <div class="flex flex-row items-center gap-2">
          <h1 class="text-2xl">{{ props.line.name }}</h1>       
        </div>
        <h1 class="text-xl">{{ props.line.color }}</h1>
      </div>
    </div>

    <div class="flex flex-row items-center gap-8">
      <div class="flex flex-col items-end">
        <h1 :class="`font-bold text-xl ${statusColor}`">
          {{ cleanStatus }}
        </h1>
        <div v-if="!props.line.is_normal" class="flex items-center gap-1 mt-1">
          <div class="w-2 h-2 bg-red-400 rounded-full animate-pulse"></div>
          <span class="text-red-400 text-sm">Service perturbé</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
</style>