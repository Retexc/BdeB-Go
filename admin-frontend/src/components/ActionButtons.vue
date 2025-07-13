<!-- src/components/ActionButtons.vue -->
<template>
  <div class="flex space-x-2">
    <!-- “Accéder au tableau” secondary button -->
    <button
      @click="$emit('open-tableau')"
      class="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-400"
    >
      Accéder au tableau
    </button>

    <!-- “Démarrer” primary button -->
    <button
      @click="$emit('start')"
      class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-400"
    >
      Démarrer
    </button>
  </div>
</template>

<script setup>
// No setup code needed unless you want props, etc.
// We emit two events: 'open-tableau' and 'start'.
</script>
