<script setup lang="ts">
import { onMounted } from "vue";
import { useSettingsStore } from "@/stores/settings";

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
        Settings
      </h1>

      <div class="space-y-8">
        <!-- Appearance -->
        <section>
          <h2
            class="text-sm font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-4 border-b border-slate-200 dark:border-slate-800 pb-2"
          >
            Appearance
          </h2>

          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <div>
                <p class="font-medium text-slate-900 dark:text-white">
                  Theme Preference
                </p>
                <p class="text-sm text-slate-500">Select application theme</p>
              </div>
              <select
                class="input-field w-40"
                :value="settings.theme"
                @change="(e) => settings.setTheme((e.target as any).value)"
              >
                <option value="system">System Default</option>
                <option value="light">Light Mode</option>
                <option value="dark">Dark Mode</option>
              </select>
            </div>
          </div>
        </section>

        <!-- Ollama Engine -->
        <section>
          <h2
            class="text-sm font-bold text-indigo-500 dark:text-indigo-400 uppercase tracking-wider mb-4 border-b border-indigo-200 dark:border-indigo-900/30 pb-2"
          >
            Ollama Engine
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
                  Save
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
            Translation Defaults
          </h2>

          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <div>
                <p class="font-medium text-slate-900 dark:text-white">
                  Source Language
                </p>
                <p class="text-sm text-slate-500">Default input language</p>
              </div>
              <select
                v-model="settings.defaultSourceLang"
                class="input-field w-40"
              >
                <option value="auto">Auto Detect</option>
                <option value="en">English</option>
                <option value="zh">Chinese</option>
                <option value="de">German</option>
                <option value="fr">French</option>
              </select>
            </div>

            <div class="flex items-center justify-between">
              <div>
                <p class="font-medium text-slate-900 dark:text-white">
                  Target Language
                </p>
                <p class="text-sm text-slate-500">Default output language</p>
              </div>
              <select
                v-model="settings.defaultTargetLang"
                class="input-field w-40"
              >
                <option value="en">English</option>
                <option value="zh">Chinese</option>
                <option value="de">German</option>
                <option value="fr">French</option>
              </select>
            </div>

            <div class="flex items-center justify-between">
              <div>
                <p class="font-medium text-slate-900 dark:text-white">
                  Default Model
                </p>
                <p class="text-sm text-slate-500">
                  Ollama model to use automatically
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
