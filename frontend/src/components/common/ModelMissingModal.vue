<script setup lang="ts">
import { Download, AlertCircle } from "lucide-vue-next";
import { useOllamaStore } from "@/stores/ollama";

const props = defineProps<{
  show: boolean;
  modelName: string;
}>();

const emit = defineEmits<{
  (e: "update:show", value: boolean): void;
}>();

const ollamaStore = useOllamaStore();

async function quickPullModel() {
  emit("update:show", false);
  if (!props.modelName) return;
  ollamaStore.pullModel(props.modelName);
  // Toast or something could be nice, but pullModel will show in ModelsView and in background
}
</script>

<template>
  <div
    v-if="show"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm"
  >
    <div
      class="glass-card max-w-md w-full p-6 space-y-4 shadow-xl border border-rose-200 dark:border-rose-800/50"
    >
      <h3
        class="text-xl font-bold flex items-center gap-2 text-rose-600 dark:text-rose-400"
      >
        <AlertCircle class="w-6 h-6" /> Model Required
      </h3>
      <p class="text-slate-600 dark:text-slate-300">
        The model <strong>{{ modelName }}</strong
        > is not installed locally or could not be found. Would you like to
        download it now? (You can check progress in the Models tab).
      </p>
      <div class="flex justify-end gap-3 mt-6">
        <button
          class="btn bg-slate-200 hover:bg-slate-300 text-slate-700 dark:bg-slate-800 dark:hover:bg-slate-700 dark:text-slate-300"
          @click="emit('update:show', false)"
        >
          Cancel
        </button>
        <button class="btn-primary flex items-center gap-2" @click="quickPullModel">
          <Download class="w-4 h-4" /> Download Model
        </button>
      </div>
    </div>
  </div>
</template>
