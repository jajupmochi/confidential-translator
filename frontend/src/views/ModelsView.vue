<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useI18n } from "vue-i18n";
import { useOllamaStore } from "@/stores/ollama";
import {
  Server,
  Download,
  Trash2,
  Cpu,
  HardDrive,
  CheckCircle2,
  AlertCircle,
  Loader2,
} from "lucide-vue-next";

const ollamaStore = useOllamaStore();
const { t } = useI18n();
const loading = ref(true);
const pullModelName = ref("");
const pullError = ref("");

const isPulling = computed(() => Object.keys(ollamaStore.pullProgress).length > 0);

async function fetchModels() {
  loading.value = true;
  try {
    await ollamaStore.fetchModels();
  } catch (e) {
    console.error("Failed to fetch models", e);
  } finally {
    loading.value = false;
  }
}

async function pullModel() {
  if (!pullModelName.value) return;
  const name = pullModelName.value;
  pullModelName.value = "";
  pullError.value = "";
  await ollamaStore.pullModel(name);
}

async function deleteModel(name: string) {
  if (!confirm(t("models.deleteConfirm", { name }))) return;
  try {
    const res = await fetch(`/api/models/${name}`, { method: "DELETE" });
    if (res.ok) {
      await fetchModels();
    }
  } catch (e) {
    console.error("Failed to delete", e);
  }
}

onMounted(() => fetchModels());

const formatBytes = (bytes: number) => {
  if (!bytes) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
};
</script>

<template>
  <div class="space-y-6 max-w-5xl">
    <div class="flex items-center justify-between">
      <h1
        class="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-slate-900 to-slate-500 dark:from-white dark:to-slate-400"
      >
        {{ t("models.title") }}
      </h1>

      <div class="flex items-center gap-2">
        <input
          v-model="pullModelName"
          @keyup.enter="pullModel"
          type="text"
          :placeholder="t('models.pullPlaceholder')"
          class="input-field w-48"
          :disabled="isPulling"
        />
        <button
          @click="pullModel"
          :disabled="!pullModelName || isPulling"
          class="btn-primary"
        >
          <Loader2 v-if="isPulling" class="w-4 h-4 animate-spin mr-1" />
          <Download v-else class="w-4 h-4 mr-1" />
          {{ t("models.pull") }}
        </button>
      </div>
    </div>

    <div
      v-if="pullError"
      class="p-4 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 flex items-center gap-2"
    >
      <AlertCircle class="w-5 h-5" />
      {{ pullError }}
    </div>

    <!-- Recommended Model -->
    <div
      v-if="ollamaStore.recommendation"
      class="glass-card p-6 bg-gradient-to-r from-emerald-50 to-teal-50 dark:from-emerald-900/10 dark:to-teal-900/10 border-emerald-100 dark:border-emerald-800/30"
    >
      <div class="flex items-start gap-4">
        <div
          class="p-3 bg-emerald-100 dark:bg-emerald-900/50 rounded-xl text-emerald-600 dark:text-emerald-400"
        >
          <CheckCircle2 class="w-6 h-6" />
        </div>
        <div>
          <h2 class="text-lg font-bold text-slate-900 dark:text-white mb-1">
            {{ t("models.recommended") }}
          </h2>
          <p class="text-slate-600 dark:text-slate-300 mb-2 text-sm">
            {{ ollamaStore.recommendation.reason }}
          </p>

          <div class="flex flex-wrap gap-4 mt-2">
            <div
              class="bg-white/60 dark:bg-slate-900/40 px-3 py-2 rounded-lg border border-slate-200/50 dark:border-slate-700/50"
            >
              <div class="text-xs text-slate-500 mb-0.5">Primary Model</div>
              <div
                class="font-mono font-medium text-emerald-700 dark:text-emerald-400"
              >
                {{ ollamaStore.recommendation.recommended_model }}
              </div>
            </div>
            
            <div
              v-for="alt in ollamaStore.recommendation.alternatives"
              :key="alt"
              class="bg-white/60 dark:bg-slate-900/40 px-3 py-2 rounded-lg border border-slate-200/50 dark:border-slate-700/50"
            >
              <div class="text-xs text-slate-500 mb-0.5">Alternative</div>
              <div
                class="font-mono font-medium text-slate-700 dark:text-slate-300"
              >
                {{ alt }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Active Pulls -->
    <div v-if="Object.keys(ollamaStore.pullProgress).length > 0" class="space-y-4">
      <div 
        v-for="(progress, name) in ollamaStore.pullProgress" 
        :key="name"
        v-show="progress.status !== 'success'"
        class="glass-card p-4 border-indigo-200 dark:border-indigo-900 bg-indigo-50/30"
      >
        <div class="flex justify-between items-center mb-2">
          <div class="font-mono font-bold text-indigo-700 dark:text-indigo-400 text-sm">
            Pulling {{ name }}...
          </div>
          <div class="text-xs font-bold text-indigo-600 dark:text-indigo-300">
            {{ progress.percent }}%
          </div>
        </div>
        <div class="h-1.5 w-full bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
          <div 
            class="h-full bg-indigo-500 transition-all duration-300" 
            :style="{ width: progress.percent + '%' }"
          ></div>
        </div>
        <div class="text-[10px] text-slate-500 mt-1 uppercase font-bold tracking-tight">
          {{ progress.status }}
        </div>
      </div>
    </div>

    <!-- Installed Models -->
    <div class="glass-card overflow-hidden">
      <div
        class="px-6 py-4 border-b border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50"
      >
        <h2
          class="text-lg font-semibold text-slate-900 dark:text-white flex items-center gap-2"
        >
          <Server class="w-5 h-5 text-indigo-500" />
          {{ t("models.installed") }}
        </h2>
      </div>

      <div v-if="loading" class="p-12 flex justify-center">
        <Loader2 class="w-8 h-8 text-indigo-600 animate-spin" />
      </div>

      <div
        v-else-if="ollamaStore.models.length === 0"
        class="p-12 text-center text-slate-500"
      >
        {{ t("models.noModelsDesc") }}
      </div>

      <div v-else class="divide-y divide-slate-200 dark:divide-slate-800">
        <div
          v-for="model in ollamaStore.models"
          :key="model.name"
          class="p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 hover:bg-slate-50/50 dark:hover:bg-slate-800/20 transition-colors"
        >
          <div class="flex-1">
            <h3
              class="text-lg font-bold font-mono text-slate-900 dark:text-white mb-1"
            >
              {{ model.name }}
            </h3>
            <div
              class="flex flex-wrap items-center gap-4 text-sm text-slate-500"
            >
              <span class="flex items-center gap-1.5"
                ><HardDrive class="w-4 h-4" />
                {{ formatBytes(model.size) }}</span
              >
              <span
                class="flex items-center gap-1.5"
                v-if="model.parameter_size"
                ><Cpu class="w-4 h-4" />
                {{ model.parameter_size }} params</span
              >
              <span
                class="px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-medium text-xs border border-slate-200 dark:border-slate-700"
                v-if="model.quantization"
              >
                {{ model.quantization }}
              </span>
            </div>
          </div>

          <button
            @click="deleteModel(model.name)"
            class="btn-icon text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-500/10 border border-transparent hover:border-rose-200 dark:hover:border-rose-900"
          >
            <Trash2 class="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
