<script setup lang="ts">
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import {
  UploadCloud,
  FileText,
  Download,
  Loader2,
  X,
  AlertCircle,
  Square,
} from "lucide-vue-next";
import { useSettingsStore } from "@/stores/settings";
import ModelMissingModal from "@/components/common/ModelMissingModal.vue";

const { t } = useI18n();
const settings = useSettingsStore();

const fileInput = ref<HTMLInputElement | null>(null);
const selectedFile = ref<File | null>(null);
const isTranslating = ref(false);
const translatedContent = ref("");
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
  thinkingText.value = "";
  report.value = null;
};

const removeFile = () => {
  selectedFile.value = null;
  translatedContent.value = "";
  thinkingText.value = "";
  report.value = null;
  chunkProgress.value = "";
  if (fileInput.value) fileInput.value.value = "";
};

const handleAbort = () => {
  abortController.value?.abort();
};

const startTranslation = async () => {
  if (!selectedFile.value) return;

  isTranslating.value = true;
  error.value = "";
  report.value = null;
  translatedContent.value = "";
  thinkingText.value = "";
  isThinkingExpanded.value = false;
  activeModel.value = settings.defaultModel;
  chunkProgress.value = "";
  startTimer();

  // First extract the file text via the existing /api/translate/file endpoint (non-streaming)
  // OR we can read the file on the client and stream the text.
  // For simplicity, let's extract text via the file endpoint first, then stream translate.

  const formData = new FormData();
  formData.append("file", selectedFile.value);
  formData.append("source_language", settings.defaultSourceLang);
  formData.append("target_language", settings.defaultTargetLang);
  formData.append("model", settings.defaultModel);

  // Use the non-streaming endpoint for file translation (handles file extraction + translation)
  // but we'll switch to using streaming for text part if possible.
  // For now, keep non-streaming for file translation but add abort + progress UI.

  abortController.value = new AbortController();

  try {
    const res = await fetch("/api/translate/file", {
      method: "POST",
      body: formData,
      signal: abortController.value.signal,
    });

    if (res.ok) {
      const data = await res.json();
      translatedContent.value = data.translated_text;
      report.value = data.report;
    } else {
      const e = await res.json();
      if (res.status === 404 && e.detail === "model_not_found") {
        missingModelName.value = settings.defaultModel;
        showModelMissingModal.value = true;
        error.value = `Model '${settings.defaultModel}' not found. Please download it via the prompt.`;
      } else {
        error.value = e.detail || "Translation failed";
      }
    }
  } catch (e: any) {
    if (e.name === "AbortError") {
      // User aborted
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
      @click="() => fileInput?.click()"
    >
      <div
        class="w-20 h-20 rounded-full bg-indigo-100 dark:bg-indigo-900/40 flex items-center justify-center mb-6"
      >
        <UploadCloud class="w-10 h-10 text-indigo-600 dark:text-indigo-400" />
      </div>
      <h2 class="text-2xl font-bold text-slate-800 dark:text-white mb-2">
        {{ t("file.dropzoneTitle") }}
      </h2>
      <p class="text-slate-500 dark:text-slate-400 mb-8">
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
            <h3 class="font-bold text-slate-900 dark:text-white">
              {{ selectedFile.name }}
            </h3>
            <p class="text-sm text-slate-500">
              {{ (selectedFile.size / 1024).toFixed(1) }} KB
            </p>
          </div>
        </div>

        <div class="flex items-center gap-3">
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
          >
            {{ t("common.translate") }}
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

      <div
        v-if="isTranslating"
        class="flex-1 flex flex-col items-center justify-center p-8 glass-card"
      >
        <Loader2 class="w-12 h-12 text-indigo-600 animate-spin mb-4" />
        <h3 class="text-lg font-bold text-slate-800 dark:text-white">
          Analyzing & Translating Document
        </h3>
        <p class="text-slate-500 mt-2">
          🤖 {{ activeModel }} &nbsp; ⏱️ {{ elapsedSeconds.toFixed(1) }}s
        </p>
        <p class="text-xs text-slate-400 mt-1">
          Click "Stop" to abort at any time
        </p>
      </div>

      <!-- Result Preview -->
      <div
        v-else-if="translatedContent"
        class="flex-1 flex flex-col overflow-hidden glass-card p-0"
      >
        <div
          class="flex items-center px-4 py-2 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50"
        >
          <span
            class="text-xs font-bold uppercase tracking-wider text-slate-500"
            >Preview</span
          >
        </div>
        <textarea
          readonly
          class="flex-1 w-full p-6 bg-transparent resize-none focus:outline-none text-slate-800 dark:text-slate-200 font-mono text-sm leading-relaxed"
          v-model="translatedContent"
        ></textarea>

        <!-- Report bar -->
        <div
          v-if="report"
          class="px-4 py-3 bg-indigo-50 dark:bg-indigo-900/20 border-t border-indigo-100 dark:border-indigo-800/50 flex items-center gap-4 text-xs font-medium text-indigo-700 dark:text-indigo-300"
        >
          <span>🤖 {{ report.model_used }}</span>
          <span>⏱️ {{ (report.time_taken_ms / 1000).toFixed(1) }}s</span>
          <span>⚡ {{ report.tokens_per_second.toFixed(1) }} t/s</span>
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
  </div>
</template>
