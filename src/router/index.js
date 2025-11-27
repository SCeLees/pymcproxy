import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import ServerManagement from '../views/ServerManagement.vue'
import Statistics from '../views/Statistics.vue'
import WhitelistBlacklist from '../views/WhitelistBlacklist.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/servers',
    name: 'ServerManagement',
    component: ServerManagement
  },
  {
    path: '/whitelist-blacklist',
    name: 'WhitelistBlacklist',
    component: WhitelistBlacklist
  },
  {
    path: '/statistics',
    name: 'Statistics',
    component: Statistics
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router