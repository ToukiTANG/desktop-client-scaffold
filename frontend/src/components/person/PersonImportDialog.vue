<template>
  <el-dialog
    :model-value="modelValue"
    title="批量导入人员"
    width="1000px"
    destroy-on-close
    @open="handleOpen"
    @close="handleClose"
  >
    <div class="import-dialog">
      <!-- 文件选择 -->
      <div class="file-section">
        <el-button type="primary" :loading="selecting" @click="handleSelectFile">
          选择 Excel 文件
        </el-button>

        <div v-if="fileName" class="file-info">
          <span class="file-label"> 当前文件： </span>

          <span class="file-name">
            {{ fileName }}
          </span>
        </div>

        <span v-else class="file-tip"> 请选择 .xlsx 文件 </span>
      </div>

      <!-- 导入说明 -->
      <el-alert class="import-alert" title="Excel 字段要求" type="info" :closable="false" show-icon>
        <template #default>
          <div class="field-description">
            Excel 第一行必须包含： 姓名、部门、职名、身份类型、专业分类、学历、性别、生产组分类。
          </div>
        </template>
      </el-alert>

      <!-- 解析统计 -->
      <div v-if="fileName" class="statistics">
        <div class="stat-item">
          <span class="stat-label"> 数据总数 </span>

          <span class="stat-value">
            {{ total }}
          </span>
        </div>

        <div class="stat-item">
          <span class="stat-label"> 校验通过 </span>

          <span class="stat-value success">
            {{ successCount }}
          </span>
        </div>

        <div class="stat-item">
          <span class="stat-label"> 校验失败 </span>

          <span class="stat-value danger">
            {{ failureCount }}
          </span>
        </div>
      </div>

      <!-- 预览区域 -->
      <div class="preview-section">
        <div class="preview-header">
          <div>
            <span class="preview-title"> 数据预览 </span>

            <span v-if="previewRows.length" class="preview-description">
              当前展示 {{ previewRows.length }} 条
            </span>
          </div>

          <span v-if="total > previewLimit" class="preview-limit">
            仅展示前 {{ previewLimit }} 条有效数据
          </span>
        </div>

        <el-table
          v-loading="selecting"
          :data="previewRows"
          border
          stripe
          height="360"
          empty-text="请选择 Excel 文件进行解析"
        >
          <!-- Excel 原始行号 -->
          <el-table-column prop="row" label="Excel行" width="80" fixed="left" />

          <el-table-column prop="name" label="姓名" width="100" fixed="left" />

          <el-table-column label="性别" width="80">
            <template #default="{ row }">
              {{ getOptionLabel(genderOptions, row.gender) }}
            </template>
          </el-table-column>

          <el-table-column prop="department" label="部门" min-width="160" show-overflow-tooltip />

          <el-table-column prop="jobTitle" label="职名" min-width="140" show-overflow-tooltip />

          <el-table-column label="身份类型" min-width="120">
            <template #default="{ row }">
              {{ getOptionLabel(identityOptions, row.identity) }}
            </template>
          </el-table-column>

          <el-table-column label="专业分类" width="100">
            <template #default="{ row }">
              {{ getOptionLabel(specializeClassifyOptions, row.specializeClassify) }}
            </template>
          </el-table-column>

          <el-table-column prop="education" label="学历" width="100" />

          <el-table-column label="生产组分类" min-width="260" show-overflow-tooltip>
            <template #default="{ row }">
              {{ getOptionLabel(productionGroupClassifyOptions, row.productionGroupClassify) }}
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 错误数据 -->
      <div v-if="errors.length > 0" class="error-section">
        <div class="error-header">
          <span class="error-title"> 数据错误 </span>

          <span class="error-count"> 共 {{ errors.length }} 条 </span>
        </div>

        <el-scrollbar max-height="180px">
          <div v-for="item in errors" :key="`${item.row}-${item.message}`" class="error-item">
            <span class="error-row"> 第 {{ item.row }} 行 </span>

            <span>
              {{ item.message }}
            </span>
          </div>
        </el-scrollbar>
      </div>
    </div>

    <!-- 底部按钮 -->
    <template #footer>
      <div class="dialog-footer">
        <el-button :disabled="selecting || importing" @click="handleClose"> 取消 </el-button>

        <el-button
          type="primary"
          :loading="importing"
          :disabled="successCount === 0 || selecting || importing"
          @click="handleConfirm"
        >
          确认导入
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'

import { ElMessage } from 'element-plus'

import { confirmPersonImport, selectPersonImportFile } from '@/api/person'

import { usePersonDictionary } from '@/composables/usePersonDictionary'

import type { PersonImportPreviewError, PersonImportPreviewRow } from '@/types'

defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  success: []
}>()

const {
  genderOptions,
  identityOptions,
  specializeClassifyOptions,
  productionGroupClassifyOptions,
  loadDictionary,
  getOptionLabel,
} = usePersonDictionary()
/**
 * 是否正在打开文件窗口 / 解析 Excel。
 */
