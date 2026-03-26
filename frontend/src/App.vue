<script setup lang="ts">
import { onMounted } from "vue";
import { RouterView } from "vue-router";
import { useSettingsStore } from "@/stores/settings";

const settings = useSettingsStore();

onMounted(() => {
  // Initialize theme on app load
  settings.initTheme();
  settings.fetchBackendSettings();
});
</script>

<template>
  <RouterView v-slot="{ Component }">
    <Transition name="page" mode="out-in">
      <component :is="Component" />
    </Transition>
  </RouterView>
</template>
