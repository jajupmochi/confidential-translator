<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import {
  UploadCloud,
  FileText,
  Download,
  Loader2,
  AlertCircle,
  AlertTriangle,
  Square,
  X,
  Brain,
  ChevronDown,
  ChevronRight,
  Play,
} from "lucide-vue-next";
import { useSettingsStore } from "@/stores/settings";
import ModelMissingModal from "@/components/common/ModelMissingModal.vue";

const { t } = useI18n();
const settings = useSettingsStore();

const fileInput = ref<HTMLInputElement | null>(null);
const selectedFile = ref<File | null>(null);
const isTranslating = ref(false);
const translatedContent = ref("");
const sourceContent = ref("");
const thinkingText = ref("");
const isThinkingExpanded = ref(false);
const error = ref("");
const report = ref<any>(null);
const activeModel = ref("");
const elapsedSeconds = ref(0);
const abortController = ref<AbortController | null>(null);
const chunkProgress = ref("");

const showModelMissingModal = ref(false);
const missingModelName = ref("");
const historyId = ref<number | null>(null);

// Language selection
const sourceLang = ref(settings.defaultSourceLang === "auto" ? "auto" : settings.defaultSourceLang);
const targetLang = ref(settings.defaultTargetLang);
const customSourceLang = ref("");
const customTargetLang = ref("");

const showLangValidationModal = ref(false);
const langValidationMessage = ref("");
const langValidationSuggestions = ref<string[]>([]);
const langValidationInput = ref("");
const langValidationField = ref<"source" | "target">("source");
const isValidatingLang = ref(false);

const langOptions = [
  { value: "auto", label: t("common.autoDetect") },
  { value: "en", label: "English" },
  { value: "zh", label: "中文" },
  { value: "de", label: "Deutsch" },
  { value: "fr", label: "Français" },
  { value: "custom", label: "✏️ Custom…" },
];
const targetLangOptions = langOptions.filter((l) => l.value !== "auto");

function getEffectiveSourceLang(): string {
  if (sourceLang.value === "custom") return customSourceLang.value.trim();
  return sourceLang.value;
}
function getEffectiveTargetLang(): string {
  if (targetLang.value === "custom") return customTargetLang.value.trim();
  return targetLang.value;
}

let timerInterval: ReturnType<typeof setInterval> | null = null;

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
    if (langValidationField.value === "source") customSourceLang.value = input;
    else customTargetLang.value = input;
    showLangValidationModal.value = false;
    startTranslation();
  } else {
    langValidationMessage.value = `"${input}" is not recognized as a valid language.`;
    langValidationSuggestions.value = result.suggestions;
  }
}

const handleDrop = (e: DragEvent) => {
  e.preventDefault();
  if (e.dataTransfer?.files.length) {
    validateAndSetFile(e.dataTransfer.files[0]);
  }
};

const handleFileSelect = (e: Event) => {
  const target = e.target as HTMLInputElement;
  if (target.files?.length) {
    validateAndSetFile(target.files[0]);
  }
};

const validateAndSetFile = (file: File) => {
  error.value = "";
  if (file.size > 50 * 1024 * 1024) {
    error.value = t("file.supportedFormats");
    return;
  }
  selectedFile.value = file;
  translatedContent.value = "";
  sourceContent.value = "";
  thinkingText.value = "";
  report.value = null;
};

const removeFile = () => {
  selectedFile.value = null;
  translatedContent.value = "";
  sourceContent.value = "";
  thinkingText.value = "";
  report.value = null;
  chunkProgress.value = "";
  if (fileInput.value) fileInput.value.value = "";
};

const triggerFileInput = async () => {
  try {
    const res = await fetch("/api/system/pick-file");
    const data = await res.json();
    if (data.file_path) {
      selectedFile.value = {
        name: data.file_name,
        path: data.file_path,
        type: "",
        size: 0,
      } as any;
      translatedContent.value = "";
      sourceContent.value = "";
      thinkingText.value = "";
      report.value = null;
      error.value = "";
    } else {
      // User cancelled picker
      return;
    }
  } catch (e) {
    // Fallback to HTML input
    fileInput.value?.click();
  }
};

const handleAbort = () => {
  abortController.value?.abort();
};

