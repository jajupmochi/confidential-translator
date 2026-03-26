<script setup lang="ts">
import { onMounted, onUnmounted } from "vue";
import ThemeToggle from "../common/ThemeToggle.vue";
import LanguageSelector from "../common/LanguageSelector.vue";
import StatusIndicator from "../common/StatusIndicator.vue";
import OllamaInstaller from "../common/OllamaInstaller.vue";
import AppSidebar from "./AppSidebar.vue";
import { useOllamaStore } from "@/stores/ollama";

const ollamaStore = useOllamaStore();

onMounted(() => {
  ollamaStore.startPolling();
});

onUnmounted(() => {
  ollamaStore.stopPolling();
});
</script>

<template>
  <div
    class="h-screen w-full flex overflow-hidden bg-slate-50 dark:bg-[#0B1120] relative"
  >
    <OllamaInstaller />
    <!-- Decorative background blobs for glassmorphism -->
    <div
      class="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none z-0"
    >
      <div
        class="absolute -top-[20%] -left-[10%] w-[50%] h-[50%] rounded-full bg-indigo-500/10 dark:bg-indigo-600/20 blur-[120px]"
      ></div>
      <div
        class="absolute top-[60%] -right-[10%] w-[40%] h-[60%] rounded-full bg-purple-500/10 dark:bg-fuchsia-600/10 blur-[120px]"
      ></div>
    </div>

    <!-- Sidebar -->
    <AppSidebar />

    <!-- Main Content wrapper -->
    <div class="flex-1 flex flex-col h-full relative z-10 overflow-hidden">
      <!-- Header -->
      <header
        class="h-16 flex-shrink-0 border-b border-slate-200 dark:border-slate-800 bg-white/40 dark:bg-slate-900/40 backdrop-blur-md px-6 flex items-center justify-between"
      >
        <!-- Mobile menu placeholder (hidden on desktop) -->
        <div class="md:hidden font-bold tracking-tight">CT Translator</div>

        <div
          class="hidden md:block text-sm font-medium text-slate-500 capitalize"
        >
          {{ $route.name?.toString().replace("-", " ") }}
        </div>

        <!-- Header tools -->
        <div class="flex items-center gap-4">
          <StatusIndicator />
          <div class="w-px h-6 bg-slate-200 dark:bg-slate-700"></div>
          <LanguageSelector />
          <ThemeToggle />
        </div>
      </header>

      <!-- Main scrollable content -->
      <main class="flex-1 overflow-x-hidden overflow-y-auto p-4 md:p-6 lg:p-8">
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>
