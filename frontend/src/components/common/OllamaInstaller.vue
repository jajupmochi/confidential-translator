<script setup lang="ts">
import { useOllamaStore } from "@/stores/ollama";
import { 
  Download, 
  CheckCircle2, 
  Loader2,
  XCircle,
  HardDrive
} from "lucide-vue-next";

const ollamaStore = useOllamaStore();

const install = () => {
  ollamaStore.installOllama();
};
</script>

<template>
  <Transition name="fade">
    <div 
      v-if="!ollamaStore.isInstalled || (ollamaStore.isInstalling)"
      class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm"
    >
      <div class="glass-card max-w-lg w-full p-8 shadow-2xl border-indigo-500/20">
        <div class="text-center space-y-4">
          <div class="inline-flex p-4 rounded-full bg-indigo-100 dark:bg-indigo-900/40 text-indigo-600 dark:text-indigo-400">
            <Download v-if="!ollamaStore.isInstalling" class="w-10 h-10" />
            <Loader2 v-else class="w-10 h-10 animate-spin" />
          </div>
          
          <h2 class="text-2xl font-bold text-slate-900 dark:text-white">
            {{ ollamaStore.isInstalling ? 'Installing Ollama...' : 'Ollama Required' }}
          </h2>
          
          <p class="text-slate-600 dark:text-slate-300">
            To provide 100% offline and secure translations, this application uses the **Ollama** engine.
          </p>

          <div v-if="!ollamaStore.isInstalling" class="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl text-left border border-slate-200 dark:border-slate-700">
            <div class="flex items-start gap-3 mb-2">
              <HardDrive class="w-5 h-5 text-slate-400 shrink-0 mt-0.5" />
              <div>
                <div class="text-sm font-semibold text-slate-900 dark:text-white">Space Required</div>
                <div class="text-xs text-slate-500">Approx. 600MB for engine + 2-8GB for models.</div>
              </div>
            </div>
            <div class="flex items-start gap-3">
              <CheckCircle2 class="w-5 h-5 text-emerald-500 shrink-0 mt-0.5" />
              <div class="text-xs text-slate-500">
                Installation will be handled automatically. You may be prompted for your system password.
              </div>
            </div>
          </div>

          <!-- Progress -->
          <div v-if="ollamaStore.isInstalling" class="space-y-3">
            <div class="h-2 w-full bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
              <div 
                class="h-full bg-indigo-500 transition-all duration-300" 
                :style="{ width: ollamaStore.installProgress.percent + '%' }"
              ></div>
            </div>
            <div class="text-sm font-medium text-indigo-600 dark:text-indigo-400">
              {{ ollamaStore.installProgress.message }}
            </div>
          </div>

          <!-- Error -->
          <div v-if="ollamaStore.installProgress.status === 'error'" class="p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 text-sm flex items-center gap-2 text-left">
            <XCircle class="w-5 h-5 shrink-0" />
            {{ ollamaStore.installProgress.message }}
          </div>

          <div class="pt-4 flex flex-col gap-2">
            <button 
              v-if="!ollamaStore.isInstalling"
              @click="install"
              class="btn-primary w-full py-3"
            >
              Confirm and Install
            </button>
            <p v-if="!ollamaStore.isInstalling" class="text-[10px] text-slate-400 uppercase tracking-wider font-bold">
              Available for Ubuntu / Linux
            </p>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
