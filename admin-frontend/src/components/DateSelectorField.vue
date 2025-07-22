<template>
<div class="space-y-2">
    <label class="block text-lg font-bold text-white mb-1">
        Date de début
    </label>
    <input
        v-model="date"
        type="date"
        class="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none"
    />
        <label class="block text-lg font-bold text-white mb-1">
        Date de fin
    </label>
    <input
        v-model="date"
        type="date"
        class="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none"
    />
</div>    
</template>