const startTranslation = async () => {
  if (!selectedFile.value) return;

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
  error.value = "";
  report.value = null;
  translatedContent.value = "";
  sourceContent.value = "";
  thinkingText.value = "";
  isThinkingExpanded.value = false;
  activeModel.value = settings.defaultModel;
  chunkProgress.value = "";
  historyId.value = null;
  startTimer();

  const isNative = !!(selectedFile.value as any).path;
  const formData = new FormData();
  if (isNative) {
    formData.append("file_path", (selectedFile.value as any).path);
  } else {
    formData.append("file", selectedFile.value);
  }
  formData.append("source_language", effSource || "auto");
  formData.append("target_language", effTarget);
  formData.append("model", settings.defaultModel);

  abortController.value = new AbortController();

  try {
    const endpoint = isNative ? "/api/translate/stream/file/native" : "/api/translate/stream/file";
    const res = await fetch(endpoint, {
      method: "POST",
      body: formData,
      signal: abortController.value.signal,
    });

    if (!res.ok) {
      const e = await res.json();
      if (res.status === 404 && e.detail === "model_not_found") {
        missingModelName.value = settings.defaultModel;
        showModelMissingModal.value = true;
        error.value = `Model '${settings.defaultModel}' not found. Please download it via the prompt.`;
      } else {
        error.value = e.detail || "Translation failed";
      }
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
            case "extracted_text":
              sourceContent.value = event.content;
              break;
            case "meta":
              activeModel.value = event.model;
              break;
            case "thinking":
              thinkingText.value += event.content;
              break;
            case "token":
              translatedContent.value += event.content;
              break;
            case "done":
              report.value = event.report;
              break;
            case "history":
              historyId.value = event.id;
              break;
            case "error":
              error.value = event.message;
              break;
          }
        } catch { /* ignore */ }
      }
    }
  } catch (e: any) {
    if (e.name === "AbortError") {
      error.value = "Translation was stopped by user.";
    } else {
      error.value = "Network error";
    }
  } finally {
    isTranslating.value = false;
    abortController.value = null;
    stopTimer();
  }
};

const downloadExport = async () => {
  if (!translatedContent.value || !selectedFile.value) return;

  try {
    const defaultName = `translated_${selectedFile.value.name}`;
    const cdRes = await fetch(`/api/system/save-file?default_name=${encodeURIComponent(defaultName)}`);
    
    if (cdRes.ok) {
      const cdData = await cdRes.json();
      
      if (cdData.file_path === null) {
        // User explicitly cancelled the native save dialog
        return;
      }
      
      if (cdData.file_path) {
        // Always use native export — write to the user's chosen path
        const payload: any = {
          save_path: cdData.file_path,
          translated_text: translatedContent.value,
          original_file_type: `.${selectedFile.value.name.split(".").pop()}`,
          file_name: `translated_${selectedFile.value.name.split(".")[0]}`,
        };
        
        // Include history_id if we have one, to update the translation column
        if (historyId.value !== null) {
          payload.history_id = historyId.value;
        }

        console.log("Export native payload:", payload);
        
        const res = await fetch("/api/export/native", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        
        if (!res.ok) {
          const errData = await res.json().catch(() => ({ detail: "Export failed" }));
          console.error("Export native failed:", errData);
          error.value = `Download failed: ${errData.detail || "Unknown error"}`;
        }
        return;
      }
    }

    // Fallback: browser download (when native dialog API itself fails)
    const res = await fetch("/api/export", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        translated_text: translatedContent.value,
        original_file_type: `.${selectedFile.value.name.split(".").pop()}`,
        file_name: `translated_${selectedFile.value.name.split(".")[0]}`,
      }),
    });

    if (res.ok) {
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      let filename = `translated_${selectedFile.value.name}`;
      const cd = res.headers.get("content-disposition");
      if (cd && cd.includes("filename=")) {
        filename = cd.split("filename=")[1].replace(/"/g, "");
      }
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      a.remove();
    }
  } catch (e) {
    console.error("Export failed", e);
  }
};
</script>

