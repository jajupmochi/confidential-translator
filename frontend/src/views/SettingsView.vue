<script setup lang="ts">
import { onMounted } from "vue";
import { useI18n } from "vue-i18n";
import { useSettingsStore } from "@/stores/settings";

const { t } = useI18n();
const settings = useSettingsStore();

onMounted(() => {
  settings.fetchBackendSettings();
});
</script>

<template>
  <div class="space-y-6 max-w-3xl">
    <div class="glass-card p-6">
      <h1
        class="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-slate-900 to-slate-500 dark:from-white dark:to-slate-400 mb-6"
      >
        {{ t("settings.title") }}
      </h1>

      <div class="space-y-8">
        <!-- Appearance -->
        <section>
          <h2
            class="text-sm font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-4 border-b border-slate-200 dark:border-slate-800 pb-2"
          >
            {{ t("settings.appearance") }}
          </h2>

          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <div>
                <p class="font-medium text-slate-900 dark:text-white">
                  {{ t("settings.themePref") }}
                </p>
                <p class="text-sm text-slate-500">{{ t("settings.themeDesc") }}</p>
              </div>
              <select
                class="input-field w-40"
                :value="settings.theme"
                @change="(e) => settings.setTheme((e.target as any).value)"
              >
                <option value="system">{{ t("settings.systemDefault") }}</option>
                <option value="light">{{ t("settings.lightMode") }}</option>
                <option value="dark">{{ t("settings.darkMode") }}</option>
              </select>
            </div>
          </div>
        </section>

        <!-- Ollama Engine -->
        <section>
          <h2
            class="text-sm font-bold text-indigo-500 dark:text-indigo-400 uppercase tracking-wider mb-4 border-b border-indigo-200 dark:border-indigo-900/30 pb-2"
          >
            {{ t("settings.ollamaEngine") }}
          </h2>

          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <div>
                <p class="font-medium text-slate-900 dark:text-white">
                  Model Storage Path
                </p>
                <p class="text-sm text-slate-500">
                  Directory where LLM models are stored (OLLAMA_MODELS)
                </p>
              </div>
              <div class="flex items-center gap-2">
                <input
                  v-model="settings.ollamaModelsPath"
                  type="text"
                  class="input-field w-80 font-mono text-xs"
                  placeholder="e.g. /media/data/models"
                />
                <button
                  @click="settings.saveBackendSettings()"
                  class="btn-primary py-2 text-xs"
                >
                  {{ t("common.save") }}
                </button>
              </div>
            </div>
          </div>
        </section>

        <!-- Translation Defaults -->
        <section>
          <h2
            class="text-sm font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-4 border-b border-slate-200 dark:border-slate-800 pb-2"
          >
            {{ t("settings.translationSettings") }}
          </h2>

          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <div>
                <p class="font-medium text-slate-900 dark:text-white">
                  {{ t("settings.defaultSource") }}
                </p>
                <p class="text-sm text-slate-500">{{ t("settings.langDesc") }}</p>
              </div>
              <select
                v-model="settings.defaultSourceLang"
                class="input-field w-40"
              >
                <option value="auto">{{ t("common.autoDetect") }}</option>
                <option value="en">English</option>
                <option value="zh">中文</option>
                <option value="de">Deutsch</option>
                <option value="fr">Français</option>
              </select>
            </div>

            <div class="flex items-center justify-between">
              <div>
                <p class="font-medium text-slate-900 dark:text-white">
                  {{ t("settings.defaultTarget") }}
                </p>
                <p class="text-sm text-slate-500">{{ t("settings.langDesc") }}</p>
              </div>
              <select
                v-model="settings.defaultTargetLang"
                class="input-field w-40"
              >
                <option value="en">English</option>
                <option value="zh">中文</option>
                <option value="de">Deutsch</option>
                <option value="fr">Français</option>
              </select>
            </div>

            <div class="flex items-center justify-between">
              <div>
                <p class="font-medium text-slate-900 dark:text-white">
                  {{ t("settings.defaultModel") }}
                </p>
                <p class="text-sm text-slate-500">
                  {{ t("settings.defaultModelDesc") }}
                </p>
              </div>
              <input
                v-model="settings.defaultModel"
                type="text"
                class="input-field w-64 font-mono text-sm"
                placeholder="e.g. qwen3.5:9b"
              />
            </div>
          </div>
        </section>

        <!-- Danger Zone -->
        <section>
          <h2
            class="text-sm font-bold text-rose-500 dark:text-rose-400 uppercase tracking-wider mb-4 border-b border-rose-200 dark:border-rose-900/30 pb-2"
          >
            Danger Zone
          </h2>
          <div
            class="flex items-center justify-between p-4 bg-rose-50 dark:bg-rose-900/10 rounded-lg border border-rose-100 dark:border-rose-900/30"
          >
            <div>
              <p class="font-medium text-rose-900 dark:text-rose-300">
                Clear History
              </p>
              <p class="text-sm text-rose-700/80 dark:text-rose-400/80">
                Permanently delete all translation records
              </p>
            </div>
            <button
              class="btn bg-rose-600 hover:bg-rose-700 text-white shadow-md shadow-rose-500/20"
            >
              Clear All
            </button>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>
