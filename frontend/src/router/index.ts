import { createRouter, createWebHashHistory } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'
import { installBusinessRouter } from '@/business/router'
import { businessRoutes, businessStandaloneRoutes } from '@/business/routes'

const router = createRouter({
  history: createWebHashHistory(),

  routes: [
    ...businessStandaloneRoutes,

    {
      path: '/',
      component: MainLayout,

      children: [
        {
          path: '',
          name: 'home',
          component: () => import('@/views/HomeView.vue'),
        },

        ...businessRoutes,

        {
          path: 'settings',
          name: 'settings',
          component: () => import('@/views/SettingsView.vue'),
        },
      ],
    },
  ],
})

installBusinessRouter(router)

export default router