const selecting = ref(false)

const importing = ref(false)

/**
 * 当前 Excel 文件名称。
 */
const fileName = ref('')

/**
 * Excel 数据总数。
 */
const total = ref(0)

/**
 * 校验成功数量。
 */
const successCount = ref(0)

/**
 * 校验失败数量。
 */
const failureCount = ref(0)

/**
 * 后端返回的最大预览数量。
 */
const previewLimit = ref(100)

/**
 * 有效数据预览。
 */
const previewRows = ref<PersonImportPreviewRow[]>([])

/**
 * Excel 数据错误。
 */
const errors = ref<PersonImportPreviewError[]>([])

/**
 * 清空当前预览状态。
 */
function resetPreview() {
  fileName.value = ''

  total.value = 0

  successCount.value = 0

  failureCount.value = 0

  previewLimit.value = 100

  previewRows.value = []

  errors.value = []
}

/**
 * Dialog 打开。
 */
async function handleOpen() {
  resetPreview()

  try {
    await loadDictionary()
  } catch (error) {
    console.error(error)

    ElMessage.error('加载人员业务字典失败')
  }
}

/**
 * Python 打开系统文件选择窗口，
 * 并直接解析 Excel。
 */
async function handleSelectFile() {
  selecting.value = true

  try {
    const response = await selectPersonImportFile()

    if (!response.success) {
      ElMessage.error(response.message || 'Excel 文件解析失败')

      return
    }

    /**
     * 用户在系统文件选择框中点击了取消。
     */
    if (!response.data) {
      resetPreview()

      return
    }

    const result = response.data

    console.log('人员导入预览结果：', result)

    fileName.value = result.fileName ?? ''

    total.value = result.total ?? 0

    successCount.value = result.successCount ?? 0

    failureCount.value = result.failureCount ?? 0

    previewLimit.value = result.previewLimit ?? 100

    previewRows.value = Array.isArray(result.preview) ? result.preview : []

    errors.value = Array.isArray(result.errors) ? result.errors : []

    if (result.failureCount > 0) {
      ElMessage.warning(
        `解析完成：${result.successCount} 条通过，${result.failureCount} 条存在错误`,
      )

      return
    }

    ElMessage.success(`解析完成，共 ${result.successCount} 条有效数据`)
  } catch (error) {
    console.error(error)

    ElMessage.error('选择或解析 Excel 文件失败')
  } finally {
    selecting.value = false
  }
}

/**
 * 关闭 Dialog。
 */
function handleClose() {
  emit('update:modelValue', false)
}

async function handleConfirm() {
  if (successCount.value === 0) {
    ElMessage.warning('没有可导入的数据')

    return
  }

  importing.value = true

  try {
    const response = await confirmPersonImport()

    if (!response.success) {
      ElMessage.error(response.message || '人员导入失败')

      return
    }

    const result = response.data

    if (result.failureCount > 0) {
      ElMessage.warning(`导入完成：成功 ${result.successCount} 条，失败 ${result.failureCount} 条`)
    } else {
      ElMessage.success(`导入成功，共 ${result.successCount} 条`)
    }

    /**
     * 通知 PersonView 刷新人员列表。
     */
    emit('success')

    /**
     * 导入完成后关闭 Dialog。
     */
    handleClose()
  } catch (error) {
    console.error(error)

    ElMessage.error('人员导入失败')
  } finally {
    importing.value = false
  }
}
</script>

<style scoped>
.import-dialog {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.file-section {
  display: flex;
  align-items: center;
  min-height: 32px;
  gap: 16px;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
}

.file-label {
  color: var(--el-text-color-secondary);
}

.file-name {
  color: var(--el-text-color-primary);
  font-weight: 500;
}

.file-tip {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.import-alert {
  flex-shrink: 0;
}

.field-description {
  line-height: 1.8;
}

.statistics {
  display: flex;
  align-items: center;
  gap: 36px;
  padding: 14px 18px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 6px;
  background: var(--el-fill-color-lighter);
}

.stat-item {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.stat-label {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.stat-value {
  color: var(--el-text-color-primary);
  font-size: 20px;
  font-weight: 600;
}

.stat-value.success {
  color: var(--el-color-success);
}

.stat-value.danger {
  color: var(--el-color-danger);
}

.preview-section {
  min-height: 0;
}

.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.preview-title {
  font-size: 15px;
  font-weight: 600;
}

.preview-description {
  margin-left: 10px;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.preview-limit {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.error-section {
  padding: 12px 16px;
  border: 1px solid var(--el-color-danger-light-7);
  border-radius: 6px;
  background: var(--el-color-danger-light-9);
}

.error-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.error-title {
  color: var(--el-color-danger);
  font-size: 14px;
  font-weight: 600;
}

.error-count {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.error-item {
  display: flex;
  gap: 12px;
  padding: 5px 0;
  font-size: 13px;
  line-height: 1.5;
}

.error-row {
  min-width: 72px;
  color: var(--el-color-danger);
  font-weight: 500;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
