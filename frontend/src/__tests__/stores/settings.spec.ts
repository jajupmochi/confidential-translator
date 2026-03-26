import { describe, it, expect, beforeEach, vi } from "vitest";
import { setActivePinia, createPinia } from "pinia";
import { useSettingsStore } from "@/stores/settings";

describe("Settings Store", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    localStorage.clear();

    // Mock matchMedia
    Object.defineProperty(window, "matchMedia", {
      writable: true,
      value: vi.fn().mockImplementation((query) => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    });
  });

  it("initializes with default values", () => {
    const store = useSettingsStore();
    expect(store.theme).toBe("system");
    expect(store.locale).toBe("en");
    expect(store.defaultSourceLang).toBe("auto");
    expect(store.defaultTargetLang).toBe("en");
    expect(store.defaultModel).toBe("qwen3:14b-q4_K_M");
  });

  it("updates theme and saves to localStorage", () => {
    const store = useSettingsStore();
    store.setTheme("dark");
    expect(store.theme).toBe("dark");
    expect(localStorage.getItem("theme")).toBe("dark");
    expect(document.documentElement.classList.contains("dark")).toBe(true);
  });

  it("updates locale and saves to localStorage", () => {
    const store = useSettingsStore();
    store.setLocale("zh");
    expect(store.locale).toBe("zh");
    expect(localStorage.getItem("locale")).toBe("zh");
  });
});
