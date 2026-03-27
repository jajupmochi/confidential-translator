<script setup lang="ts">
import { ref, onMounted, onActivated } from "vue";
import { useI18n } from "vue-i18n";
import { Languages, FileText, Trash2, Search, Filter, Copy, Check } from "lucide-vue-next";

const { t } = useI18n();

const history = ref<any[]>([]);
const loading = ref(true);
const page = ref(1);
const total = ref(0);
const searchQuery = ref("");
const totalPages = ref(1);
const selectedType = ref("all");
const copiedId = ref<string | null>(null);

const copyText = async (text: string, id: string) => {
  try {
    await navigator.clipboard.writeText(text);
    copiedId.value = id;
    setTimeout(() => {
      copiedId.value = null;
    }, 2000);
  } catch (err) {
    console.error('Failed to copy text: ', err);
  }
};

const isAbsolutePath = (path: string) => path && (path.includes('/') || path.includes('\\'));

const openNativeFolder = async (path: string) => {
  try {
    const res = await fetch("/api/system/open-folder", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ file_path: path })
    });
    if (!res.ok) {
      const data = await res.json();
      alert("Failed to open file: " + (data.detail || "Unknown error"));
    }
  } catch (e) {
    console.error(e);
    alert("Connection error when opening file.");
  }
};

const buildTooltip = (...parts: string[]) => parts.join('\n\n');