<template>
  <div class="h-[calc(100vh-8rem)] flex flex-col gap-6">
    <!-- Split view when file selected, otherwise full dropzone -->
    <div
      v-if="!selectedFile"
      class="flex-1 flex flex-col items-center justify-center p-8 glass-card border-2 border-dashed border-slate-300 dark:border-slate-700 hover:border-indigo-400 dark:hover:border-indigo-500 hover:bg-indigo-50/30 dark:hover:bg-indigo-900/10 transition-colors"
      @dragover.prevent
      @drop="handleDrop"
      @click="triggerFileInput"
    >
      <div
        class="w-20 h-20 rounded-full bg-indigo-100 dark:bg-indigo-900/40 flex items-center justify-center mb-6"
      >
        <UploadCloud class="w-10 h-10 text-indigo-600 dark:text-indigo-400" />
      </div>
      <h2 class="text-2xl font-bold text-slate-800 dark:text-white mb-2">
        {{ t("file.dropzoneTitle") }}
      </h2>
      <p class="text-slate-500 dark:text-slate-400 mb-8 max-w-md text-center">
        {{ t("file.dropzoneSubtitle") }}
      </p>

      <div
        class="text-sm font-medium text-slate-400 text-center px-4 py-2 bg-slate-100 dark:bg-slate-800/50 rounded-lg"
      >
        {{ t("file.supportedFormats") }}
      </div>
      <input
        type="file"
        class="hidden"
        ref="fileInput"
        @change="handleFileSelect"
        accept=".pdf,.png,.jpg,.jpeg,.md,.txt,.xlsx,.csv,.docx"
      />
    </div>

    <div v-else class="flex-1 flex flex-col min-h-0">
      <div
        class="flex items-center justify-between p-4 glass-card mb-4 flex-shrink-0 border-l-4 border-l-indigo-500"
      >
        <div class="flex items-center gap-4">
          <div class="p-3 bg-slate-100 dark:bg-slate-800 rounded-lg">
            <FileText class="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
          </div>
          <div>
            <h3 class="text-lg font-medium text-slate-700 dark:text-slate-200">
              {{ selectedFile?.name || 'File Selected' }}
            </h3>
            <p class="text-sm text-slate-500 dark:text-slate-400">
              Selected for translation
            </p>
          </div>
        </div>

        <div class="flex items-center gap-3">
          <!-- Language selectors -->
          <div class="flex items-center gap-2">
            <div class="flex flex-col gap-1">
              <select v-model="sourceLang" class="input-field max-w-[130px] py-1 text-xs">
                <option v-for="l in langOptions" :key="l.value" :value="l.value">{{ l.label }}</option>
              </select>
              <input v-if="sourceLang === 'custom'" v-model="customSourceLang" type="text" placeholder="e.g. Español" class="input-field max-w-[130px] py-0.5 text-xs" />
            </div>
            <span class="text-slate-400 text-sm">&rarr;</span>
            <div class="flex flex-col gap-1">
              <select v-model="targetLang" class="input-field max-w-[130px] py-1 text-xs font-medium text-indigo-600 dark:text-indigo-400">
                <option v-for="l in targetLangOptions" :key="l.value" :value="l.value">{{ l.label }}</option>
              </select>
              <input v-if="targetLang === 'custom'" v-model="customTargetLang" type="text" placeholder="e.g. 日本語" class="input-field max-w-[130px] py-0.5 text-xs" />
            </div>
          </div>

          <!-- Live status -->
          <div
            v-if="isTranslating"
            class="flex items-center gap-2 text-xs text-slate-500 font-mono"
          >
            <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            🤖 {{ activeModel }} ⏱️ {{ elapsedSeconds.toFixed(1) }}s
          </div>

          <!-- Abort button -->
          <button
            v-if="isTranslating"
            class="btn bg-rose-600 hover:bg-rose-700 text-white shadow-md shadow-rose-500/20"
            @click="handleAbort"
          >
            <Square class="w-4 h-4 mr-1 fill-current" />
            Stop
          </button>

          <button
            v-if="!isTranslating && !translatedContent"
            class="btn-primary"
            @click="startTranslation"
            :disabled="isValidatingLang"
          >
            <Loader2 v-if="isValidatingLang" class="w-4 h-4 mr-1 animate-spin" />
            <Play v-else class="w-4 h-4 mr-1 fill-current" />
            {{ isValidatingLang ? 'Validating…' : t("common.translate") }}
          </button>

          <button
            v-if="translatedContent"
            class="btn bg-emerald-600 hover:bg-emerald-700 text-white"
            @click="downloadExport"
          >
            <Download class="w-4 h-4 mr-2" />
            {{ t("common.download") }}
          </button>

          <button
            class="btn-icon bg-slate-200 dark:bg-slate-800 hover:bg-rose-100 dark:hover:bg-rose-900/30 text-rose-600 dark:text-rose-400"
            @click="removeFile"
            :disabled="isTranslating"
          >
            <X class="w-5 h-5" />
          </button>
        </div>
      </div>

      <div
        v-if="error"
        class="mb-4 p-4 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 flex items-center gap-2"
      >
        <AlertCircle class="w-5 h-5" />
        {{ error }}
      </div>

      <!-- Language validation indicator -->
      <div
        v-if="isValidatingLang"
        class="mb-4 p-3 rounded-lg bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800/30 flex items-center gap-3 text-amber-700 dark:text-amber-400 text-sm font-medium"
      >
        <Loader2 class="w-4 h-4 animate-spin" />
        <span>Validating language name with AI…</span>
      </div>

      <div
        v-if="isTranslating || translatedContent || sourceContent"
        class="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-6 min-h-0"
      >
         <!-- source pane -->
         <div class="glass-card flex flex-col overflow-hidden focus-within:ring-2 focus-within:ring-indigo-500/50">
            <div class="px-4 py-2 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50 flex items-center justify-between">
              <span class="text-xs font-bold uppercase tracking-wider text-slate-500">Source Document</span>
              <span v-if="!sourceContent && isTranslating" class="text-xs text-indigo-500 flex items-center gap-1"><Loader2 class="w-3 h-3 animate-spin"/> Extracting Text...</span>
            </div>
            <textarea readonly class="flex-1 w-full p-4 md:p-6 bg-transparent resize-none focus:outline-none text-slate-800 dark:text-slate-200 font-mono text-sm leading-relaxed" v-model="sourceContent"></textarea>
         </div>

         <!-- translation pane -->
         <div class="glass-card flex flex-col overflow-hidden relative bg-slate-50/50 dark:bg-[#0B1120]/50">
            <div class="px-4 py-2 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50 flex justify-between items-center">
              <span class="text-xs font-bold uppercase tracking-wider text-slate-500">Translation Preview</span>
              <span v-if="isTranslating && sourceContent" class="text-xs text-emerald-500 font-medium flex items-center gap-1"><Loader2 class="w-3.5 h-3.5 animate-spin"/> Translating...</span>
            </div>
            
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

            <textarea readonly class="flex-1 w-full p-4 md:p-6 bg-transparent resize-none focus:outline-none text-slate-800 dark:text-slate-200 font-mono text-sm leading-relaxed" v-model="translatedContent"></textarea>

            <div
              v-if="report"
              class="px-4 py-3 bg-indigo-50 dark:bg-indigo-900/20 border-t border-indigo-100 dark:border-indigo-800/50 flex items-center gap-4 text-xs font-medium text-indigo-700 dark:text-indigo-300"
            >
              <span>🤖 {{ report.model_used }}</span>
              <span>⏱️ {{ (report.time_taken_ms / 1000).toFixed(1) }}s</span>
              <span>⚡ {{ report.tokens_per_second.toFixed(1) }} t/s</span>
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

      <div
        v-else
        class="flex-1 glass-card bg-slate-50/50 dark:bg-slate-900/10 border-dashed border-2 flex items-center justify-center"
      >
        <span class="text-slate-400 font-medium"
          >Click Translate to begin processing document</span
        >
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
              >{{ suggestion }}</button>
            </div>
          </div>
          <div class="space-y-2">
            <label class="text-xs font-medium text-slate-500 dark:text-slate-400">Revised language name:</label>
            <input v-model="langValidationInput" type="text" class="input-field w-full" placeholder="Type corrected language name…" @keyup.enter="handleLangValidationRetry" />
          </div>
          <div class="flex justify-end gap-3">
            <button @click="showLangValidationModal = false" class="btn-secondary text-sm">Cancel</button>
            <button @click="handleLangValidationRetry" :disabled="!langValidationInput.trim() || isValidatingLang" class="btn-primary text-sm">
              <Loader2 v-if="isValidatingLang" class="w-3.5 h-3.5 mr-1 animate-spin" />
              Retry
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
