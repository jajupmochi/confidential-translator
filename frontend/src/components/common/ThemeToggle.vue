<script setup lang="ts">
import { useSettingsStore } from "@/stores/settings";
import { Sun, Moon, Monitor } from "lucide-vue-next";

const settings = useSettingsStore();

const themes = [
  { value: "light", icon: Sun, label: "Light" },
  { value: "dark", icon: Moon, label: "Dark" },
  { value: "system", icon: Monitor, label: "System" },
] as const;
</script>

<template>
  <div class="relative group">
    <button
      class="btn-icon bg-white/50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 hover:bg-white dark:hover:bg-slate-700"
    >
      <Sun v-if="settings.theme === 'light'" class="w-5 h-5 text-amber-500" />
      <Moon
        v-else-if="settings.theme === 'dark'"
        class="w-5 h-5 text-indigo-400"
      />
      <Monitor v-else class="w-5 h-5 text-slate-500 dark:text-slate-400" />
    </button>

    <!-- Dropdown -->
    <div
      class="absolute right-0 mt-2 w-36 glass-panel rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50"
    >
      <div class="p-1">
        <button
          v-for="t in themes"
          :key="t.value"
          @click="settings.setTheme(t.value)"
          class="w-full flex items-center gap-3 px-3 py-2 text-sm rounded-md transition-colors"
          :class="
            settings.theme === t.value
              ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400'
              : 'hover:bg-slate-100 dark:hover:bg-slate-800/50'
          "
        >
          <component :is="t.icon" class="w-4 h-4" />
          {{ t.label }}
        </button>
      </div>
    </div>
  </div>
</template>
