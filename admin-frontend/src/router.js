// src/router.js
import { createRouter, createWebHistory } from 'vue-router'
import Login      from './views/Login.vue'
import Background from './views/Background.vue'
import Settings   from './views/Settings.vue'
import Console    from './views/Console.vue'   // ← make sure this file exists!

const routes = [

  { path: '/console',   component: Console   },
  { path: '/login',     component: Login     },
  { path: '/background',component: Background},
  { path: '/settings',  component: Settings  },
  { path: '/admin',           redirect: '/admin/console' },
]

export default createRouter({
  history: createWebHistory(),  // ← use the thing you imported
  routes
})
