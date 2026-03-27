import re

with open("frontend/src/views/FileTranslateView.vue", "r") as f:
    content = f.read()

# 1. Add Icons
content = content.replace("FolderSearch\n}", "FolderSearch,\n  Brain,\n  ChevronDown,\n  ChevronRight\n}")

# 2. Add sourceContent ref
content = content.replace('const translatedContent = ref("");', 'const translatedContent = ref("");\nconst sourceContent = ref("");')

# 3. reset sourceContent
content = content.replace('translatedContent.value = "";\n  thinkingText', 'translatedContent.value = "";\n  sourceContent.value = "";\n  thinkingText')

# 4. Replace startTranslation body
src_start_trans = """  try {
    const endpoint = isNative ? "/api/translate/file/native" : "/api/translate/file";
    const res = await fetch(endpoint, {"""
src_end_trans = """    } else {
      error.value = "Network error";
    }
  } finally {"""

new_start_trans = """  try {
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
      const lines = buffer.split("\\n");
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
  } finally {"""

content = content[:content.find(src_start_trans)] + new_start_trans + content[content.find(src_end_trans)+len(src_end_trans):]


# 5. Replace Template Previews
template_old = """      <div
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
      </div>"""

template_new = """      <div
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
         </div>
      </div>

      <div
        v-else
        class="flex-1 glass-card bg-slate-50/50 dark:bg-slate-900/10 border-dashed border-2 flex items-center justify-center"
      >
        <span class="text-slate-400 font-medium"
          >Click Translate to begin processing document</span
        >
      </div>"""

if template_old in content:
    content = content.replace(template_old, template_new)
else:
    print("WARNING: template_old not found!")

with open("frontend/src/views/FileTranslateView.vue", "w") as f:
    f.write(content)
