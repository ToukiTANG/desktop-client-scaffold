import { createRouter, createWebHashHistory } from 'vue-router'

import { getAppConfig } from '@/api/appConfig'
import MainLayout from '@/layouts/MainLayout.vue'

const router = createRouter({
  history: createWebHashHistory(),

  routes: [
    {
      path: '/setup',
      name: 'setup',
      component: () => import('@/views/SetupView.vue'),
    },

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
          path: 'settings',
          name: 'settings',
          component: () => import('@/views/SettingsView.vue'),
        },
      ],
    },
  ],
})

router.beforeEach(async (to) => {
  try {
    const response = await getAppConfig()

    const configured = response.success && response.data?.configured

    // 未初始化时，只允许进入 setup
    if (!configured && to.name !== 'setup') {
      return {
        name: 'setup',
      }
    }

    // 已初始化后，不允许再进入 setup
    if (configured && to.name === 'setup') {
      return {
        name: 'home',
      }
    }

    return true
  } catch (error) {
    console.error('检查初始化配置失败:', error)

    // 获取配置失败时，优先进入初始化页面
    if (to.name !== 'setup') {
      return {
        name: 'setup',
      }
    }

    return true
  }
})

export default router
