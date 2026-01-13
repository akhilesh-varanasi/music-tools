// src/router/index.ts
import { createRouter, createWebHistory, createWebHashHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import AlbumArtView from '../views/AlbumArtView.vue'
import Yt2Mp3View from '../views/Yt2Mp3View.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
  },
  { path: '/album-art', name: 'album-art', component: AlbumArtView },
  { path: '/yt2mp3', name: 'yt2mp3', component: Yt2Mp3View },

]

const isDesktopBuild = import.meta.env.MODE === 'desktop'

const history = isDesktopBuild ? createWebHashHistory() : createWebHistory()

const router = createRouter({
  history,
  routes,
})

export default router
