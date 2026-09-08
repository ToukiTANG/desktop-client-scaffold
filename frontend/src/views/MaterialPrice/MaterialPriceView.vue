<template>
  <div class="material-price-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div>
        <h2 class="page-title">材料价格</h2>
      </div>

      <el-button :icon="Refresh" :loading="loading" @click="handleRefresh"> 刷新 </el-button>
    </div>

    <!-- 当前数据来源 -->
    <div class="source-bar">
      <span class="source-label"> 当前车间、公寓： </span>

      <template v-if="appConfig">
        <el-tag effect="plain">
          {{ appConfig.workshop }}
        </el-tag>

        <span class="separator"> / </span>

        <el-tag effect="plain">
          {{ appConfig.apartment }}
        </el-tag>
      </template>

      <span v-else class="empty-config"> 未配置 </span>
    </div>

    <!-- 查询区域 -->
    <el-card shadow="never" class="query-card">
      <el-form inline @submit.prevent>
        <el-form-item label="品名">
          <el-input v-model="keyword" clearable placeholder="请输入品名" style="width: 240px" @keyup.enter="handleSearch" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch"> 查询 </el-button>

          <el-button @click="handleReset"> 重置 </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 表格区域 -->
    <el-card shadow="never" class="table-card">
      <div class="table-header">
        <span class="table-title"> 材料价格列表 </span>

        <span class="table-count"> 共 {{ filteredMaterials.length }} 条 </span>
      </div>

      <el-table v-loading="loading" :data="pagedMaterials" stripe border table-layout="fixed" style="width: 100%">
        <el-table-column label="序号" width="80" align="center">
          <template #default="{ $index }">
            {{ (currentPage - 1) * pageSize + $index + 1 }}
          </template>
        </el-table-column>

        <el-table-column prop="name" label="品名" min-width="240" />

        <el-table-column prop="price" label="单价" min-width="160" align="right">
          <template #default="{ row }">
            {{ row.price ?? '-' }}
          </template>
        </el-table-column>

        <el-table-column prop="unit" label="单位" width="140" align="center" />

        <template #empty>
          <el-empty description="暂无材料价格数据" :image-size="80" />
        </template>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="filteredMaterials.length"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @size-change="handlePageSizeChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Search } from '@element-plus/icons-vue'

import { getAppConfig } from '@/api/appConfig'
import { materialPriceStore } from '@/stores/materialPrice'

import type { AppConfig } from '@/types'

const appConfig = ref<AppConfig | null>(null)

const keyword = ref('')
const queryKeyword = ref('')

const currentPage = ref(1)
const pageSize = ref(20)

const loading = computed(() => {
  return materialPriceStore.state.loading
})

const materials = computed(() => {
  return materialPriceStore.state.materials
})

const filteredMaterials = computed(() => {
  const value = queryKeyword.value.trim().toLowerCase()

  if (!value) {
    return materials.value
  }

  return materials.value.filter((item) => {
    return item.name.toLowerCase().includes(value)
  })
})

const pagedMaterials = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value

  return filteredMaterials.value.slice(start, end)
})

async function loadAppConfig() {
  try {
    const response = await getAppConfig()

    if (!response.success) {
      ElMessage.error(response.message || '读取应用配置失败')
      return
    }

    appConfig.value = response.data?.config ?? null
  } catch (error) {
    console.error('Failed to load app config:', error)
    ElMessage.error('读取应用配置失败')
  }
}

function handleSearch() {
  queryKeyword.value = keyword.value
  currentPage.value = 1
}

function handleReset() {
  keyword.value = ''
  queryKeyword.value = ''
  currentPage.value = 1
}

async function handleRefresh() {
  const success = await materialPriceStore.refresh()

  if (success) {
    currentPage.value = 1
    ElMessage.success('材料价格已刷新')
  } else {
    ElMessage.error(materialPriceStore.state.error || '材料价格表读取失败')
  }
}

function handlePageSizeChange() {
  currentPage.value = 1
}

onMounted(async () => {
  await loadAppConfig()

  const success = await materialPriceStore.load()

  if (!success && materialPriceStore.state.error) {
    ElMessage.error(materialPriceStore.state.error)
  }
})
</script>

<style scoped>
.material-price-page {
  padding: 24px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.page-title {
  margin: 0;
  font-size: 22px;
  font-weight: 600;
}

.page-description {
  margin-top: 6px;
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.source-bar {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  font-size: 14px;
}

.source-label {
  margin-right: 8px;
  color: var(--el-text-color-secondary);
}

.separator {
  margin: 0 8px;
  color: var(--el-text-color-placeholder);
}

.empty-config {
  color: var(--el-text-color-secondary);
}

.query-card {
  margin-bottom: 16px;
}

.query-card :deep(.el-card__body) {
  padding-bottom: 2px;
}

.table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.table-title {
  font-size: 16px;
  font-weight: 600;
}

.table-count {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.table-card :deep(.el-table__header th) {
  font-weight: 600;
  background: var(--el-fill-color-light);
}

.table-card :deep(.el-table__cell) {
  padding: 10px 0;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
}
</style>
