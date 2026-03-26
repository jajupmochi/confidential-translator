import { createI18n } from "vue-i18n";
import en from "./en.json";
import zh from "./zh.json";

// Use localStorage directly so it's loaded before Pinia
const savedLocale = localStorage.getItem("locale") || "en";
const defaultLocale = ["en", "zh", "de", "fr"].includes(savedLocale)
  ? savedLocale
  : "en";

export const i18n = createI18n({
  legacy: false,
  locale: defaultLocale,
  fallbackLocale: "en",
  messages: {
    en,
    zh,
    // DE and FR omitted for brevity, fallback to EN
  },
});

export const availableLocales = [
  { code: "en", name: "English" },
  { code: "zh", name: "中文" },
  { code: "de", name: "Deutsch" },
  { code: "fr", name: "Français" },
];

export function setI18nLanguage(locale: string) {
  i18n.global.locale.value = locale as any;
  document.querySelector("html")?.setAttribute("lang", locale);
}
