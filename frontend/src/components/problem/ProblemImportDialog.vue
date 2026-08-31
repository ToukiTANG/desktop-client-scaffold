<template>
  <el-dialog
    v-model="visible"
    title="导入问题数据"
    width="92%"
    top="5vh"
    destroy-on-close
    :close-on-click-modal="false"
  >
    <div class="import-toolbar">
      <el-button type="primary" :loading="selecting" @click="handleSelectFile">
        选择 Excel
      </el-button>

      <span class="import-tip">
        支持 .xls、.xlsx；第 1 行为标题，第 2 行为字段名，第 3 行开始为数据
      </span>
    </div>

    <template v-if="previewResult">
      <el-alert class="file-alert" type="info" :closable="false" show-icon>
        <template #title>
          {{ previewResult.fileName }}
        </template>
      </el-alert>

      <div class="statistics">
        <el-statistic title="数据总数" :value="previewResult.total" />

        <el-statistic title="可导入" :value="previewResult.successCount" />

        <el-statistic title="错误数据" :value="previewResult.failureCount" />

        <el-statistic title="当前预览" :value="previewResult.preview.length" />
      </div>

      <el-alert
        v-if="previewResult.preview.length >= previewResult.previewLimit"
        class="preview-alert"
        type="info"
        :closable="false"
        :title="`数据较多，当前仅预览前 ${previewResult.previewLimit} 条有效数据`"
      />

      <div class="section-title">数据预览</div>

      <el-table :data="previewResult.preview" border stripe height="430" style="width: 100%">
        <el-table-column prop="row" label="Excel 行" width="90" fixed="left" align="center" />

        <el-table-column label="状态" width="100" fixed="left">
          <template #default="{ row }">
            {{ getOptionLabel(statusOptions, row.status) }}
          </template>
        </el-table-column>

        <el-table-column label="已分解" width="90">
          <template #default="{ row }">
            {{ getOptionLabel(decomposedOptions, row.decomposed) }}
          </template>
        </el-table-column>

        <el-table-column label="已修订" width="90">
          <template #default="{ row }">
            {{ getOptionLabel(revisedOptions, row.revised) }}
          </template>
        </el-table-column>

        <el-table-column label="已考核" width="90">
          <template #default="{ row }">
            {{ getOptionLabel(assessedOptions, row.assessed) }}
          </template>
        </el-table-column>

        <el-table-column
          prop="checkDepartment"
          label="检查部门"
          width="160"
          show-overflow-tooltip
        />

        <el-table-column prop="checkPerson" label="检查人员" width="130" show-overflow-tooltip />

        <el-table-column label="检查类型" width="190" show-overflow-tooltip>
          <template #default="{ row }">
            {{ getOptionLabel(checkTypeOptions, row.checkType) }}
          </template>
        </el-table-column>

        <el-table-column label="检查方式" width="150">
          <template #default="{ row }">
            {{ getOptionLabel(checkWayOptions, row.checkWay) }}
          </template>
        </el-table-column>

        <el-table-column prop="checkStartTime" label="检查开始时间" width="170" />

        <el-table-column prop="checkEndTime" label="检查结束时间" width="170" />

        <el-table-column prop="submitTime" label="提交时间" width="170" />

        <el-table-column prop="problemItem" label="问题项点" width="200" show-overflow-tooltip />

        <el-table-column prop="consequences" label="后果明示" width="200" show-overflow-tooltip />

        <el-table-column prop="riskType" label="风险类型" width="160" show-overflow-tooltip />

        <el-table-column label="风险等级" width="140">
          <template #default="{ row }">
            {{ getOptionLabel(riskLevelOptions, row.riskLevel) }}
          </template>
        </el-table-column>

        <el-table-column label="问题归类" width="130">
          <template #default="{ row }">
            {{ getOptionLabel(problemClassifyOptions, row.problemClassify) }}
          </template>
        </el-table-column>

        <el-table-column label="问题分项" width="100">
          <template #default="{ row }">
            {{ getOptionLabel(problemLabelOptions, row.problemLabel) }}
          </template>
        </el-table-column>

        <el-table-column prop="problemExtraPoints" label="问题加分" width="110" />

        <el-table-column prop="problemType" label="问题类型" width="160" show-overflow-tooltip />

        <el-table-column label="是否红线" width="100">
          <template #default="{ row }">
            {{ getOptionLabel(redLineOptions, row.redLine) }}
          </template>
        </el-table-column>

        <el-table-column
          prop="problemPosition"
          label="发现地点"
          width="180"
          show-overflow-tooltip
        />

        <el-table-column
          prop="implementDepartment"
          label="落实部门"
          width="160"
          show-overflow-tooltip
        />

        <el-table-column prop="dutyDepartment" label="责任部门" width="160" show-overflow-tooltip />

        <el-table-column prop="otherClassify" label="其他归类" width="160" show-overflow-tooltip />

        <el-table-column label="跨单位" width="90">
          <template #default="{ row }">
            {{ getOptionLabel(crossUnitOptions, row.crossUnit) }}
          </template>
        </el-table-column>

        <el-table-column label="业务指导" width="100">
          <template #default="{ row }">
            {{ getOptionLabel(businessGuidanceOptions, row.businessGuidance) }}
          </template>
        </el-table-column>

        <el-table-column label="路外" width="80">
          <template #default="{ row }">
            {{ getOptionLabel(outsideOptions, row.outside) }}
          </template>
        </el-table-column>

        <el-table-column
          prop="problemDescription"
          label="问题描述"
          width="320"
          show-overflow-tooltip
        />

        <el-table-column prop="deadline" label="整改时限" width="120" />

        <el-table-column label="整改要求" width="240" show-overflow-tooltip>
          <template #default="{ row }">
            {{ displayValue(row.rectificationRequirements) }}
          </template>
        </el-table-column>

        <el-table-column label="整改人" width="120">
          <template #default="{ row }">
            {{ displayValue(row.rectificationPerson) }}
          </template>
        </el-table-column>

        <el-table-column label="整改时间" width="170">
          <template #default="{ row }">
            {{ displayValue(row.rectificationTime) }}
          </template>
        </el-table-column>

        <el-table-column label="整改描述" width="260" show-overflow-tooltip>
          <template #default="{ row }">
            {{ displayValue(row.rectificationDescription) }}
          </template>
        </el-table-column>

        <el-table-column label="问题责任人" width="140">
          <template #default="{ row }">
            {{ displayValue(row.responsiblePerson) }}
          </template>
        </el-table-column>

        <el-table-column label="问题原因" width="240" show-overflow-tooltip>
          <template #default="{ row }">
            {{ displayValue(row.reason) }}
          </template>
        </el-table-column>

        <el-table-column label="销号人" width="120">
          <template #default="{ row }">
            {{ displayValue(row.closeIssuePerson) }}
          </template>
        </el-table-column>

        <el-table-column label="销号评价" width="240" show-overflow-tooltip>
          <template #default="{ row }">
            {{ displayValue(row.closeIssueEvaluate) }}
          </template>
        </el-table-column>

        <el-table-column label="销号时间" width="170">
          <template #default="{ row }">
            {{ displayValue(row.closeIssueTime) }}
          </template>
        </el-table-column>
      </el-table>

      <template v-if="previewResult.errors.length">
        <div class="section-title error-title">数据错误</div>

        <el-table :data="previewResult.errors" border max-height="220">
          <el-table-column prop="row" label="Excel 行" width="100" align="center" />

          <el-table-column prop="message" label="错误原因" min-width="400" />
        </el-table>
      </template>
    </template>

    <el-empty v-else description="请选择需要导入的问题 Excel 文件" />

    <template #footer>
      <el-button @click="visible = false"> 取消 </el-button>

      <el-button
        type="primary"
        :loading="importing"
        :disabled="!previewResult || previewResult.successCount === 0"
        @click="handleConfirmImport"
      >
        确认导入
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'

