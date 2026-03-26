<script setup lang="ts">
import { ref, onMounted } from "vue";
import { Languages, FileText, Trash2, Search, Filter } from "lucide-vue-next";

const history = ref<any[]>([]);
const loading = ref(true);
const page = ref(1);
const total = ref(0);
const searchQuery = ref("");
const totalPages = ref(1);
const selectedType = ref("all");

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
  if (!confirm("Are you sure you want to delete this record?")) return;
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
        Translation History
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
            placeholder="Search translations..."
            class="input-field pl-9 w-full"
          />
        </div>

        <select
          v-model="selectedType"
          @change="fetchHistory(1)"
          class="input-field w-32 hidden md:block"
        >
          <option value="all">All Types</option>
          <option value="text">Text only</option>
          <option value="file">Files only</option>
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
        No history records found.
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full text-left text-sm whitespace-nowrap">
          <thead
            class="bg-slate-50 dark:bg-slate-900/50 text-slate-500 dark:text-slate-400 border-b border-slate-200 dark:border-slate-800"
          >
            <tr>
              <th class="px-6 py-4 font-medium">Type</th>
              <th class="px-6 py-4 font-medium">Source</th>
              <th class="px-6 py-4 font-medium">Translation</th>
              <th class="px-6 py-4 font-medium">Model</th>
              <th class="px-6 py-4 font-medium">Date</th>
              <th class="px-6 py-4 font-medium text-right">Actions</th>
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
              <td
                class="px-6 py-4 max-w-[200px] truncate text-slate-600 dark:text-slate-300"
                :title="item.source_text"
              >
                <span
                  v-if="item.file_name"
                  class="text-xs font-medium px-1.5 py-0.5 bg-slate-100 dark:bg-slate-800 rounded mr-2"
                  >{{ item.file_name }}</span
                >
                {{ item.source_text }}
              </td>
              <td
                class="px-6 py-4 max-w-[250px] truncate text-slate-800 dark:text-slate-200 font-medium"
                :title="item.translated_text"
              >
                {{ item.translated_text }}
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
            Prev
          </button>
          <button
            @click="fetchHistory(page + 1)"
            :disabled="page >= totalPages"
            class="btn-secondary px-3 py-1.5 text-sm"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
