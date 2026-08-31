<template>
  <div class="problem-page">
    <el-card class="filter-card">
      <el-form :model="query" inline>
        <el-form-item label="关键词">
          <el-input
            v-model="query.keyword"
            clearable
            placeholder="问题描述 / 项点 / 部门 / 人员"
            style="width: 240px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>

        <el-form-item label="状态">
          <el-select v-model="query.status" clearable placeholder="全部" style="width: 130px">
            <el-option
              v-for="item in statusOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="检查部门">
          <el-input
            v-model="query.checkDepartment"
            clearable
            placeholder="检查部门"
            style="width: 160px"
          />
        </el-form-item>

        <el-form-item label="检查人员">
          <el-input
            v-model="query.checkPerson"
            clearable
            placeholder="检查人员"
            style="width: 140px"
          />
        </el-form-item>

        <el-form-item label="检查类型">
          <el-select v-model="query.checkType" clearable placeholder="全部" style="width: 190px">
            <el-option
              v-for="item in checkTypeOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="检查方式">
          <el-select v-model="query.checkWay" clearable placeholder="全部" style="width: 160px">
            <el-option
              v-for="item in checkWayOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="风险等级">
          <el-select v-model="query.riskLevel" clearable placeholder="全部" style="width: 150px">
            <el-option
              v-for="item in riskLevelOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="问题归类">
          <el-select
            v-model="query.problemClassify"
            clearable
            placeholder="全部"
            style="width: 150px"
          >
            <el-option
              v-for="item in problemClassifyOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="问题分项">
          <el-select v-model="query.problemLabel" clearable placeholder="全部" style="width: 110px">
            <el-option
              v-for="item in problemLabelOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="红线">
          <el-select v-model="query.redLine" clearable placeholder="全部" style="width: 100px">
            <el-option
              v-for="item in redLineOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSearch"> 查询 </el-button>

          <el-button type="success" @click="importVisible = true"> 导入 </el-button>

          <el-button @click="handleReset"> 重置 </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="problems"
        border
        stripe
        height="calc(100vh - 300px)"
        style="width: 100%"
      >
        <!-- 基础状态 -->

        <el-table-column prop="id" label="ID" width="80" fixed="left" align="center" />

        <el-table-column label="状态" width="100" fixed="left" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">
              {{ getOptionLabel(statusOptions, row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="已分解" width="90" align="center">
          <template #default="{ row }">
            {{ getOptionLabel(decomposedOptions, row.decomposed) }}
          </template>
        </el-table-column>

        <el-table-column label="已修订" width="90" align="center">
          <template #default="{ row }">
            {{ getOptionLabel(revisedOptions, row.revised) }}
          </template>
        </el-table-column>

        <el-table-column label="已考核" width="90" align="center">
          <template #default="{ row }">
            {{ getOptionLabel(assessedOptions, row.assessed) }}
          </template>
        </el-table-column>

        <!-- 检查信息 -->

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

        <el-table-column label="检查方式" width="150" show-overflow-tooltip>
          <template #default="{ row }">
            {{ getOptionLabel(checkWayOptions, row.checkWay) }}
          </template>
        </el-table-column>

        <el-table-column prop="checkStartTime" label="检查开始时间" width="170" align="center" />

        <el-table-column prop="checkEndTime" label="检查结束时间" width="170" align="center" />

        <el-table-column prop="submitTime" label="提交时间" width="170" align="center" />

        <!-- 问题信息 -->

        <el-table-column prop="problemItem" label="问题项点" width="200" show-overflow-tooltip />

        <el-table-column prop="consequences" label="后果明示" width="200" show-overflow-tooltip />

        <el-table-column prop="riskType" label="风险类型" width="160" show-overflow-tooltip />

        <el-table-column label="风险等级" width="130" align="center">
          <template #default="{ row }">
            <el-tag :type="getRiskTagType(row.riskLevel)" effect="plain">
              {{ getOptionLabel(riskLevelOptions, row.riskLevel) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="问题归类" width="130" align="center">
          <template #default="{ row }">
            {{ getOptionLabel(problemClassifyOptions, row.problemClassify) }}
          </template>
        </el-table-column>

        <el-table-column label="问题分项" width="100" align="center">
          <template #default="{ row }">
            {{ getOptionLabel(problemLabelOptions, row.problemLabel) }}
          </template>
        </el-table-column>

        <el-table-column prop="problemExtraPoints" label="问题加分" width="110" align="center" />

        <el-table-column prop="problemType" label="问题类型" width="160" show-overflow-tooltip />

        <el-table-column label="是否红线" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.redLine === 1 ? 'danger' : 'info'" effect="plain">
              {{ getOptionLabel(redLineOptions, row.redLine) }}
            </el-tag>
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

        <!-- 业务属性 -->

        <el-table-column label="跨单位" width="90" align="center">
          <template #default="{ row }">
            {{ getOptionLabel(crossUnitOptions, row.crossUnit) }}
          </template>
        </el-table-column>

        <el-table-column label="业务指导" width="100" align="center">
          <template #default="{ row }">
            {{ getOptionLabel(businessGuidanceOptions, row.businessGuidance) }}
          </template>
        </el-table-column>

        <el-table-column label="路外" width="80" align="center">
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

        <!-- 整改信息 -->

        <el-table-column prop="deadline" label="整改时限" width="120" align="center" />

        <el-table-column label="整改要求" width="240" show-overflow-tooltip>
          <template #default="{ row }">
            {{ displayValue(row.rectificationRequirements) }}
          </template>
        </el-table-column>

        <el-table-column label="整改人" width="120" show-overflow-tooltip>
          <template #default="{ row }">
            {{ displayValue(row.rectificationPerson) }}
          </template>
        </el-table-column>

        <el-table-column label="整改时间" width="170" align="center">
          <template #default="{ row }">
            {{ displayValue(row.rectificationTime) }}
          </template>
        </el-table-column>

        <el-table-column label="整改描述" width="260" show-overflow-tooltip>
          <template #default="{ row }">
            {{ displayValue(row.rectificationDescription) }}
          </template>
        </el-table-column>

        <!-- 责任信息 -->

        <el-table-column label="问题责任人" width="140" show-overflow-tooltip>
          <template #default="{ row }">
            {{ displayValue(row.responsiblePerson) }}
          </template>
        </el-table-column>

        <el-table-column label="问题原因" width="240" show-overflow-tooltip>
          <template #default="{ row }">
            {{ displayValue(row.reason) }}
          </template>
        </el-table-column>

        <!-- 销号信息 -->

        <el-table-column label="销号人" width="120" show-overflow-tooltip>
          <template #default="{ row }">
            {{ displayValue(row.closeIssuePerson) }}
          </template>
        </el-table-column>

        <el-table-column label="销号评价" width="240" show-overflow-tooltip>
          <template #default="{ row }">
            {{ displayValue(row.closeIssueEvaluate) }}
          </template>
        </el-table-column>

        <el-table-column label="销号时间" width="170" align="center">
          <template #default="{ row }">
            {{ displayValue(row.closeIssueTime) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="100" fixed="right" align="center">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleViewDetail(row)"> 查看详情 </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="query.page"
          v-model:page-size="query.pageSize"
          :total="total"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="handlePageChange"
          @size-change="handlePageSizeChange"
        />
      </div>
    </el-card>

    <ProblemImportDialog v-model="importVisible" @success="handleImportSuccess" />
    <ProblemDetailDrawer v-model="detailVisible" :problem="currentProblem" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'

import { getProblemList } from '@/api/problem'
import { useProblemDictionary } from '@/composables/useProblemDictionary'
import ProblemImportDialog from '@/components/problem/ProblemImportDialog.vue'
import ProblemDetailDrawer from '@/components/problem/ProblemDetailDrawer.vue'
import type { CheckProblem, CheckProblemQuery } from '@/types'

const loading = ref(false)
const problems = ref<CheckProblem[]>([])
const total = ref(0)
const importVisible = ref(false)

const detailVisible = ref(false)
const currentProblem = ref<CheckProblem | null>(null)

function handleViewDetail(row: CheckProblem) {
  currentProblem.value = row
  detailVisible.value = true
}

const query = reactive<CheckProblemQuery>({
  keyword: '',
  status: undefined,
  checkDepartment: '',
  checkPerson: '',
  checkType: undefined,
  checkWay: undefined,
  riskLevel: undefined,
  problemClassify: undefined,
  problemLabel: undefined,
  redLine: undefined,
  page: 1,
  pageSize: 20,
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

async function loadProblems() {
  loading.value = true

  try {
    const response = await getProblemList(query)

    if (!response.success || !response.data) {
      ElMessage.error(response.message || '加载问题列表失败')
      return
    }

    problems.value = response.data.items
    total.value = response.data.total
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '加载问题列表失败')
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  query.page = 1
  loadProblems()
}

function handleReset() {
  query.keyword = ''
  query.status = undefined
  query.checkDepartment = ''
  query.checkPerson = ''
  query.checkType = undefined
  query.checkWay = undefined
  query.riskLevel = undefined
  query.problemClassify = undefined
  query.problemLabel = undefined
  query.redLine = undefined
  query.page = 1

  loadProblems()
}

function handlePageChange(page: number) {
  query.page = page
  loadProblems()
}

function handlePageSizeChange(pageSize: number) {
  query.pageSize = pageSize
  query.page = 1
  loadProblems()
}

function getStatusTagType(status: number) {
  switch (status) {
    case 0:
      return 'warning'
    case 1:
      return 'primary'
    case 2:
      return 'success'
    default:
      return 'info'
  }
}

function getRiskTagType(riskLevel: number) {
  switch (riskLevel) {
    case 3:
      return 'danger'
    case 1:
      return 'warning'
    case 2:
      return 'primary'
    default:
      return 'info'
  }
}

function displayValue(value: string | null | undefined) {
  return value || '-'
}

function handleImportSuccess() {
  query.page = 1
  loadProblems()
}

onMounted(async () => {
  try {
    await loadDictionary()
    await loadProblems()
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '页面初始化失败')
  }
})
</script>

<style scoped>
.problem-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.filter-card :deep(.el-card__body) {
  padding-bottom: 2px;
}

.table-card :deep(.el-card__body) {
  padding-bottom: 16px;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
