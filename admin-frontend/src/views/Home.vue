<template>
<div class="flex max-h-screen bg-[#0f0f0f]">
  <side-bar />

  <div class="flex-1 flex flex-col p-6 space-y-6 mt-18 ml-5">
    <div class="flex items-center justify-between w-full">
      <div class="space-y-1">
        <h2 class="text-4xl font-bold text-white">Console</h2>
        <p class="text-xl text-white">État : Inconnu</p>
      </div>
    <action-buttons/>
    </div>

    <div class="flex-1">
      <console-log/>
    </div>
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
