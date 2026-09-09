<template>
  <div class="settings-page">
    <el-card v-if="businessSettingItems.length" class="business-settings-card">
      <template #header>
        <span>业务设置</span>
      </template>

      <div v-for="item in businessSettingItems" :key="item.title" class="setting-item">
        <div class="setting-info">
          <div class="setting-title">{{ item.title }}</div>
          <div v-if="item.description" class="setting-description">
            {{ item.description }}
          </div>
        </div>

        <el-button type="primary" link @click="router.push(item.to)">
          {{ item.actionLabel }}
        </el-button>
      </div>
    </el-card>
    <el-card>
      <template #header>
        <span>关于</span>
      </template>

      <el-descriptions :column="1" border>
        <el-descriptions-item label="应用名称">
          {{ appInfo?.name ?? '-' }}
        </el-descriptions-item>

        <el-descriptions-item label="当前版本">
          {{ appInfo.version }}
        </el-descriptions-item>

        <el-descriptions-item label="数据目录">
          <div class="path-row">
            <span class="path-text">{{ appInfo.dataDir }}</span>

            <div class="path-actions">
              <el-button link type="primary" @click="handleOpenDirectory(appInfo.dataDir)"> 打开目录 </el-button>

              <el-button link type="primary" @click="handleCopyPath(appInfo.dataDir)"> 复制路径 </el-button>
            </div>
          </div>
        </el-descriptions-item>

        <el-descriptions-item label="日志目录">
          <div class="path-row">
            <span class="path-text">{{ appInfo.logDir }}</span>

            <div class="path-actions">
              <el-button link type="primary" @click="handleOpenDirectory(appInfo.logDir)"> 打开目录 </el-button>

              <el-button link type="primary" @click="handleCopyPath(appInfo.logDir)"> 复制路径 </el-button>
            </div>
          </div>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'

import { getAppInfo, openDirectory } from '@/api/app'
import type { AppInfo } from '@/types'
import { useRouter } from 'vue-router'

import { businessSettingItems } from '@/business/settings'

const router = useRouter()

const appInfo = ref<AppInfo>({
  name: '-',
  version: '-',
  dataDir: '-',
  logDir: '-',
})

async function loadAppInfo() {
  const response = await getAppInfo()

  if (response.success && response.data) {
    appInfo.value = response.data
  }
}

async function handleOpenDirectory(path: string) {
  const response = await openDirectory(path)

  if (!response.success) {
    ElMessage.error(response.message || '打开目录失败')
  }
}

async function handleCopyPath(path: string) {
  try {
    await navigator.clipboard.writeText(path)
  } catch {
    const textarea = document.createElement('textarea')

    textarea.value = path
    textarea.style.position = 'fixed'
    textarea.style.opacity = '0'

    document.body.appendChild(textarea)
    textarea.select()
    document.execCommand('copy')
    textarea.remove()
  }

  ElMessage.success('路径已复制')
}

onMounted(() => {
  loadAppInfo()
})
</script>

<style scoped>
.settings-page {
  padding: 20px;
}

.path-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.path-text {
  flex: 1;
  word-break: break-all;
}

.business-settings-card {
  margin-bottom: 20px;
}

.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}

.setting-info {
  min-width: 0;
}

.setting-title {
  font-weight: 500;
}

.setting-description {
  margin-top: 6px;
  color: #909399;
  font-size: 13px;
}
</style>
