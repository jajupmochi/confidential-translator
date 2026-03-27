<script setup lang="ts">
import { ref, computed, onBeforeUnmount } from "vue";
import { useI18n } from "vue-i18n";
import {
  Copy,
  Loader2,
  Play,
  Square,
  ChevronDown,
  ChevronRight,
  Brain,
  AlertTriangle,
} from "lucide-vue-next";
import { useSettingsStore } from "@/stores/settings";
import ModelMissingModal from "@/components/common/ModelMissingModal.vue";

const { t } = useI18n();
const settings = useSettingsStore();

const sourceText = ref("");
const translatedText = ref("");
const thinkingText = ref("");
const isTranslating = ref(false);
const isThinkingExpanded = ref(false);
const detectedLanguage = ref("");
const report = ref<any>(null);
const activeModel = ref("");
const elapsedSeconds = ref(0);
const abortController = ref<AbortController | null>(null);
const error = ref("");

const showModelMissingModal = ref(false);
const missingModelName = ref("");
let timerInterval: ReturnType<typeof setInterval> | null = null;

// Custom language support
const customSourceLang = ref("");
const customTargetLang = ref("");
const showLangValidationModal = ref(false);
const langValidationMessage = ref("");
const langValidationSuggestions = ref<string[]>([]);
const langValidationInput = ref("");
const langValidationField = ref<"source" | "target">("source");
const isValidatingLang = ref(false);

const sourceLang = ref(settings.defaultSourceLang);
const targetLang = ref(settings.defaultTargetLang);

const langOptions = [
  { value: "auto", label: t("common.autoDetect") },
  { value: "en", label: "English" },
  { value: "zh", label: "中文" },
  { value: "de", label: "Deutsch" },
  { value: "fr", label: "Français" },
  { value: "custom", label: "✏️ Custom…" },
];

const targetLangOptions = langOptions.filter((l) => l.value !== "auto");
const characterCount = computed(() => sourceText.value.length);

function getEffectiveSourceLang(): string {
  if (sourceLang.value === "custom") return customSourceLang.value.trim();
  return sourceLang.value;
}

function getEffectiveTargetLang(): string {
  if (targetLang.value === "custom") return customTargetLang.value.trim();
  return targetLang.value;
}

function startTimer() {
  elapsedSeconds.value = 0;
  timerInterval = setInterval(() => {
    elapsedSeconds.value += 0.1;
  }, 100);
}

function stopTimer() {
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
}

async function validateLanguage(langName: string): Promise<{valid: boolean; suggestions: string[]}> {
  try {
    isValidatingLang.value = true;
    const res = await fetch("/api/validate-language", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ language_name: langName, model: settings.defaultModel }),
    });
    if (!res.ok) return { valid: false, suggestions: [] };
    const data = await res.json();
    return { valid: data.valid, suggestions: data.suggestions || [] };
  } catch {
    return { valid: false, suggestions: [] };
  } finally {
    isValidatingLang.value = false;
  }
}

function handleLangSuggestionClick(suggestion: string) {
  langValidationInput.value = suggestion;
}

async function handleLangValidationRetry() {
  const input = langValidationInput.value.trim();
  if (!input) return;

  const result = await validateLanguage(input);
  if (result.valid) {
    if (langValidationField.value === "source") {
      customSourceLang.value = input;
    } else {
      customTargetLang.value = input;
    }
    showLangValidationModal.value = false;
    handleTranslate();
  } else {
    langValidationMessage.value = `"${input}" is not recognized as a valid language.`;
    langValidationSuggestions.value = result.suggestions;
  }
}

