import { createRouter, createWebHistory } from 'vue-router'

import HistoryPage from '../pages/HistoryPage.vue'
import HomePage from '../pages/HomePage.vue'
import RealtimePage from '../pages/RealtimePage.vue'
import SettingsPage from '../pages/SettingsPage.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomePage },
    { path: '/realtime', name: 'realtime', component: RealtimePage },
    { path: '/history', name: 'history', component: HistoryPage },
    { path: '/settings', name: 'settings', component: SettingsPage },
  ],
})

export default router
