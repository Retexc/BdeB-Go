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
      <h1 :class="`font-bold text-2xl ${props.line.statusColor}`">
        {{ props.line.status }}
      </h1>
    </div>
  </div>
</template>

<style scoped>
/* All styling via Tailwind utilities */
</style>