async function handleTranslate() {
  if (!sourceText.value.trim() || isTranslating.value) return;

  // Validate custom languages first
  const effSource = getEffectiveSourceLang();
  const effTarget = getEffectiveTargetLang();

  if (sourceLang.value === "custom" && effSource) {
    const result = await validateLanguage(effSource);
    if (!result.valid) {
      langValidationField.value = "source";
      langValidationMessage.value = `"${effSource}" is not recognized as a valid language name.`;
      langValidationSuggestions.value = result.suggestions;
      langValidationInput.value = effSource;
      showLangValidationModal.value = true;
      return;
    }
  }

  if (targetLang.value === "custom" && effTarget) {
    const result = await validateLanguage(effTarget);
    if (!result.valid) {
      langValidationField.value = "target";
      langValidationMessage.value = `"${effTarget}" is not recognized as a valid language name.`;
      langValidationSuggestions.value = result.suggestions;
      langValidationInput.value = effTarget;
      showLangValidationModal.value = true;
      return;
    }
  }

  isTranslating.value = true;
  translatedText.value = "";
  thinkingText.value = "";
  report.value = null;
  activeModel.value = settings.defaultModel;
  isThinkingExpanded.value = false;
  startTimer();

  // Create abort controller for cancellation
  abortController.value = new AbortController();

  try {
    const res = await fetch("/api/translate/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: sourceText.value,
        source_language: effSource || "auto",
        target_language: effTarget,
        model: settings.defaultModel,
      }),
      signal: abortController.value.signal,
    });

    if (!res.ok) {
      translatedText.value = "Translation failed. Please check Ollama connection.";
      return;
    }

    const reader = res.body?.getReader();
    if (!reader) return;

    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        const jsonStr = line.slice(6).trim();
        if (!jsonStr) continue;

        try {
          const event = JSON.parse(jsonStr);

          switch (event.type) {
            case "meta":
              activeModel.value = event.model;
              if (event.source_lang && sourceLang.value === "auto") {
                const det = langOptions.find((l) => l.value === event.source_lang);
                if (det) detectedLanguage.value = det.label;
              }
              break;
            case "thinking":
              thinkingText.value += event.content;
              break;
            case "token":
              translatedText.value += event.content;
              break;
            case "chunk_done":
              // Could show chunk progress in the future
              break;
            case "done":
              report.value = event.report;
              break;
            case "error":
              if (event.error_type === "model_not_found") {
                missingModelName.value = event.model || activeModel.value;
                showModelMissingModal.value = true;
                error.value = `Model not found. Please pull it.`;
                translatedText.value += `\n[Error: Model '${missingModelName.value}' is not downloaded. Please download it via the prompt.]`;
              } else {
                translatedText.value += `\n[Error: ${event.message}]`;
              }
              break;
          }
        } catch {
          // Ignore malformed JSON
        }
      }
    }
  } catch (e: any) {
    if (e.name === "AbortError") {
      // User aborted — keep partial output
    } else {
      console.error("Translation stream error", e);
      translatedText.value = translatedText.value || "Network error. Backend not reachable.";
    }
  } finally {
    isTranslating.value = false;
    abortController.value = null;
    stopTimer();
  }
}

function handleAbort() {
  abortController.value?.abort();
}

async function handleCopy() {
  if (translatedText.value) {
    await navigator.clipboard.writeText(translatedText.value);
  }
}

onBeforeUnmount(() => {
  stopTimer();
  abortController.value?.abort();
});
</script>

