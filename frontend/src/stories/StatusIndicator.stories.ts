import type { Meta, StoryObj } from "@storybook/vue3";
import StatusIndicator from "../components/common/StatusIndicator.vue";

const meta: Meta<typeof StatusIndicator> = {
  title: "Common/StatusIndicator",
  component: StatusIndicator,
  tags: ["autodocs"],
};

export default meta;
type Story = StoryObj<typeof StatusIndicator>;

export const Default: Story = {
  render: () => ({
    components: { StatusIndicator },
    template: "<StatusIndicator />",
  }),
};
