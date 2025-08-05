<template>
  <div
    class="titlebar flex items-center justify-between h-9 px-3 bg-black text-white shadow-sm"
    style="-webkit-user-select: none;"
  >
    <!-- draggable area -->
    <div class="flex items-center gap-2" style="-webkit-app-region: drag;">
      <!-- Logo, adjust path if needed -->
      <img src="@/assets/Logo.png" alt="logo" class="h-5 w-auto" />
      <span class="text-sm font-semibold">BdeB GTFS</span>
    </div>

    <!-- window controls -->
    <div class="flex gap-1" style="-webkit-app-region: no-drag;">
      <button
        @click="minimize"
        aria-label="Minimize"
        class="flex items-center justify-center w-8 h-8 rounded hover:bg-zinc-800 transition"
      >
        <span class="text-lg leading-none">—</span>
      </button>
      <button
        @click="toggleMaximize"
        :aria-label="isMaximized ? 'Restore' : 'Maximize'"
        class="flex items-center justify-center w-8 h-8 rounded hover:bg-zinc-800 transition"
      >
        <span class="text-sm leading-none">
          {{ isMaximized ? "🗗" : "🗖" }}
        </span>
      </button>
      <button
        @click="close"
        aria-label="Close"
        class="flex items-center justify-center w-8 h-8 rounded hover:bg-red-600 transition"
      >
        ✕
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";

const isMaximized = ref(false);

function minimize() {
  window.electron?.minimize?.();
}
function toggleMaximize() {
  window.electron?.toggleMaximize?.();
}
function close() {
  window.electron?.close?.();
}

onMounted(async () => {
  if (window.electron) {
    try {
      isMaximized.value = await window.electron.isMaximized();
    } catch {}
    window.electron.onMaximize(() => {
      isMaximized.value = true;
    });
    window.electron.onUnmaximize(() => {
      isMaximized.value = false;
    });
  }
});
</script>

<style scoped>
.titlebar {
  /* subtle bottom border to separate from content if desired */
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}
/* ensure buttons don’t get draggable region */
button {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0;
}
</style>
