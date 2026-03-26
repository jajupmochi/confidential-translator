<script setup lang="ts">
import { useSettingsStore } from "@/stores/settings";
import { setI18nLanguage, availableLocales } from "@/i18n";
import { Languages, Check } from "lucide-vue-next";

const settings = useSettingsStore();

function changeLocale(code: "en" | "zh" | "de" | "fr") {
  settings.setLocale(code);
  setI18nLanguage(code);
}
</script>

<template>
  <div class="relative group">
    <button
      class="btn-icon bg-white/50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 hover:bg-white dark:hover:bg-slate-700"
      title="Language"
    >
      <Languages class="w-5 h-5 text-slate-600 dark:text-slate-300" />
    </button>

    <!-- Dropdown -->
    <div
      class="absolute right-0 mt-2 w-36 glass-panel rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50"
    >
      <div class="p-1">
        <button
          v-for="loc in availableLocales"
          :key="loc.code"
          @click="changeLocale(loc.code as any)"
          class="w-full flex items-center justify-between px-3 py-2 text-sm rounded-md transition-colors hover:bg-slate-100 dark:hover:bg-slate-800/50"
          :class="{
            'text-primary-600 dark:text-primary-400 font-medium':
              settings.locale === loc.code,
          }"
        >
          {{ loc.name }}
          <Check v-if="settings.locale === loc.code" class="w-4 h-4" />
        </button>
      </div>
    </div>
  </div>
</template>
