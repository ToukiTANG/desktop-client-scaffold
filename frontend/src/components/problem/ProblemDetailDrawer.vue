<script setup lang="ts">
import { computed } from 'vue'

import { useProblemDictionary } from '@/composables/useProblemDictionary'
import type { CheckProblem } from '@/types'

const props = defineProps<{
  modelValue: boolean
  problem: CheckProblem | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

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
  getOptionLabel,
} = useProblemDictionary()

function displayValue(value: string | null | undefined): string {
  return value || '-'
}
</script>

<template>
  <el-drawer v-model="visible" title="问题详情" size="70%" destroy-on-close>
    <template v-if="problem">
      <el-descriptions title="基础状态" :column="4" border>
        <el-descriptions-item label="ID">
          {{ problem.id }}
        </el-descriptions-item>

        <el-descriptions-item label="状态">
          {{ getOptionLabel(statusOptions, problem.status) }}
        </el-descriptions-item>

        <el-descriptions-item label="是否已分解">
          {{ getOptionLabel(decomposedOptions, problem.decomposed) }}
        </el-descriptions-item>

        <el-descriptions-item label="是否已修订">
          {{ getOptionLabel(revisedOptions, problem.revised) }}
        </el-descriptions-item>

        <el-descriptions-item label="是否已考核">
          {{ getOptionLabel(assessedOptions, problem.assessed) }}
        </el-descriptions-item>
      </el-descriptions>

      <el-descriptions class="detail-section" title="检查信息" :column="3" border>
        <el-descriptions-item label="检查部门">
          {{ problem.checkDepartment }}
        </el-descriptions-item>

        <el-descriptions-item label="检查人员">
          {{ problem.checkPerson }}
        </el-descriptions-item>

        <el-descriptions-item label="检查类型">
          {{ getOptionLabel(checkTypeOptions, problem.checkType) }}
        </el-descriptions-item>

        <el-descriptions-item label="检查方式">
          {{ getOptionLabel(checkWayOptions, problem.checkWay) }}
        </el-descriptions-item>

        <el-descriptions-item label="检查开始时间">
          {{ problem.checkStartTime }}
        </el-descriptions-item>

        <el-descriptions-item label="检查结束时间">
          {{ problem.checkEndTime }}
        </el-descriptions-item>

        <el-descriptions-item label="提交时间">
          {{ problem.submitTime }}
        </el-descriptions-item>
      </el-descriptions>

      <el-descriptions class="detail-section" title="问题信息" :column="3" border>
        <el-descriptions-item label="问题项点">
          {{ problem.problemItem }}
        </el-descriptions-item>

        <el-descriptions-item label="后果明示">
          {{ problem.consequences }}
        </el-descriptions-item>

        <el-descriptions-item label="风险类型">
          {{ problem.riskType }}
        </el-descriptions-item>

        <el-descriptions-item label="风险等级">
          {{ getOptionLabel(riskLevelOptions, problem.riskLevel) }}
        </el-descriptions-item>

        <el-descriptions-item label="问题归类">
          {{ getOptionLabel(problemClassifyOptions, problem.problemClassify) }}
        </el-descriptions-item>

        <el-descriptions-item label="问题分项">
          {{ getOptionLabel(problemLabelOptions, problem.problemLabel) }}
        </el-descriptions-item>

        <el-descriptions-item label="问题加分">
          {{ problem.problemExtraPoints }}
        </el-descriptions-item>

        <el-descriptions-item label="问题类型">
          {{ problem.problemType }}
        </el-descriptions-item>

        <el-descriptions-item label="是否红线">
          {{ getOptionLabel(redLineOptions, problem.redLine) }}
        </el-descriptions-item>

        <el-descriptions-item label="发现地点">
          {{ problem.problemPosition }}
        </el-descriptions-item>

        <el-descriptions-item label="落实部门">
          {{ problem.implementDepartment }}
        </el-descriptions-item>

        <el-descriptions-item label="责任部门">
          {{ problem.dutyDepartment }}
        </el-descriptions-item>

        <el-descriptions-item label="其他归类">
          {{ problem.otherClassify }}
        </el-descriptions-item>

        <el-descriptions-item label="是否跨单位">
          {{ getOptionLabel(crossUnitOptions, problem.crossUnit) }}
        </el-descriptions-item>

        <el-descriptions-item label="是否业务指导">
          {{ getOptionLabel(businessGuidanceOptions, problem.businessGuidance) }}
        </el-descriptions-item>

        <el-descriptions-item label="是否路外">
          {{ getOptionLabel(outsideOptions, problem.outside) }}
        </el-descriptions-item>

        <el-descriptions-item label="问题描述" :span="3">
          {{ problem.problemDescription }}
        </el-descriptions-item>
      </el-descriptions>

      <el-descriptions class="detail-section" title="整改信息" :column="3" border>
        <el-descriptions-item label="整改时限">
          {{ problem.deadline }}
        </el-descriptions-item>

        <el-descriptions-item label="整改要求" :span="2">
          {{ displayValue(problem.rectificationRequirements) }}
        </el-descriptions-item>

        <el-descriptions-item label="整改人">
          {{ displayValue(problem.rectificationPerson) }}
        </el-descriptions-item>

        <el-descriptions-item label="整改时间">
          {{ displayValue(problem.rectificationTime) }}
        </el-descriptions-item>

        <el-descriptions-item label="整改描述" :span="3">
          {{ displayValue(problem.rectificationDescription) }}
        </el-descriptions-item>

        <el-descriptions-item label="问题责任人">
          {{ displayValue(problem.responsiblePerson) }}
        </el-descriptions-item>

        <el-descriptions-item label="问题原因" :span="2">
          {{ displayValue(problem.reason) }}
        </el-descriptions-item>
      </el-descriptions>

      <el-descriptions class="detail-section" title="销号信息" :column="3" border>
        <el-descriptions-item label="销号人">
          {{ displayValue(problem.closeIssuePerson) }}
        </el-descriptions-item>

        <el-descriptions-item label="销号时间">
          {{ displayValue(problem.closeIssueTime) }}
        </el-descriptions-item>

        <el-descriptions-item label="销号评价" :span="3">
          {{ displayValue(problem.closeIssueEvaluate) }}
        </el-descriptions-item>
      </el-descriptions>
    </template>
  </el-drawer>
</template>

<style scoped>
.detail-section {
  margin-top: 24px;
}

:deep(.el-descriptions__label) {
  width: 120px;
}
</style>
