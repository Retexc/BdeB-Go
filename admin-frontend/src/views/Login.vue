<script setup>
import { ref } from "vue"
import { motion } from "motion-v"
import logo       from '../assets/images/logo.png'
import bgImg from '../assets/images/268.jpg'

const username = ref("")
const password = ref("")
const remember = ref(false)
const loading = ref(false)
const error = ref(null)

function onSubmit() {
  loading.value = true
  error.value = null

  // ←– replace this with your real API call…
  setTimeout(() => {
    loading.value = false
    // e.g. this.$router.push("/home") on success
  }, 1000)
}
</script>

<style scoped>
/* nothing here—everything is in utility classes */
</style>

<template>
<div class="min-h-screen bg-center bg-cover bg-no-repeat"
     :style="{ backgroundImage: `url(${bgImg})` }">
     <div class="flex items-center justify-start h-screen">
        <div
          class="relative z-10 bg-[#080913] w-2/5 h-full p-8 overflow-hidden"
     ></div>
    </div>
  </div>
</template>
