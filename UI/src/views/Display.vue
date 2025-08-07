<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from "vue";
import { motion } from "motion-v";
import BusRow from "../components/BusRow.vue";
import TrainRow from "../components/TrainRow.vue";
import MetroRow from "../components/MetroRow.vue";
import Header from "../components/Header.vue";
import STMLogo from "../assets/icons/STM.png";
import ExoLogo from "../assets/icons/exo_white.png";

const buses = ref([])

async function fetchData() {
  try {
    const res = await fetch('/api/data')
    const json = await res.json()
    buses.value = json.buses.filter(b =>
      ['171','180','164'].includes(b.route_id)
    )
  } catch (err) {
    console.error(err)
  }
}

onMounted(() => {
  fetchData()
  setInterval(fetchData, 30_000)
})
</script>

<template>
<Header />
<img :src="STMLogo" alt="STM logo" class="w-22 h-auto mt-4 ml-6"></img>
  <div class="flex flex-col">
    
    <template v-if="buses.length">
      <BusRow
        v-for="bus in buses"
        :key="bus.trip_id"
        :bus="bus"
      />
    </template>
    <p v-if="buses.length === 0" class="text-gray-500">
      Aucun autobus à afficher…
    </p>
  </div>

</template>

<style scoped>
/* ensure full‐height so motion has space */
:host {
  display: block;
  height: 100%;
}
</style>
