import { createRouter, createWebHistory } from "vue-router";
import AppLayout from "@/components/layout/AppLayout.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      component: AppLayout,
      children: [
        {
          path: "",
          name: "dashboard",
          component: () => import("@/views/DashboardView.vue"),
        },
        {
          path: "translate",
          name: "translate",
          component: () => import("@/views/TranslateView.vue"),
        },
        {
          path: "translate/file",
          name: "translate-file",
          component: () => import("@/views/FileTranslateView.vue"),
        },
        {
          path: "history",
          name: "history",
          component: () => import("@/views/HistoryView.vue"),
        },
        {
          path: "models",
          name: "models",
          component: () => import("@/views/ModelsView.vue"),
        },
        {
          path: "glossaries",
          name: "glossaries",
          component: () => import("@/views/GlossaryView.vue"),
        },
        {
          path: "settings",
          name: "settings",
          component: () => import("@/views/SettingsView.vue"),
        },
      ],
    },
  ],
});

export default router;
