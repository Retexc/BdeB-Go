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
  

  let cleanText = props.line.status.replace(/<[^>]*>/g, '');

  
  return cleanText;
});

// Determine status color based on content and is_normal flag
const statusColor = computed(() => {
  if (props.line.statusColor) {
    return props.line.statusColor;
  }
  
  if (props.line.is_normal === false) {
    return "text-red-400";
  }
  
  if (props.line.is_normal === true) {
    return "text-black";
  }
  
  const statusLower = (props.line.status || '').toLowerCase();
  if (statusLower.includes('service normal') || statusLower.includes('normal service')) {
    return "text-black ";
  }
  
  // Default to red for any other status
  return "text-red-400";
});
</script>

<template>
  <div class="flex flex-row justify-between items-center ml-8 mr-8 border-b border-gray-300  px-4">
    <div class="flex flex-row items-center gap-8">
      <img :src="lineIcon" :alt="`${props.line.color} line`" class="w-18 h-18 mt-4"></img>

      <div class="flex flex-col text-black font-bold bg-[#F8F8F8] opacity-90 rounded-xl w-100 px-4 py-1 ">
        <div class="flex flex-row items-center gap-2">
          <h1 class="text-2xl">{{ props.line.name }}</h1>       
        </div>
        <h1 class="text-xl">{{ props.line.color }}</h1>
      </div>
    </div>

    <div class="flex flex-row items-center gap-8">
      <div class="flex flex-col items-end">
        <h1 :class="`font-bold text-xl bg-green-500 rounded-xl text-black pr-4 pl-4 py-1.5`">
          {{ cleanStatus }}
        </h1>
        <div v-if="!props.line.is_normal" class="flex items-center gap-4 mt-1">
          <div class="w-4 h-4 bg-red-400 rounded-full animate-pulse"></div>
          <span class="font-bold text-xl bg-red-400 rounded-xl text-black pr-4 pl-4 py-1.5">Service perturbé</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
</style>