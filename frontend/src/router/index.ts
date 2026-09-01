import { createRouter, createWebHashHistory } from 'vue-router'

import MainLayout from '@/layouts/MainLayout.vue'

const router = createRouter({
  history: createWebHashHistory(),

  routes: [
    {
      path: '/',
      component: MainLayout,

      children: [
        {
          path: '',
          name: 'home',
          component: () => import('@/views/HomeView.vue'),
        },

        {
          path: 'person',
          name: 'person',
          component: () => import('@/views/PersonView.vue'),
        },

        {
          path: 'problem',
          name: 'problem',
          component: () => import('@/views/ProblemView.vue'),
        },

        {
          path: 'profile',
          name: 'profile',
          component: () => import('@/views/PorfileView.vue'),
        },

        {
          path: 'settings',
          name: 'settings',
          component: () => import('@/views/SettingsView.vue'),
        },
      ],
    },
  ],
})

export default router
