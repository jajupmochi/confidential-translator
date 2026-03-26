import { defineStore } from "pinia";
import { ref, watch } from "vue";

export type Theme = "light" | "dark" | "system";
export type Locale = "en" | "zh" | "de" | "fr";

export const useSettingsStore = defineStore("settings", () => {
  // State
  const theme = ref<Theme>(
    (localStorage.getItem("theme") as Theme) || "system",
  );
  const locale = ref<Locale>(
    (localStorage.getItem("locale") as Locale) || "en",
  );

  const defaultSourceLang = ref(
    localStorage.getItem("defaultSourceLang") || "auto",
  );
  const defaultTargetLang = ref(
    localStorage.getItem("defaultTargetLang") || "en",
  );
  const defaultModel = ref(
    localStorage.getItem("defaultModel") || "qwen3.5:9b",
  );
  const ollamaModelsPath = ref("");

  // Actions
  async function fetchBackendSettings() {
    try {
      const res = await fetch("/api/settings");
      if (res.ok) {
        const data = await res.json();
        ollamaModelsPath.value = data.ollama_models_path;
      }
    } catch (e) {
      console.error("Failed to fetch backend settings", e);
    }
  }

  async function saveBackendSettings() {
    try {
      await fetch("/api/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ollama_models_path: ollamaModelsPath.value }),
      });
    } catch (e) {
      console.error("Failed to save backend settings", e);
    }
  }
  function setTheme(newTheme: Theme) {
    theme.value = newTheme;
    localStorage.setItem("theme", newTheme);
    applyTheme();
  }

  function applyTheme() {
    const root = window.document.documentElement;
    root.classList.remove("light", "dark");

    if (theme.value === "system") {
      const systemTheme = window.matchMedia("(prefers-color-scheme: dark)")
        .matches
        ? "dark"
        : "light";
      root.classList.add(systemTheme);
    } else {
      root.classList.add(theme.value);
    }
  }

  function initTheme() {
    applyTheme();
    window
      .matchMedia("(prefers-color-scheme: dark)")
      .addEventListener("change", () => {
        if (theme.value === "system") {
          applyTheme();
        }
      });
  }

  function setLocale(newLocale: Locale) {
    locale.value = newLocale;
    localStorage.setItem("locale", newLocale);
    // The actual i18n locale switch happens where i18n is available
  }

  // Watchers for other settings
  watch(defaultSourceLang, (val) =>
    localStorage.setItem("defaultSourceLang", val),
  );
  watch(defaultTargetLang, (val) =>
    localStorage.setItem("defaultTargetLang", val),
  );
  watch(defaultModel, (val) => localStorage.setItem("defaultModel", val));

  return {
    theme,
    locale,
    defaultSourceLang,
    defaultTargetLang,
    defaultModel,
    ollamaModelsPath,
    setTheme,
    initTheme,
    setLocale,
    fetchBackendSettings,
    saveBackendSettings,
  };
});
