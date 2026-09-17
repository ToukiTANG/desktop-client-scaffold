<template>
  <div class="app-layout">
    <!-- 左侧导航 -->
    <aside class="sidebar">
      <!-- Logo / 名称 -->
      <div class="sidebar-header">
        <div class="logo">D</div>

        <span class="app-name"> Desktop Tool </span>
      </div>

      <!-- 主菜单：仅此区域滚动 -->
      <el-scrollbar class="sidebar-menu-scroll">
        <el-menu class="sidebar-menu" :default-active="activeMenu" router>
          <el-menu-item index="/">
            <el-icon>
              <HomeFilled />
            </el-icon>

            <span>首页</span>
          </el-menu-item>

          <template v-for="item in menuItems" :key="item.index">
            <!-- 带子菜单 -->
            <el-sub-menu v-if="item.children?.length" :index="item.index">
              <template #title>
                <el-icon v-if="item.icon">
                  <component :is="item.icon" />
                </el-icon>

                <span>
                  {{ item.label }}
                </span>
              </template>

              <el-menu-item v-for="child in item.children" :key="child.index" :index="child.index">
                <el-icon v-if="child.icon">
                  <component :is="child.icon" />
                </el-icon>

                <span>
                  {{ child.label }}
                </span>
              </el-menu-item>
            </el-sub-menu>

            <!-- 普通菜单 -->
            <el-menu-item v-else :index="item.index">
              <el-icon v-if="item.icon">
                <component :is="item.icon" />
              </el-icon>

              <span>
                {{ item.label }}
              </span>
            </el-menu-item>
          </template>
        </el-menu>
      </el-scrollbar>

      <!-- 底部设置：固定，不参与滚动 -->
      <div class="sidebar-footer">
        <el-menu :default-active="activeMenu" router>
          <el-menu-item index="/settings">
            <el-icon>
              <Setting />
            </el-icon>

            <span>设置</span>
          </el-menu-item>
        </el-menu>
      </div>
    </aside>

    <!-- 右侧内容 -->
    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { HomeFilled, Setting } from '@element-plus/icons-vue'
import { useRoute } from 'vue-router'

import { businessMenuItems } from '@/business/menu'
import type { AppMenuItem } from '@/types/navigation'

const route = useRoute()

const menuItems: AppMenuItem[] = businessMenuItems

const activeMenu = computed(() => route.path)
</script>

<style scoped>
.app-layout {
  display: flex;

  width: 100%;
  height: 100%;

  min-width: 0;
  min-height: 0;

  overflow: hidden;

  background: #f5f6f8;
}

.sidebar {
  width: 220px;
  height: 100%;

  flex-shrink: 0;

  display: flex;
  flex-direction: column;

  min-height: 0;

  overflow: hidden;

  background: #ffffff;

  border-right: 1px solid #e5e7eb;

  box-sizing: border-box;
}

.sidebar-header {
  height: 64px;
  padding: 0 20px;

  flex-shrink: 0;

  display: flex;
  align-items: center;

  box-sizing: border-box;
}

.logo {
  width: 32px;
  height: 32px;

  flex-shrink: 0;

  display: flex;
  align-items: center;
  justify-content: center;

  border-radius: 8px;

  background: #409eff;

  color: #ffffff;

  font-size: 16px;
  font-weight: 600;
}

.app-name {
  margin-left: 8px;

  white-space: nowrap;
}

/*
 * 中间菜单区域：
 * 占据 Header 和 Footer 之间的所有剩余空间。
 * 菜单过长时只滚动这里。
 */
.sidebar-menu-scroll {
  flex: 1;

  min-height: 0;
}

/*
 * 防止 Element Plus 横向滚动。
 */
.sidebar-menu-scroll :deep(.el-scrollbar__wrap) {
  overflow-x: hidden;
}

.sidebar-menu-scroll :deep(.el-scrollbar__view) {
  min-height: 100%;
}

.sidebar-menu {
  width: 100%;

  border-right: none;
}

.sidebar-footer {
  flex-shrink: 0;

  background: #ffffff;

  border-top: 1px solid #e5e7eb;
}

.sidebar-footer :deep(.el-menu) {
  border-right: none;
}

.main-content {
  flex: 1;

  min-width: 0;
  min-height: 0;

  overflow: hidden;
}
</style>
