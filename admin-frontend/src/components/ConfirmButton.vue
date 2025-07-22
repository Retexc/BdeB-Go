<template>
  <button
    type="button"
    @click="pickFile"
    class="inline-flex items-center px-4 py-2 bg-yellow-400 text-black rounded-lg hover:bg-yellow-500 font-bold"
  >
    <!-- named slot for an icon; falls back to nothing -->
    <slot name="icon"></slot>
    <!-- default slot for your label -->
    <slot>Confirmer</slot>
  </button>
</template>
