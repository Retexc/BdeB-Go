import { createRouter, createWebHistory } from 'vue-router'
import Login       from './views/Login.vue'
import Home        from './views/Home.vue'
//import Background  from './views/Background.vue'
//import Settings    from './views/Settings.vue'

const routes = [
  { path: '/',        redirect: '/login' },
  { path: '/login',   component: Login },
  { path: '/home',    component: Home },
//  { path: '/background', component: Background },
//  { path: '/settings',   component: Settings },
]

export default createRouter({
  history: createWebHistory('/admin/'),
  routes,
})