<template>
  <div class="space-y-6 h-[calc(100vh-8rem)] flex flex-col">
    <!-- Toolbar -->
    <div class="flex items-center gap-4 p-4 glass-card shadow-sm flex-shrink-0">
      <div class="flex items-center gap-2">
        <div class="flex flex-col gap-1">
          <select
            v-model="sourceLang"
            class="input-field max-w-[150px] py-1.5 text-sm"
          >
            <option v-for="l in langOptions" :key="l.value" :value="l.value">
              {{ l.label }}
            </option>
          </select>
          <input
            v-if="sourceLang === 'custom'"
            v-model="customSourceLang"
            type="text"
            placeholder="e.g. Español, 日本語…"
            class="input-field max-w-[150px] py-1 text-xs"
          />
        </div>
        <span class="text-slate-400">&rarr;</span>
        <div class="flex flex-col gap-1">
          <select
            v-model="targetLang"
            class="input-field max-w-[150px] py-1.5 text-sm font-medium text-indigo-600 dark:text-indigo-400"
          >
            <option
              v-for="l in targetLangOptions"
              :key="l.value"
              :value="l.value"
            >
              {{ l.label }}
            </option>
          </select>
          <input
            v-if="targetLang === 'custom'"
            v-model="customTargetLang"
            type="text"
            placeholder="e.g. Español, 日本語…"
            class="input-field max-w-[150px] py-1 text-xs"
          />
        </div>
      </div>

      <!-- Language validation indicator -->
      <div
        v-if="isValidatingLang"
        class="flex items-center gap-3 px-3 py-1.5 rounded-lg bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800/30 text-amber-700 dark:text-amber-400 text-xs font-medium"
      >
        <Loader2 class="w-3.5 h-3.5 animate-spin" />
        <span>Validating language name with AI…</span>
      </div>

      <div class="flex-1"></div>

      <!-- Live status during translation -->
      <div
        v-if="isTranslating"
        class="flex items-center gap-3 text-xs text-slate-500 dark:text-slate-400 font-mono"
      >
        <span class="flex items-center gap-1">
          <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          🤖 {{ activeModel }}
        </span>
        <span>⏱️ {{ elapsedSeconds.toFixed(1) }}s</span>
      </div>

      <!-- Abort button -->
      <button
        v-if="isTranslating"
        @click="handleAbort"
        class="btn bg-rose-600 hover:bg-rose-700 text-white min-w-[100px] shadow-md shadow-rose-500/20"
      >
        <Square class="w-4 h-4 mr-1 fill-current" />
        Stop
      </button>

      <!-- Translate button -->
      <button
        v-else
        @click="handleTranslate"
        :disabled="characterCount === 0 || isValidatingLang"
        class="btn-primary min-w-[140px]"
      >
        <Loader2 v-if="isValidatingLang" class="w-4 h-4 mr-1 animate-spin" />
        <Play v-else class="w-4 h-4 mr-1 fill-current" />
        {{ isValidatingLang ? 'Validating…' : t("common.translate") }}
      </button>
    </div>

    <!-- Translation Panes -->
    <div class="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-6 min-h-0">
      <!-- Source -->
      <div
        class="glass-card relative flex flex-col overflow-hidden group focus-within:ring-2 focus-within:ring-indigo-500/50 focus-within:border-indigo-500"
      >
        <div class="absolute top-4 left-4 z-10 flex gap-2">
          <span
            v-if="sourceLang === 'auto' && detectedLanguage"
            class="px-2 py-1 text-xs font-medium rounded-md bg-indigo-100 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300 backdrop-blur-md"
          >
            {{ t("common.autoDetect") }}: {{ detectedLanguage }}
          </span>
        </div>
        <textarea
          v-model="sourceText"
          :placeholder="t('translate.sourcePlaceholder')"
          class="flex-1 w-full resize-none bg-transparent p-4 md:p-6 text-lg leading-relaxed focus:outline-none text-slate-900 dark:text-slate-100 pt-12"
        ></textarea>
        <!-- Footer info -->
        <div
          class="px-4 py-3 border-t border-slate-200/50 dark:border-slate-700/50 flex justify-between text-xs text-slate-400 font-mono"
        >
          <span>{{ characterCount }} chars</span>
        </div>
      </div>

      <!-- Target -->
      <div
        class="glass-card relative flex flex-col overflow-hidden bg-slate-50/50 dark:bg-[#0B1120]/50"
      >
        <!-- Thinking process (collapsible) -->
        <div
          v-if="thinkingText"
          class="border-b border-amber-200/50 dark:border-amber-800/30 bg-amber-50/50 dark:bg-amber-900/10"
        >
          <button
            @click="isThinkingExpanded = !isThinkingExpanded"
            class="w-full flex items-center gap-2 px-4 py-2 text-xs font-medium text-amber-700 dark:text-amber-400 hover:bg-amber-100/50 dark:hover:bg-amber-900/20 transition-colors"
          >
            <Brain class="w-3.5 h-3.5" />
            <component
              :is="isThinkingExpanded ? ChevronDown : ChevronRight"
              class="w-3.5 h-3.5"
            />
            <span>Thinking Process</span>
            <span class="text-amber-500/60 ml-auto">
              {{ thinkingText.length }} chars
            </span>
          </button>
          <div
            v-if="isThinkingExpanded"
            class="px-4 pb-3 max-h-[200px] overflow-y-auto"
          >
            <pre
              class="text-xs text-amber-800/70 dark:text-amber-300/60 whitespace-pre-wrap font-mono italic leading-relaxed"
            >{{ thinkingText }}</pre>
          </div>
        </div>

        <!-- Translated text -->
        <textarea
          v-model="translatedText"
          readonly
          :placeholder="t('translate.targetPlaceholder')"
          class="flex-1 w-full resize-none bg-transparent p-4 md:p-6 text-lg leading-relaxed focus:outline-none text-slate-900 dark:text-slate-100"
          :class="{ 'pt-4': thinkingText, 'pt-12': !thinkingText }"
        ></textarea>

        <!-- Copy Button overlay -->
        <div
          class="absolute top-4 right-4 z-10 opacity-0 group-hover:opacity-100 transition-opacity"
          :class="{ 'top-2 right-2': thinkingText }"
        >
          <button
            @click="handleCopy"
            :disabled="!translatedText"
            class="btn-icon bg-white/80 dark:bg-slate-800/80 hover:bg-white dark:hover:bg-slate-700 backdrop-blur border border-slate-200 dark:border-slate-700"
          >
            <Copy class="w-4 h-4 text-slate-500" />
          </button>
        </div>

        <!-- Live streaming indicator -->
        <div
          v-if="isTranslating"
          class="px-4 py-3 bg-emerald-50 dark:bg-emerald-900/20 border-t border-emerald-100 dark:border-emerald-800/50 flex items-center gap-3 text-xs font-medium text-emerald-700 dark:text-emerald-300"
        >
          <Loader2 class="w-3.5 h-3.5 animate-spin" />
          <span>Translating...</span>
          <span class="ml-auto font-mono">
            🤖 {{ activeModel }} &nbsp; ⏱️ {{ elapsedSeconds.toFixed(1) }}s
          </span>
        </div>

        <!-- Final Translation Report -->
        <div
          v-else-if="report"
          class="px-4 py-3 bg-indigo-50 dark:bg-indigo-900/20 border-t border-indigo-100 dark:border-indigo-800/50 flex items-center justify-between text-xs font-medium text-indigo-700 dark:text-indigo-300"
        >
          <div class="flex items-center gap-4">
            <span title="Model Used">🤖 {{ report.model_used }}</span>
            <span title="Time Taken"
              >⏱️ {{ (report.time_taken_ms / 1000).toFixed(1) }}s</span
            >
            <span title="Inference Speed"
              >⚡ {{ report.tokens_per_second.toFixed(1) }} t/s</span
            >
          </div>
        </div>

        <!-- AI Disclaimer -->
        <div
          v-if="report && !isTranslating"
          class="px-4 py-2 bg-amber-50 dark:bg-amber-900/10 border-t border-amber-200/50 dark:border-amber-800/30 flex items-center gap-2 text-xs text-amber-700 dark:text-amber-400"
        >
          <AlertTriangle class="w-3.5 h-3.5 flex-shrink-0" />
          <span>⚠️ This translation was generated by an external AI language model. Please verify critical content for accuracy.</span>
        </div>
      </div>
    </div>

    <!-- Missing Model Modal -->
    <ModelMissingModal
      v-model:show="showModelMissingModal"
      :model-name="missingModelName"
    />

    <!-- Language Validation Modal -->
    <Teleport to="body">
      <div
        v-if="showLangValidationModal"
        class="fixed inset-0 z-[999] flex items-center justify-center bg-black/40 backdrop-blur-sm"
        @click.self="showLangValidationModal = false"
      >
        <div class="glass-card p-6 w-full max-w-md mx-4 space-y-4 shadow-2xl">
          <div class="flex items-center gap-2 text-amber-600 dark:text-amber-400">
            <AlertTriangle class="w-5 h-5" />
            <h3 class="text-lg font-bold">Invalid Language</h3>
          </div>
          <p class="text-sm text-slate-600 dark:text-slate-300">{{ langValidationMessage }}</p>

          <div v-if="langValidationSuggestions.length" class="space-y-2">
            <p class="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">Did you mean:</p>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="suggestion in langValidationSuggestions"
                :key="suggestion"
                @click="handleLangSuggestionClick(suggestion)"
                class="px-3 py-1.5 text-sm rounded-lg bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800/50 hover:bg-indigo-100 dark:hover:bg-indigo-900/50 transition-colors cursor-pointer"
              >
                {{ suggestion }}
              </button>
            </div>
          </div>

          <div class="space-y-2">
            <label class="text-xs font-medium text-slate-500 dark:text-slate-400">Revised language name:</label>
            <input
              v-model="langValidationInput"
              type="text"
              class="input-field w-full"
              placeholder="Type corrected language name…"
              @keyup.enter="handleLangValidationRetry"
            />
          </div>

          <div class="flex justify-end gap-3">
            <button
              @click="showLangValidationModal = false"
              class="btn-secondary text-sm"
            >
              Cancel
            </button>
            <button
              @click="handleLangValidationRetry"
              :disabled="!langValidationInput.trim() || isValidatingLang"
              class="btn-primary text-sm"
            >
              <Loader2 v-if="isValidatingLang" class="w-3.5 h-3.5 mr-1 animate-spin" />
              Retry
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
