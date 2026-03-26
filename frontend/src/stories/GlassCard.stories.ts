import type { Meta, StoryObj } from "@storybook/vue3";
import { defineComponent } from "vue";

const GlassCardWrapper = defineComponent({
  template: `
    <div class="p-8 bg-gradient-to-br from-indigo-500 to-purple-600 min-h-[300px] flex items-center justify-center">
      <div class="glass-card p-6 w-64 text-center">
        <h3 class="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-slate-900 to-slate-500 dark:from-white dark:to-slate-400 mb-2">Glass Card</h3>
        <p class="text-slate-600 dark:text-slate-300">This is a glassmorphism card component testing the backdrop blur and borders.</p>
        <button class="btn-primary mt-4 w-full">Action</button>
      </div>
    </div>
  `,
});

const meta: Meta = {
  title: "Common/GlassCard",
  component: GlassCardWrapper,
  tags: ["autodocs"],
};

export default meta;
type Story = StoryObj<typeof GlassCardWrapper>;

export const Default: Story = {
  render: () => ({
    components: { GlassCardWrapper },
    template: "<GlassCardWrapper />",
  }),
};
