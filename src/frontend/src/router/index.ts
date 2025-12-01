// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ExampleServiceView from '../views/ExampleServiceView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
  },
  {
    path: '/example-service',
    name: 'example-service',
    component: ExampleServiceView,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
