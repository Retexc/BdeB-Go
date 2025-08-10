<script setup>
import Home from "./views/Console.vue";
import Background from "./views/Background.vue";
import Settings from "./views/Settings.vue";
import Sidebar from "./components/SideBar.vue";
import './style.css'
</script>

<template>
  <div id="app" class="flex min-h-screen bg-[#0f0f0f]">
    <!-- only render sidebar if NOT on /login -->
    <Sidebar v-if="$route.path !== '/display' && $route.path !== '/loading'" />

    <!-- render current page -->
    <div class="flex-1 overflow-auto"><router-view /></div>
  </div>
</template>

<style>
/* optional global styles */
</style>
