<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import {
  Languages,
  FileText,
  Clock,
  Zap,
  TrendingDown,
  Activity,
} from "lucide-vue-next";

const { t } = useI18n();
const loading = ref(true);
const stats = ref<any>(null);

async function fetchStats() {
  try {
    const res = await fetch("/api/statistics");
    if (res.ok) {
      stats.value = await res.json();
    }
  } catch (e) {
    console.error("Failed to fetch stats", e);
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  fetchStats();
});
</script>

<template>
  <div class="space-y-6">
    <!-- Welcome Header -->
    <div
      class="glass-card p-8 bg-gradient-to-br from-indigo-500/10 to-purple-500/10 dark:from-indigo-900/20 dark:to-purple-900/20 border-indigo-100 dark:border-indigo-900/30"
    >
      <h1
        class="text-3xl font-bold tracking-tight text-slate-900 dark:text-white mb-2"
      >
        {{ t("dashboard.welcome") }}
      </h1>
      <p class="text-slate-600 dark:text-slate-300 max-w-2xl text-lg">
        Your offline, privacy-first translation environment powered by local
        LLMs.
      </p>
    </div>

    <div
      v-if="loading"
      class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
    >
      <div
        v-for="i in 4"
        :key="i"
        class="glass-card p-6 h-32 animate-pulse bg-slate-200/50 dark:bg-slate-800/50"
      ></div>
    </div>

    <!-- Stat Grid -->
    <div
      v-else-if="stats"
      class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
    >
      <!-- Translations -->
      <div class="glass-card p-6 relative overflow-hidden group">
        <div
          class="absolute top-0 right-0 p-4 opacity-10 group-hover:scale-110 group-hover:-rotate-12 transition-transform duration-300"
        >
          <Languages class="w-24 h-24 text-indigo-600 dark:text-indigo-400" />
        </div>
        <h3 class="text-sm font-medium text-slate-500 dark:text-slate-400 mb-1">
          {{ t("dashboard.totalTranslations") }}
        </h3>
        <p class="text-4xl font-bold text-slate-900 dark:text-white font-mono">
          {{ stats.total_translations.toLocaleString() }}
        </p>
        <div
          class="mt-4 flex items-center text-sm text-indigo-600 dark:text-indigo-400 font-medium bg-indigo-50 dark:bg-indigo-500/10 w-fit px-2.5 py-1 rounded-full"
        >
          <FileText class="w-4 h-4 mr-1.5" />
          {{ stats.total_files_translated.toLocaleString() }} files
        </div>
      </div>

      <!-- Characters -->
      <div class="glass-card p-6 relative overflow-hidden group">
        <div
          class="absolute top-0 right-0 p-4 opacity-10 group-hover:scale-110 group-hover:-rotate-12 transition-transform duration-300"
        >
          <Activity class="w-24 h-24 text-emerald-600 dark:text-emerald-400" />
        </div>
        <h3 class="text-sm font-medium text-slate-500 dark:text-slate-400 mb-1">
          {{ t("dashboard.charsTranslated") }}
        </h3>
        <p class="text-4xl font-bold text-slate-900 dark:text-white font-mono">
          {{ (stats.total_characters_translated / 1000).toFixed(1) }}k
        </p>
      </div>

      <!-- Avg Time -->
      <div class="glass-card p-6 relative overflow-hidden group">
        <div
          class="absolute top-0 right-0 p-4 opacity-10 group-hover:scale-110 group-hover:-rotate-12 transition-transform duration-300"
        >
          <Clock class="w-24 h-24 text-amber-600 dark:text-amber-400" />
        </div>
        <h3 class="text-sm font-medium text-slate-500 dark:text-slate-400 mb-1">
          {{ t("dashboard.avgTime") }}
        </h3>
        <p class="text-4xl font-bold text-slate-900 dark:text-white font-mono">
          {{ (stats.average_time_ms / 1000).toFixed(1) }}s
        </p>
        <div
          class="mt-4 flex items-center text-sm text-emerald-600 dark:text-emerald-400 font-medium bg-emerald-50 dark:bg-emerald-500/10 w-fit px-2.5 py-1 rounded-full"
        >
          <Zap class="w-4 h-4 mr-1.5" />
          Fast mode
        </div>
      </div>

      <!-- Top Pair -->
      <div class="glass-card p-6 relative overflow-hidden group">
        <div
          class="absolute top-0 right-0 p-4 opacity-10 group-hover:scale-110 group-hover:-rotate-12 transition-transform duration-300"
        >
          <TrendingDown class="w-24 h-24 text-rose-600 dark:text-rose-400" />
        </div>
        <h3 class="text-sm font-medium text-slate-500 dark:text-slate-400 mb-1">
          {{ t("dashboard.topPair") }}
        </h3>
        <p
          class="text-3xl font-bold text-slate-900 dark:text-white uppercase tracking-wider"
        >
          {{ stats.most_used_language_pair }}
        </p>
      </div>
    </div>

    <!-- Recent History Table -->
    <div
      v-if="stats && stats.recent_translations.length > 0"
      class="glass-card overflow-hidden"
    >
      <div class="px-6 py-4 border-b border-slate-200 dark:border-slate-800">
        <h2 class="text-lg font-semibold text-slate-900 dark:text-white">
          {{ t("dashboard.recentHistory") }}
        </h2>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead
            class="bg-slate-50 dark:bg-slate-900/50 text-slate-500 dark:text-slate-400"
          >
            <tr>
              <th class="px-6 py-3 font-medium">Type</th>
              <th class="px-6 py-3 font-medium">Langs</th>
              <th class="px-6 py-3 font-medium">Time</th>
              <th class="px-6 py-3 font-medium">Chars</th>
              <th class="px-6 py-3 font-medium">Speed</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 dark:divide-slate-800">
            <tr
              v-for="tx in stats.recent_translations"
              :key="tx.id"
              class="hover:bg-slate-50/50 dark:hover:bg-slate-800/20 transition-colors"
            >
              <td class="px-6 py-4">
                <span
                  class="inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-medium"
                  :class="
                    tx.translation_type === 'text'
                      ? 'bg-indigo-50 text-indigo-700 dark:bg-indigo-500/10 dark:text-indigo-400'
                      : 'bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-400'
                  "
                >
                  <Languages
                    v-if="tx.translation_type === 'text'"
                    class="w-3.5 h-3.5"
                  />
                  <FileText v-else class="w-3.5 h-3.5" />
                  {{ tx.translation_type }}
                </span>
              </td>
              <td
                class="px-6 py-4 font-mono text-xs text-slate-600 dark:text-slate-300"
              >
                {{ tx.source_language.toUpperCase() }} &rarr;
                {{ tx.target_language.toUpperCase() }}
              </td>
              <td class="px-6 py-4 text-slate-600 dark:text-slate-300">
                {{ (tx.time_taken_ms / 1000).toFixed(1) }}s
              </td>
              <td
                class="px-6 py-4 font-mono text-slate-600 dark:text-slate-300"
              >
                {{ tx.characters_input }}
              </td>
              <td
                class="px-6 py-4 text-xs font-medium text-slate-500 dark:text-slate-400"
              >
                {{ tx.tokens_per_second.toFixed(1) }} t/s
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
