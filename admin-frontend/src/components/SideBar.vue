<template>
  <div class="flex min-h-screen">
    <div
      class="w-64 text-white bg-[#0A0A0A] border-r justify-items-start"
    >
      <div class="py-4 px-6">
        <a href="/">
          <img
            src="../assets/images/logo-menu.svg"
            alt="Bdeblogo"
            class="w-16 mb-2 mt-8"
          />
        </a>
      </div>
      <div class="mb-10">
        <a href="/admin/home" class="flex items-center font-semibold px-6 py-2.5 gap-2 hover:text-amber-300">
          <img src="../assets/images/home.svg" alt="Console" class="w-8" />
          Console
        </a>
      </div>

      <div class="mb-10">
        <a href="/admin/home" class="flex items-center font-semibold px-6 py-2.5 gap-2 hover:text-amber-300">
          <img src="../assets/images/background.svg" alt="Console" class="w-8" />
          Fond d’écran
        </a>
      </div>
      <div class="mb-10">
        <a href="/admin/home" class="flex items-center font-semibold px-6 py-2.5 gap-2 hover:text-amber-300">
          <img src="../assets/images/settings.svg" alt="Console" class="w-8" />
          Paramètres
        </a>
      </div>
      <div class="mb-10">
        <a href="/admin/home" class="flex items-center font-semibold px-6 py-2.5 gap-2 hover:text-red-600">
          <img src="../assets/icons/logout.svg" alt="Console" class="w-8" />
          Déconnexion
        </a>
      </div>
    </div>
  </div>
</template>
