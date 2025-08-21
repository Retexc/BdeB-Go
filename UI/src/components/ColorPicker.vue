<template>
  <div class="text-white font-sans w-full">
    <!-- Title -->
    <h3 class="text-lg font-semibold text-white mb-4">{{ title }}</h3>
    
    <!-- Color picker container -->
    <div class="flex items-center gap-3">
      <!-- Hex input field -->
      <div class="flex-1">
        <input 
          v-model="hexValue"
          @input="updateFromHex"
          type="text"
          placeholder="#FFFFFF"
          class="w-full bg-gray-800 border border-gray-600 rounded-md px-3 py-2 text-white text-sm transition-all duration-200 focus:outline-none focus:border-yellow-400 focus:bg-gray-700 placeholder:text-gray-400"
        />
      </div>
      
      <!-- Color preview square -->
      <div class="relative">
        <div 
          class="w-10 h-10 rounded border border-gray-600 cursor-pointer transition-all duration-200 hover:border-gray-400"
          :style="{ backgroundColor: colorValue }"
          @click="openColorPicker"
        ></div>
        
        <!-- Hidden native color input -->
        <input 
          ref="colorInput"
          v-model="colorValue"
          @input="updateFromPicker"
          type="color"
          class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />
      </div>
    </div>
    
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

// Props
const props = defineProps({
  title: {
    type: String,
    default: 'Couleur texte principal'
  },
  modelValue: {
    type: String,
    default: '#FFFFFF'
  },
  showPresets: {
    type: Boolean,
    default: true
  },
  presetColors: {
    type: Array,
    default: () => [
      '#FFFFFF', '#000000', '#FF0000', '#00FF00', '#0000FF',
      '#FFFF00', '#FF00FF', '#00FFFF', '#FFA500', '#800080',
      '#FFC0CB', '#A52A2A', '#808080', '#FFD700', '#90EE90'
    ]
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'change'])

// Reactive data
const colorInput = ref(null)
const colorValue = ref(props.modelValue)
const hexValue = ref(props.modelValue)

// Methods
const updateFromHex = () => {
  let hex = hexValue.value.trim()
  
  // Add # if missing
  if (hex && !hex.startsWith('#')) {
    hex = '#' + hex
    hexValue.value = hex
  }
  
  // Validate hex format
  if (isValidHex(hex)) {
    colorValue.value = hex.toUpperCase()
    emit('update:modelValue', colorValue.value)
    emit('change', colorValue.value)
  }
}

const updateFromPicker = () => {
  hexValue.value = colorValue.value.toUpperCase()
  emit('update:modelValue', colorValue.value)
  emit('change', colorValue.value)
}

const openColorPicker = () => {
  colorInput.value?.click()
}

const selectPreset = (color) => {
  colorValue.value = color
  hexValue.value = color
  emit('update:modelValue', color)
  emit('change', color)
}

const isValidHex = (hex) => {
  return /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/.test(hex)
}

// Watch for prop changes
watch(() => props.modelValue, (newValue) => {
  colorValue.value = newValue
  hexValue.value = newValue
})

// Expose methods for parent component
defineExpose({
  selectPreset,
  colorValue: computed(() => colorValue.value)
})
</script>