<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import { Plus, Trash2, Upload, BookOpen } from "lucide-vue-next";

const { t } = useI18n();

interface GlossaryEntry {
  id: number;
  source_term: string;
  target_term: string;
}

interface Glossary {
  id: number;
  name: string;
  source_language: string;
  target_language: string;
  created_at: string;
  entry_count: number;
}

const glossaries = ref<Glossary[]>([]);
const expandedId = ref<number | null>(null);
const entries = ref<Record<number, GlossaryEntry[]>>({});
const loading = ref(false);

// New glossary form
const showNewForm = ref(false);
const newName = ref("");
const newSourceLang = ref("en");
const newTargetLang = ref("zh");

// New entry form
const newSourceTerm = ref("");
const newTargetTerm = ref("");

const langOptions = [
  { value: "en", label: "English" },
  { value: "zh", label: "Chinese" },
  { value: "de", label: "German" },
  { value: "fr", label: "French" },
];

async function fetchGlossaries() {
  loading.value = true;
  try {
    const res = await fetch("/api/glossaries");
    if (res.ok) {
      const data = await res.json();
      glossaries.value = data.glossaries;
    }
  } finally {
    loading.value = false;
  }
}

async function createGlossary() {
  if (!newName.value.trim()) return;
  await fetch("/api/glossaries", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name: newName.value,
      source_language: newSourceLang.value,
      target_language: newTargetLang.value,
    }),
  });
  newName.value = "";
  showNewForm.value = false;
  await fetchGlossaries();
}

async function deleteGlossary(id: number) {
  await fetch(`/api/glossaries/${id}`, { method: "DELETE" });
  if (expandedId.value === id) expandedId.value = null;
  await fetchGlossaries();
}

async function toggleExpand(id: number) {
  if (expandedId.value === id) {
    expandedId.value = null;
    return;
  }
  expandedId.value = id;
  await fetchEntries(id);
}

async function fetchEntries(glossaryId: number) {
  const res = await fetch(`/api/glossaries/${glossaryId}/entries`);
  if (res.ok) {
    entries.value[glossaryId] = await res.json();
  }
}

async function addEntry(glossaryId: number) {
  if (!newSourceTerm.value.trim() || !newTargetTerm.value.trim()) return;
  await fetch(`/api/glossaries/${glossaryId}/entries`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      source_term: newSourceTerm.value,
      target_term: newTargetTerm.value,
    }),
  });
  newSourceTerm.value = "";
  newTargetTerm.value = "";
  await fetchEntries(glossaryId);
  await fetchGlossaries(); // update count
}

async function deleteEntry(glossaryId: number, entryId: number) {
  await fetch(`/api/glossaries/${glossaryId}/entries/${entryId}`, {
    method: "DELETE",
  });
  await fetchEntries(glossaryId);
  await fetchGlossaries();
}

async function handleUpload(glossaryId: number, event: Event) {
  const input = event.target as HTMLInputElement;
  if (!input.files?.length) return;
  const file = input.files[0];
  const formData = new FormData();
  formData.append("file", file);
  await fetch(`/api/glossaries/${glossaryId}/upload`, {
    method: "POST",
    body: formData,
  });
  input.value = "";
  await fetchEntries(glossaryId);
  await fetchGlossaries();
}

function getLangLabel(code: string) {
  return langOptions.find((l) => l.value === code)?.label || code;
}

onMounted(fetchGlossaries);
</script>