async function fetchHistory(p = 1) {
  loading.value = true;
  try {
    const url = new URL("/api/history", window.location.origin);
    url.searchParams.append("page", p.toString());
    url.searchParams.append("page_size", "20");
    if (searchQuery.value) url.searchParams.append("search", searchQuery.value);
    if (selectedType.value !== "all")
      url.searchParams.append("translation_type", selectedType.value);

    const res = await fetch(url.toString());
    if (res.ok) {
      const data = await res.json();
      history.value = data.records;
      total.value = data.total;
      page.value = data.page;
      totalPages.value = Math.ceil(data.total / data.page_size);
    }
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
}

async function deleteRecord(id: number) {
  if (!confirm(t("history.deleteConfirm"))) return;
  try {
    const res = await fetch(`/api/history/${id}`, { method: "DELETE" });
    if (res.ok) {
      await fetchHistory(page.value);
    }
  } catch (e) {
    console.error(e);
  }
}

onMounted(() => fetchHistory());
onActivated(() => fetchHistory());

const formatDate = (ds: string) => {
  return new Date(ds).toLocaleString();
};
</script>

<template>
  <div class="space-y-6">
    <div
      class="glass-card p-6 flex flex-col md:flex-row gap-4 justify-between items-center"
    >
      <h1
        class="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-slate-900 to-slate-500 dark:from-white dark:to-slate-400"
      >
        {{ t("history.title") }}
      </h1>

      <div class="flex items-center gap-3 w-full md:w-auto">
        <div class="relative flex-1 md:w-64">
          <Search
            class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400"
          />
          <input
            v-model="searchQuery"
            @keyup.enter="fetchHistory(1)"
            type="text"
            :placeholder="t('history.searchPlaceholder')"
            class="input-field pl-9 w-full"
          />
        </div>

        <select
          v-model="selectedType"
          @change="fetchHistory(1)"
          class="input-field w-32 hidden md:block"
        >
          <option value="all">{{ t("common.all") }}</option>
          <option value="text">{{ t("common.text") }}</option>
          <option value="file">{{ t("common.file") }}</option>
        </select>

        <button @click="fetchHistory(1)" class="btn-secondary h-[42px]">
          <Filter class="w-4 h-4" />
        </button>
      </div>
    </div>

    <div class="glass-card overflow-hidden">
      <div v-if="loading" class="p-12 flex justify-center">
        <div
          class="w-8 h-8 rounded-full border-2 border-indigo-600 border-t-transparent animate-spin"
        ></div>
      </div>

      <div
        v-else-if="history.length === 0"
        class="p-12 text-center text-slate-500"
      >
        {{ t("history.noHistory") }}
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full text-left text-sm whitespace-nowrap">
          <thead
            class="bg-slate-50 dark:bg-slate-900/50 text-slate-500 dark:text-slate-400 border-b border-slate-200 dark:border-slate-800"
          >
            <tr>
              <th class="px-6 py-4 font-medium">{{ t("history.columns.type") }}</th>
              <th class="px-6 py-4 font-medium">{{ t("history.columns.source") }}</th>
              <th class="px-6 py-4 font-medium">{{ t("history.columns.translation") }}</th>
              <th class="px-6 py-4 font-medium">{{ t("history.columns.model") }}</th>
              <th class="px-6 py-4 font-medium">{{ t("history.columns.date") }}</th>
              <th class="px-6 py-4 font-medium text-right">{{ t("history.columns.actions") }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 dark:divide-slate-800">
            <tr
              v-for="item in history"
              :key="item.id"
              class="hover:bg-slate-50/50 dark:hover:bg-slate-800/20 group"
            >
              <td class="px-6 py-4">
                <span
                  class="inline-flex items-center gap-1.5 px-2 py-1 rounded border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-xs font-medium text-slate-600 dark:text-slate-300"
                >
                  <Languages
                    v-if="item.translation_type === 'text'"
                    class="w-3.5 h-3.5 text-indigo-500"
                  />
                  <FileText v-else class="w-3.5 h-3.5 text-emerald-500" />
                  {{ item.translation_type }}
                </span>
                <div class="mt-1 text-xs text-slate-400 font-mono">
                  {{ item.source_language }} &rarr; {{ item.target_language }}
                </div>
              </td>
              <td class="px-6 py-4 max-w-[200px] text-slate-600 dark:text-slate-300">
                <div 
                  class="flex items-start justify-between group/text border border-transparent hover:border-slate-200 dark:hover:border-slate-700 p-1 -m-1 rounded transition-colors cursor-pointer" 
                  @click="copyText(item.source_text, 'src-' + item.id)"
                  :title="buildTooltip('Click to copy source text:', item.source_text)"
                >
                  <div class="truncate mr-2 w-full text-ellipsis overflow-hidden">
                    <span
                      v-if="item.file_name"
                      class="text-xs font-medium px-1.5 py-0.5 bg-slate-100 dark:bg-slate-800 rounded mr-2"
                      :class="{'hover:bg-indigo-100 dark:hover:bg-indigo-900/50 cursor-pointer border border-indigo-200 dark:border-indigo-800/50 text-indigo-700 dark:text-indigo-300': isAbsolutePath(item.file_name)}"
                      @click.stop="isAbsolutePath(item.file_name) && openNativeFolder(item.file_name)"
                      :title="isAbsolutePath(item.file_name) ? buildTooltip(item.file_name, item.source_text.substring(0, 800)) : buildTooltip('Browser upload (no path available)', item.source_text.substring(0, 800))"
                    >{{ isAbsolutePath(item.file_name) ? '📁 ' + item.file_name.split(/[/\\]/).pop() : item.file_name }}</span>
                    {{ item.source_text }}
                  </div>
                  <button class="opacity-0 group-hover/text:opacity-100 flex-shrink-0 transition-opacity text-slate-400 hover:text-indigo-500">
                    <Check v-if="copiedId === 'src-' + item.id" class="w-3.5 h-3.5 text-emerald-500" />
                    <Copy v-else class="w-3.5 h-3.5" />
                  </button>
                </div>
              </td>
              <td class="px-6 py-4 max-w-[250px] text-slate-800 dark:text-slate-200 font-medium">
                <div 
                  class="flex items-start justify-between group/text border border-transparent hover:border-slate-200 dark:hover:border-slate-700 p-1 -m-1 rounded transition-colors cursor-pointer" 
                  @click="copyText(item.translated_text, 'tgt-' + item.id)"
                  :title="buildTooltip('Click to copy translation:', item.translated_text)"
                >
                  <div class="truncate mr-2 w-full text-ellipsis overflow-hidden">
                    <span
                      v-if="item.target_file_name && item.translation_type === 'file'"
                      class="text-xs font-medium px-1.5 py-0.5 bg-slate-100 dark:bg-slate-800 rounded mr-2 hover:bg-emerald-100 dark:hover:bg-emerald-900/50 cursor-pointer border border-emerald-200 dark:border-emerald-800/50 text-emerald-700 dark:text-emerald-300"
                      @click.stop="openNativeFolder(item.target_file_name)"
                      :title="buildTooltip(item.target_file_name, item.translated_text.substring(0, 800))"
                    >📁 {{ item.target_file_name.split(/[/\\]/).pop() }}</span>
                    {{ item.translated_text }}
                  </div>
                  <button class="opacity-0 group-hover/text:opacity-100 flex-shrink-0 transition-opacity text-slate-400 hover:text-indigo-500">
                    <Check v-if="copiedId === 'tgt-' + item.id" class="w-3.5 h-3.5 text-emerald-500" />
                    <Copy v-else class="w-3.5 h-3.5" />
                  </button>
                </div>
              </td>
              <td
                class="px-6 py-4 text-xs font-mono text-slate-500 dark:text-slate-400"
              >
                {{ item.model_used }}
                <div class="mt-1 opacity-70">
                  {{ item.tokens_per_second.toFixed(1) }} t/s
                </div>
              </td>
              <td class="px-6 py-4 text-xs text-slate-500 dark:text-slate-400">
                {{ formatDate(item.created_at) }}
              </td>
              <td class="px-6 py-4 text-right">
                <button
                  @click="deleteRecord(item.id)"
                  class="btn-icon text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-500/10 opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <Trash2 class="w-4 h-4" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div
        v-if="totalPages > 1"
        class="px-6 py-4 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between"
      >
        <span class="text-sm text-slate-500"
          >Showing page {{ page }} of {{ totalPages }} ({{ total }} total)</span
        >
        <div class="flex gap-2">
          <button
            @click="fetchHistory(page - 1)"
            :disabled="page <= 1"
            class="btn-secondary px-3 py-1.5 text-sm"
          >
            {{ t("common.previous") }}
          </button>
          <button
            @click="fetchHistory(page + 1)"
            :disabled="page >= totalPages"
            class="btn-secondary px-3 py-1.5 text-sm"
          >
            {{ t("common.next") }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
