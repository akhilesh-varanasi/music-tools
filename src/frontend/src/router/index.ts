// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import AlbumArtView from '../views/AlbumArtView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
  },
  { path: '/album-art', name: 'album-art', component: AlbumArtView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
