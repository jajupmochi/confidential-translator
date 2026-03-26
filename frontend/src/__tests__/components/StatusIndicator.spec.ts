import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import StatusIndicator from "@/components/common/StatusIndicator.vue";

// Basic test showing component mounting
describe("StatusIndicator", () => {
  it("renders correctly", () => {
    const wrapper = mount(StatusIndicator);
    expect(wrapper.text()).toContain("Ollama");
    // We expect the pulsing dot since it's "checking" by default
    expect(wrapper.find(".animate-pulse").exists()).toBe(true);
  });
});