<template>
  <div class="space-y-6 max-w-4xl">
    <div class="glass-card p-6">
      <div class="flex items-center justify-between mb-6">
        <div>
          <h1
            class="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-slate-900 to-slate-500 dark:from-white dark:to-slate-400"
          >
            📖 {{ t("glossary.title") }}
          </h1>
          <p class="text-sm text-slate-500 mt-1">
            {{ t("glossary.subtitle") }}
          </p>
        </div>
        <button
          @click="showNewForm = !showNewForm"
          class="btn-primary"
        >
          <Plus class="w-4 h-4 mr-1" />
          {{ t("glossary.newGlossary") }}
        </button>
      </div>

      <!-- New glossary form -->
      <div
        v-if="showNewForm"
        class="mb-6 p-4 rounded-lg bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-200 dark:border-indigo-800/30 space-y-3"
      >
        <input
          v-model="newName"
          type="text"
          :placeholder="t('glossary.namePlaceholder')"
          class="input-field w-full"
        />
        <div class="flex items-center gap-3">
          <select v-model="newSourceLang" class="input-field">
            <option v-for="l in langOptions" :key="l.value" :value="l.value">
              {{ l.label }}
            </option>
          </select>
          <span class="text-slate-400 font-bold">&rarr;</span>
          <select v-model="newTargetLang" class="input-field">
            <option v-for="l in langOptions" :key="l.value" :value="l.value">
              {{ l.label }}
            </option>
          </select>
          <button @click="createGlossary" class="btn-primary text-sm">
            {{ t("common.create") }}
          </button>
        </div>
      </div>

      <!-- Empty state -->
      <div
        v-if="!loading && glossaries.length === 0"
        class="flex flex-col items-center justify-center py-16 text-slate-400"
      >
        <BookOpen class="w-16 h-16 mb-4 text-slate-300 dark:text-slate-600" />
        <p class="text-lg font-medium">No glossaries yet</p>
        <p class="text-sm mt-1">
          Create a glossary to ensure consistent translations of domain-specific
          terms.
        </p>
      </div>

      <!-- Glossary list -->
      <div class="space-y-4">
        <div
          v-for="g in glossaries"
          :key="g.id"
          class="border border-slate-200 dark:border-slate-700 rounded-lg overflow-hidden"
        >
          <!-- Glossary header -->
          <div
            @click="toggleExpand(g.id)"
            class="flex items-center justify-between p-4 cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors"
          >
            <div class="flex items-center gap-3">
              <BookOpen class="w-5 h-5 text-indigo-500" />
              <div>
                <h3
                  class="font-bold text-slate-900 dark:text-white"
                >
                  {{ g.name }}
                </h3>
                <p class="text-xs text-slate-500">
                  {{ getLangLabel(g.source_language) }} →
                  {{ getLangLabel(g.target_language) }}
                  &nbsp;·&nbsp; {{ g.entry_count }} {{ t("common.terms") }}
                </p>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <label
                class="btn text-xs bg-slate-100 dark:bg-slate-800 hover:bg-indigo-100 dark:hover:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 cursor-pointer"
                @click.stop
              >
                <Upload class="w-3.5 h-3.5 mr-1" />
                CSV/TSV
                <input
                  type="file"
                  class="hidden"
                  accept=".csv,.tsv"
                  @change="handleUpload(g.id, $event)"
                />
              </label>
              <button
                @click.stop="deleteGlossary(g.id)"
                class="btn-icon text-rose-500 hover:bg-rose-100 dark:hover:bg-rose-900/20"
              >
                <Trash2 class="w-4 h-4" />
              </button>
            </div>
          </div>

          <!-- Expanded entries -->
          <div
            v-if="expandedId === g.id"
            class="border-t border-slate-200 dark:border-slate-700 bg-slate-50/50 dark:bg-slate-900/30 p-4"
          >
            <!-- Entry list -->
            <div class="space-y-1 mb-4 max-h-[300px] overflow-y-auto">
              <div
                v-for="e in entries[g.id] || []"
                :key="e.id"
                class="flex items-center justify-between py-1.5 px-3 rounded hover:bg-white dark:hover:bg-slate-800/50 group text-sm"
              >
                <div class="flex items-center gap-3 font-mono">
                  <span class="text-slate-800 dark:text-slate-200">{{
                    e.source_term
                  }}</span>
                  <span class="text-slate-400">→</span>
                  <span
                    class="text-indigo-600 dark:text-indigo-400 font-medium"
                    >{{ e.target_term }}</span
                  >
                </div>
                <button
                  @click="deleteEntry(g.id, e.id)"
                  class="opacity-0 group-hover:opacity-100 transition-opacity text-rose-400 hover:text-rose-600"
                >
                  <Trash2 class="w-3.5 h-3.5" />
                </button>
              </div>
              <p
                v-if="!entries[g.id]?.length"
                class="text-xs text-slate-400 text-center py-4"
              >
                {{ t("glossary.noEntries") }}
              </p>
            </div>

            <!-- Add entry form -->
            <div
              class="flex items-center gap-2 pt-3 border-t border-slate-200 dark:border-slate-700"
            >
              <input
                v-model="newSourceTerm"
                type="text"
                :placeholder="t('glossary.sourceTerm')"
                class="input-field flex-1 text-sm font-mono"
                @keydown.enter="addEntry(g.id)"
              />
              <span class="text-slate-400">→</span>
              <input
                v-model="newTargetTerm"
                type="text"
                :placeholder="t('glossary.targetTranslation')"
                class="input-field flex-1 text-sm font-mono"
                @keydown.enter="addEntry(g.id)"
              />
              <button
                @click="addEntry(g.id)"
                class="btn-primary text-xs py-2"
              >
                <Plus class="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
