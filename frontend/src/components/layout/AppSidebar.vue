<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";
import { useI18n } from "vue-i18n";
import {
  LayoutDashboard,
  Languages,
  FileText,
  History,
  Cpu,
  BookOpen,
  Settings,
} from "lucide-vue-next";

const route = useRoute();
const { t } = useI18n();

const navItems = computed(() => [
  {
    name: t("nav.dashboard"),
    path: "/",
    icon: LayoutDashboard,
    active: route.path === "/",
  },
  {
    name: t("nav.textTranslation"),
    path: "/translate",
    icon: Languages,
    active: route.path === "/translate",
  },
  {
    name: t("nav.fileTranslation"),
    path: "/translate/file",
    icon: FileText,
    active: route.path === "/translate/file",
  },
  {
    name: t("nav.history"),
    path: "/history",
    icon: History,
    active: route.path === "/history",
  },
  {
    name: t("nav.models"),
    path: "/models",
    icon: Cpu,
    active: route.path === "/models",
  },
  {
    name: "Glossaries",
    path: "/glossaries",
    icon: BookOpen,
    active: route.path === "/glossaries",
  },
  {
    name: t("nav.settings"),
    path: "/settings",
    icon: Settings,
    active: route.path === "/settings",
  },
]);
</script>

<template>
  <aside
    class="w-64 flex-shrink-0 border-r border-slate-200 dark:border-slate-800 bg-white/50 dark:bg-slate-900/50 backdrop-blur-xl hidden md:flex flex-col h-full relative z-20"
  >
    <!-- Branding -->
    <div
      class="h-16 flex items-center px-6 border-b border-slate-200 dark:border-slate-800"
    >
      <div class="flex items-center gap-3">
        <div
          class="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold shadow-md shadow-indigo-500/20"
        >
          CT
        </div>
        <span
          class="font-bold text-lg tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-slate-800 to-slate-500 dark:from-white dark:to-slate-300"
        >
          Translator
        </span>
      </div>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="flex items-center gap-3 px-3 py-2.5 rounded-lg font-medium transition-all duration-200 group"
        :class="
          item.active
            ? 'bg-indigo-50 dark:bg-indigo-500/10 text-indigo-600 dark:text-indigo-400'
            : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-white'
        "
      >
        <component
          :is="item.icon"
          class="w-5 h-5 transition-transform group-hover:scale-110"
          :class="
            item.active
              ? 'text-indigo-600 dark:text-indigo-400'
              : 'text-slate-400'
          "
        />
        {{ item.name }}
      </router-link>
    </nav>

    <!-- Footer info -->
    <div
      class="p-4 border-t border-slate-200 dark:border-slate-800 text-xs text-slate-500 text-center"
    >
      Confidential Translator v0.1.0
    </div>
  </aside>
</template>
