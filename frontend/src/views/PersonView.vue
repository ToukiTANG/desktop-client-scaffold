<template>
  <div class="person-page">
    <el-card class="person-card">
      <!-- 顶部 -->
      <template #header>
        <div class="card-header">
          <span class="card-title"> 人员管理 </span>

          <el-button type="primary" @click="handleAdd"> 新增人员 </el-button>
        </div>
      </template>

      <!-- 查询区域 -->
      <div class="search-bar">
        <!-- 姓名 / 职名 -->
        <el-input
          v-model="query.keyword"
          placeholder="姓名 / 职名"
          clearable
          style="width: 180px"
          @keyup.enter="handleSearch"
        />

        <!-- 部门 -->
        <el-input
          v-model="query.department"
          placeholder="部门"
          clearable
          style="width: 180px"
          @keyup.enter="handleSearch"
        />

        <!-- 身份类型 -->
        <el-select v-model="query.identity" placeholder="身份类型" clearable style="width: 150px">
          <el-option
            v-for="item in identityOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>

        <!-- 专业分类 -->
        <el-select
          v-model="query.specializeClassify"
          placeholder="专业分类"
          clearable
          style="width: 140px"
        >
          <el-option
            v-for="item in specializeClassifyOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>

        <!-- 学历 -->
        <el-input
          v-model="query.education"
          placeholder="学历"
          clearable
          style="width: 140px"
          @keyup.enter="handleSearch"
        />

        <!-- 性别 -->
        <el-select v-model="query.gender" placeholder="性别" clearable style="width: 100px">
          <el-option
            v-for="item in genderOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>

        <!-- 生产组分类 -->
        <el-select
          v-model="query.productionGroupClassify"
          placeholder="生产组分类"
          clearable
          style="width: 220px"
        >
          <el-option
            v-for="item in productionGroupClassifyOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>

        <el-button type="primary" @click="handleSearch"> 查询 </el-button>

        <el-button @click="handleReset"> 重置 </el-button>
      </div>

      <!-- 表格 -->
      <div class="table-wrapper">
        <el-table v-loading="loading" :data="persons" border stripe height="100%">
          <el-table-column prop="name" label="姓名" width="100" />

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

          <el-table-column label="生产组分类" min-width="220" show-overflow-tooltip>
            <template #default="{ row }">
              {{ getOptionLabel(productionGroupClassifyOptions, row.productionGroupClassify) }}
            </template>
          </el-table-column>

          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="handleEdit(row)"> 编辑 </el-button>

              <el-button type="danger" link @click="handleDelete(row)"> 删除 </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="query.page"
          v-model:page-size="query.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next"
          @current-change="loadPersons"
          @size-change="handlePageSizeChange"
        />
      </div>
    </el-card>

    <!-- 新增 / 编辑 -->
    <PersonFormDialog
      v-model="dialogVisible"
      :person="currentPerson"
      @success="handleDialogSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'

import { ElMessage, ElMessageBox } from 'element-plus'

import { deletePerson, getPersonList } from '@/api/person'

import {
  genderOptions,
  identityOptions,
  specializeClassifyOptions,
  productionGroupClassifyOptions,
  getOptionLabel,
} from '@/constants/person'

import PersonFormDialog from '@/components/person/PersonFormDialog.vue'

import type { Person, PersonQuery } from '@/types'

const loading = ref(false)

const persons = ref<Person[]>([])

const total = ref(0)

const dialogVisible = ref(false)

const currentPerson = ref<Person | null>(null)

const query = reactive<PersonQuery>({
  keyword: '',
  department: '',

  identity: undefined,
  specializeClassify: undefined,

  education: '',

  gender: undefined,

  productionGroupClassify: undefined,

  page: 1,
  pageSize: 20,
})

/**
 * 查询人员列表
 */
async function loadPersons() {
  loading.value = true

  try {
    const response = await getPersonList({
      ...query,
    })

    if (!response.success) {
      ElMessage.error(response.message || '查询人员失败')

      return
    }

    persons.value = response.data.items

    total.value = response.data.total
  } catch (error) {
    console.error(error)

    ElMessage.error('查询人员失败')
  } finally {
    loading.value = false
  }
}

/**
 * 查询
 */
function handleSearch() {
  query.page = 1

  loadPersons()
}

/**
 * 重置
 */
function handleReset() {
  query.keyword = ''
  query.department = ''

  query.identity = undefined
  query.specializeClassify = undefined

  query.education = ''

  query.gender = undefined

  query.productionGroupClassify = undefined

  query.page = 1

  loadPersons()
}

/**
 * 每页数量变化
 */
function handlePageSizeChange() {
  query.page = 1

  loadPersons()
}

/**
 * 新增人员
 */
function handleAdd() {
  currentPerson.value = null

  dialogVisible.value = true
}

/**
 * 编辑人员
 */
function handleEdit(person: Person) {
  currentPerson.value = person

  dialogVisible.value = true
}

/**
 * 删除人员
 */
async function handleDelete(person: Person) {
  try {
    await ElMessageBox.confirm(`确定要删除“${person.name}”吗？`, '删除确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
  } catch {
    return
  }

  try {
    const response = await deletePerson(person.id)

    if (!response.success) {
      ElMessage.error(response.message || '删除失败')

      return
    }

    ElMessage.success(response.message || '删除成功')

    /**
     * 当前页只有最后一条数据时，
     * 删除后自动回到上一页。
     */
    if (persons.value.length === 1 && query.page > 1) {
      query.page -= 1
    }

    await loadPersons()
  } catch (error) {
    console.error(error)

    ElMessage.error('删除人员失败')
  }
}

/**
 * 新增 / 编辑成功后重新查询。
 */
function handleDialogSuccess() {
  loadPersons()
}

onMounted(() => {
  loadPersons()
})
</script>

<style scoped>
.person-page {
  width: 100%;
  height: 100%;
  min-width: 0;
  min-height: 0;
}

.person-card {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.person-card :deep(.el-card__body) {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
}

.search-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  flex-shrink: 0;
  margin-bottom: 16px;
}

.table-wrapper {
  flex: 1;
  min-height: 0;
}

.pagination {
  display: flex;
  flex-shrink: 0;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
