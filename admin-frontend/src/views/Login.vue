<script setup>
import { ref } from "vue";
import { motion } from "motion-v";
import logo from "../assets/images/logo.png";
import bgImg from "../assets/images/268.jpg";

const username = ref("");
const password = ref("");
const remember = ref(false);
const loading = ref(false);
const error = ref(null);

function onSubmit() {
  loading.value = true;
  error.value = null;

  // ←– replace this with your real API call…
  setTimeout(() => {
    loading.value = false;
    // e.g. this.$router.push("/home") on success
  }, 1000);
}
</script>

<style scoped>
/* nothing here—everything is in utility classes */
</style>

<template>
  <div
    class="min-h-screen bg-center bg-cover bg-no-repeat"
    :style="{ backgroundImage: `url(${bgImg})` }"
  >
    <div class="flex items-center justify-start h-screen">
      <!-- BLACK CARD -->
      <div class="bg-[#080913] w-2/5 h-full p-8 overflow-hidden flex flex-col">
        <!-- 1) Top-left BdeB logo zone -->
         <motion.div
          :initial="{ opacity: 0, y: 20, filter: 'blur(10px)' }"
          :animate="{
            opacity: 1,
            y: 0,
            filter: 'blur(0px)',
            transition: { duration: 1 },
          }"
        >
        <img
          src="../assets/icons/bdeb.svg"
          alt="BdeB Logo"
          class="w-48 h-24 self-start mt-2"
        />      
      </motion.div>

        <!-- 2) The rest of the screen, flexed to center -->
        <motion.div
          :initial="{ opacity: 0, y: 20, filter: 'blur(10px)' }"
          :animate="{
            opacity: 1,
            y: 0,
            filter: 'blur(0px)',
            transition: { delay: 0.5, duration: 1 },
          }"
          class="flex py-32 flex-col items-center justify-center space-y-6 w-full text-center"
        >
          <img
            src="../assets/icons/Go_logo.png"
            alt="Go Logo"
            class="w-24 h-24"
          />
          <div class="space-y-2">
          <h1 class="text-4xl text-white font-bold">Bonjour</h1>
          <p class="text-gray-300">Entrer votre identifiant de connexion</p>            
          </div>


          <!-- Form -->
          <form
            @submit.prevent="onSubmit"
            class="w-full flex flex-col items-center space-y-6"
          >
            <input
              v-model="username"
              type="text"
              placeholder="Utilisateur"
              required
              class="w-3/4 p-3 bg-transparent border-2 border-[#535353] rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#ffcf25]"
            />

            <input
              v-model="password"
              type="password"
              placeholder="Mot de passe"
              required
              class="w-3/4 p-3 bg-transparent border-2 border-[#535353] rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#ffcf25]"
            />

            <button
              type="submit"
              class="w-3/4 py-3 bg-yellow-400 hover:bg-yellow-500 text-black font-bold rounded-xl"
            >
              Se connecter
            </button>
          </form>      
      </motion.div>

        <!-- 3) Bottom-right footer -->
      </div>
    </div>
  </div>
</template>
