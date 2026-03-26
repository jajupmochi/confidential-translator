<script setup lang="ts">
import { useOllamaStore } from "@/stores/ollama";

const ollamaStore = useOllamaStore();
</script>

<template>
  <div
    class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-100 dark:bg-slate-800 text-sm font-medium border border-slate-200 dark:border-slate-700"
  >
    <div class="relative flex h-3 w-3 items-center justify-center">
      <!-- Ping effect only when healthy -->
      <span
        v-if="ollamaStore.isConnected"
        class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"
      ></span>
      <span
        class="relative inline-flex rounded-full h-2.5 w-2.5"
        :class="ollamaStore.isConnected ? 'bg-emerald-500' : 'bg-rose-500'"
      ></span>
    </div>
    <span class="text-slate-600 dark:text-slate-300">Ollama</span>
  </div>
</template>