import { confirmProblemImport, selectProblemImportFile } from '@/api/problem'
import { useProblemDictionary } from '@/composables/useProblemDictionary'
import type { ProblemImportPreviewResult } from '@/types'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  success: []
}>()

const selecting = ref(false)
const importing = ref(false)

const previewResult = ref<ProblemImportPreviewResult | null>(null)

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

const {
  statusOptions,
  decomposedOptions,
  revisedOptions,
  assessedOptions,
  checkTypeOptions,
  checkWayOptions,
  riskLevelOptions,
  problemClassifyOptions,
  problemLabelOptions,
  redLineOptions,
  crossUnitOptions,
  businessGuidanceOptions,
  outsideOptions,
  loadDictionary,
  getOptionLabel,
} = useProblemDictionary()

function displayValue(value: string | null | undefined): string {
  return value || '-'
}

async function handleSelectFile() {
  selecting.value = true

  try {
    const response = await selectProblemImportFile()

    if (!response.success) {
      ElMessage.error(response.message || '选择文件失败')
      return
    }

    // 用户取消文件选择
    if (!response.data) {
      return
    }

    previewResult.value = response.data
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '选择文件失败')
  } finally {
    selecting.value = false
  }
}

async function handleConfirmImport() {
  if (!previewResult.value) {
    ElMessage.warning('请先选择需要导入的 Excel 文件')
    return
  }

  if (previewResult.value.successCount === 0) {
    ElMessage.warning('当前文件没有可导入的数据')
    return
  }

  importing.value = true

  try {
    const response = await confirmProblemImport()

    if (!response.success || !response.data) {
      ElMessage.error(response.message || '导入失败')
      return
    }

    const result = response.data

    if (result.failureCount > 0) {
      ElMessage.warning(`导入完成：成功 ${result.successCount} 条，失败 ${result.failureCount} 条`)
    } else {
      ElMessage.success(`成功导入 ${result.successCount} 条问题数据`)
    }

    emit('success')
    visible.value = false
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '导入失败')
  } finally {
    importing.value = false
  }
}

watch(
  () => props.modelValue,
  async (value) => {
    if (!value) {
      return
    }

    previewResult.value = null

    try {
      await loadDictionary()
    } catch (error) {
      ElMessage.error(error instanceof Error ? error.message : '加载问题字典失败')
    }
  },
)
</script>

<style scoped>
.import-toolbar {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.import-tip {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.file-alert {
  margin-bottom: 16px;
}

.statistics {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.statistics :deep(.el-statistic) {
  padding: 16px;
  background: var(--el-fill-color-light);
  border-radius: 6px;
}

.preview-alert {
  margin-bottom: 16px;
}

.section-title {
  margin: 16px 0 10px;
  font-size: 15px;
  font-weight: 600;
}

.error-title {
  color: var(--el-color-danger);
}
</style>
