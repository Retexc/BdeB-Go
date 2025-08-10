// src/router.js
import { createRouter, createWebHistory } from "vue-router";
import Background from "./views/Background.vue";
import Settings from "./views/Settings.vue";
import Console from "./views/Console.vue";
import Display from "./views/MainDisplay.vue";
import Loading from "./views/Loading.vue";
import EndDisplay from "./views/EndDisplay.vue";
const routes = [
  { path: "/console", component: Console },
  { path: "/background", component: Background },
  { path: "/settings", component: Settings },
  { path: "/display", component: Display },
  { path: "/loading", component: Loading },
  { path: "/end_display", component: EndDisplay },  
  { path: "/admin", redirect: "/admin/console" },
];

export default createRouter({
  history: createWebHistory(),
  routes,
});
