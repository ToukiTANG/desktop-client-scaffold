<template>
  <el-dialog
    :model-value="modelValue"
    :title="dialogTitle"
    width="560px"
    destroy-on-close
    @close="handleClose"
    @open="handleOpen"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="110px" status-icon>
      <!-- 姓名 -->
      <el-form-item label="姓名" prop="name">
        <el-input v-model="form.name" placeholder="请输入姓名" maxlength="50" clearable />
      </el-form-item>

      <!-- 性别 -->
      <el-form-item label="性别" prop="gender">
        <el-radio-group v-model="form.gender">
          <el-radio v-for="item in genderOptions" :key="item.value" :value="item.value">
            {{ item.label }}
          </el-radio>
        </el-radio-group>
      </el-form-item>

      <!-- 部门 -->
      <el-form-item label="部门" prop="department">
        <el-input v-model="form.department" placeholder="请输入部门" maxlength="255" clearable />
      </el-form-item>

      <!-- 职名 -->
      <el-form-item label="职名" prop="jobTitle">
        <el-input v-model="form.jobTitle" placeholder="请输入职名" maxlength="255" clearable />
      </el-form-item>

      <!-- 身份类型 -->
      <el-form-item label="身份类型" prop="identity">
        <el-select
          v-model="form.identity"
          placeholder="请选择身份类型"
          clearable
          style="width: 100%"
        >
          <el-option
            v-for="item in identityOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
      </el-form-item>

      <!-- 专业分类 -->
      <el-form-item label="专业分类" prop="specializeClassify">
        <el-select
          v-model="form.specializeClassify"
          placeholder="请选择专业分类"
          clearable
          style="width: 100%"
        >
          <el-option
            v-for="item in specializeClassifyOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
      </el-form-item>

      <!-- 学历 -->
      <el-form-item label="学历" prop="education">
        <el-input v-model="form.education" placeholder="请输入学历" maxlength="255" clearable />
      </el-form-item>

      <!-- 生产组分类 -->
      <el-form-item label="生产组分类" prop="productionGroupClassify">
        <el-select
          v-model="form.productionGroupClassify"
          placeholder="请选择生产组分类"
          clearable
          style="width: 100%"
        >
          <el-option
            v-for="item in productionGroupClassifyOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button :disabled="submitting" @click="handleClose"> 取消 </el-button>

        <el-button type="primary" :loading="submitting" @click="handleSubmit"> 保存 </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'

import { ElMessage, type FormInstance, type FormRules } from 'element-plus'

import { createPerson, updatePerson } from '@/api/person'

import { usePersonDictionary } from '@/composables/usePersonDictionary'

import type { Person, PersonForm } from '@/types'

const {
  genderOptions,
  identityOptions,
  specializeClassifyOptions,
  productionGroupClassifyOptions,
  loadDictionary,
} = usePersonDictionary()

const props = defineProps<{
  modelValue: boolean
  person: Person | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  success: []
}>()

const formRef = ref<FormInstance>()

const submitting = ref(false)

/**
 * 创建空表单。
 */
const createEmptyForm = (): PersonForm => ({
  name: '',
  department: '',
  jobTitle: '',

  identity: null,
  specializeClassify: null,

  education: '',

  gender: null,

  productionGroupClassify: null,
})

const form = reactive<PersonForm>(createEmptyForm())

const dialogTitle = computed(() => {
  return props.person ? '编辑人员' : '新增人员'
})

const rules: FormRules<PersonForm> = {
  name: [
    {
      required: true,
      message: '请输入姓名',
      trigger: 'blur',
    },
  ],

  gender: [
    {
      required: true,
      message: '请选择性别',
      trigger: 'change',
    },
  ],

  department: [
    {
      required: true,
      message: '请输入部门',
      trigger: 'blur',
    },
  ],

  jobTitle: [
    {
      required: true,
      message: '请输入职名',
      trigger: 'blur',
    },
  ],

  identity: [
    {
      required: true,
      message: '请选择身份类型',
      trigger: 'change',
    },
  ],

  specializeClassify: [
    {
      required: true,
      message: '请选择专业分类',
      trigger: 'change',
    },
  ],
}

/**
 * 重置表单。
 */
function resetForm() {
  Object.assign(form, createEmptyForm())
}

/**
 * Dialog 打开时初始化数据。
 */
async function handleOpen() {
  resetForm()

  try {
    await loadDictionary()
  } catch (error) {
    console.error(error)

    ElMessage.error('加载人员业务字典失败')
  }

  if (props.person) {
    Object.assign(form, {
      name: props.person.name,
      department: props.person.department,
      jobTitle: props.person.jobTitle,
      identity: props.person.identity,
      specializeClassify: props.person.specializeClassify,
      education: props.person.education ?? '',
      gender: props.person.gender,
      productionGroupClassify: props.person.productionGroupClassify,
    })
  }

  formRef.value?.clearValidate()
}

/**
 * 关闭 Dialog。
 */
function handleClose() {
  emit('update:modelValue', false)
}

/**
 * 提交表单。
 */
async function handleSubmit() {
  if (!formRef.value) {
    return
  }

  const valid = await formRef.value.validate().catch(() => false)

  if (!valid) {
    return
  }

  submitting.value = true

  try {
    const response = props.person
      ? await updatePerson(props.person.id, {
          ...form,
        })
      : await createPerson({
          ...form,
        })

    if (!response.success) {
      ElMessage.error(response.message || '保存失败')

      return
    }

    ElMessage.success(props.person ? '修改成功' : '新增成功')

    emit('success')

    handleClose()
  } catch (error) {
    console.error(error)

    ElMessage.error('保存人员失败')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
