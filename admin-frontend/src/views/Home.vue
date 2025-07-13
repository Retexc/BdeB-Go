<template>
<div class="flex max-h-screen">
  <side-bar />

  <div class="flex-1">
    <div class="flex justify-between py-3 px-6 bg-gray-900 border-b space-x-6"></div>
    <main>Console area</main>
  </div>
</div>
</template>

<script setup>
import ActionButtons from '../components/ActionButtons.vue'
import ConsoleLog from '../components/ConsoleLog.vue'
import SideBar from '../components/SideBar.vue'


function goToTableau() {
  // e.g. this.$router.push('/tableau')
}

function startProcess() {
  // your start logic...
}
</script>

<style scoped>
.home-page {
  padding: 2rem;
  text-align: center;
}
</style>
