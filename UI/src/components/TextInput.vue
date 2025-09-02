<template>
  <div class="text-white font-sans w-full">
    <h3 class="text-lg font-semibold text-white mb-4">{{ title }}</h3>
    <div class="flex items-center gap-3">
      <div class="flex-1">
        <input
          type="number"
          :value="modelValue"
          @input="$emit('update:modelValue', Number($event.target.value))"
          placeholder="45 secondes"
          class="w-full bg-gray-800 border border-gray-600 rounded-md px-3 py-2 text-white text-sm transition-all duration-200 focus:outline-none focus:border-blue-400 focus:bg-gray-700 placeholder:text-gray-400"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  title: {
    type: String,
    default: "",
  },
  modelValue: {
    type: [String, Number],
    default: ""
  }
});

const emit = defineEmits(['update:modelValue']);
</script>