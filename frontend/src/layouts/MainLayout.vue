<template>
  <div class="app-layout">
    <!-- 左侧导航 -->
    <aside class="sidebar">
      <!-- Logo / 名称 -->
      <div class="sidebar-header">
        <div class="logo">D</div>

        <span class="app-name"> Desktop Tool </span>
      </div>

      <!-- 主菜单 -->
      <el-menu class="sidebar-menu" :default-active="activeMenu" router>
        <el-menu-item index="/">
          <el-icon> <HomeFilled /> </el-icon>
          <span>首页</span>
        </el-menu-item>

        <el-menu-item index="/material-price">
          <el-icon><Coin /></el-icon>
          <span>材料价格</span>
        </el-menu-item>
      </el-menu>

      <div class="sidebar-footer">
        <el-menu :default-active="activeMenu" router>
          <el-menu-item index="/settings">
            <el-icon> <Setting /> </el-icon>
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
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Coin, HomeFilled, Setting } from '@element-plus/icons-vue'
import { materialPriceStore } from '@/stores/materialPrice.ts'

const route = useRoute()

const activeMenu = computed(() => route.path)

onMounted(() => {
  void materialPriceStore.load()
})
</script>

<style scoped>
.app-layout {
  display: flex;

  width: 100%;
  height: 100%;

  overflow: hidden;

  background: #f5f6f8;
}

.sidebar {
  width: 220px;
  height: 100%;

  flex-shrink: 0;

  display: flex;
  flex-direction: column;

  background: #ffffff;
  border-right: 1px solid #e5e7eb;
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

  color: white;

  font-size: 16px;
  font-weight: 600;
}

.sidebar-menu {
  flex: 1;

  min-height: 0;

  border-right: none;
}

.sidebar-footer {
  flex-shrink: 0;

  border-top: 1px solid #e5e7eb;
}

.sidebar-footer :deep(.el-menu) {
  border-right: none;
}

.main-content {
  flex: 1;

  min-width: 0;
  min-height: 0;

  overflow: auto;

  padding: 12px;

  box-sizing: border-box;
}
</style>
