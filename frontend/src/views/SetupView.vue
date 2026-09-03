<template>
  <div class="setup-page">
    <el-card class="setup-card" shadow="never">
      <div class="setup-header">
        <h2>初始化配置</h2>
        <p>请选择当前设备对应的车间和公寓</p>
      </div>

      <el-form :model="form" label-position="top" @submit.prevent>
        <el-form-item label="车间">
          <el-select v-model="form.workshop" placeholder="请选择车间" style="width: 100%" @change="handleWorkshopChange">
            <el-option v-for="item in workshopOptions" :key="item.workshop" :label="item.workshop" :value="item.workshop" />
          </el-select>
        </el-form-item>

        <el-form-item label="公寓">
          <el-select v-model="form.apartment" placeholder="请选择公寓" style="width: 100%" :disabled="!form.workshop">
            <el-option v-for="item in apartmentOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>

        <el-button type="primary" style="width: 100%" :disabled="!canSubmit" :loading="submitting" @click="handleSubmit"> 确认并进入 </el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

import { saveAppConfig } from '@/api/appConfig'
import type { AppConfig } from '@/types'

interface WorkshopOption {
  workshop: string
  apartment: string[]
}

const router = useRouter()

const submitting = ref(false)

const form = reactive<AppConfig>({
  workshop: '',
  apartment: '',
})

const workshopOptions: WorkshopOption[] = [
  {
    workshop: '广元公寓车间',
    apartment: ['车间', '广元公寓', '广元西公寓', '江油公寓'],
  },
  {
    workshop: '成都北公寓车间',
    apartment: ['车间', '成都北公寓', '成都客机公寓', '成都西动车组司机间休室', '燕岗公寓', '乐山公寓', '安靖动车组司机间休室'],
  },
  {
    workshop: '成都公寓车间',
    apartment: [
      '车间',
      '成都公寓',
      '成都动车公寓',
      '成都东机车公寓',
      '成都东客车公寓',
      '安靖动车组司机间休室',
      '雅安公寓',
      '天府动车公寓',
      '龙泉驿公寓筹备组',
      '天全保障组',
    ],
  },
  {
    workshop: '松潘房建公寓车间',
    apartment: ['车间', '广汉公寓', '茂县公寓'],
  },
  {
    workshop: '西昌房建公寓车间',
    apartment: ['车间', '普雄公寓', '西昌公寓', '西昌西公寓'],
  },
  {
    workshop: '攀枝花房建公寓车间',
    apartment: ['车间', '攀枝花南机务公寓', '密地公寓', '攀枝花公寓', '攀枝花南公寓'],
  },
]

const apartmentOptions = computed(() => {
  const workshop = workshopOptions.find((item) => item.workshop === form.workshop)

  return workshop?.apartment ?? []
})

const canSubmit = computed(() => {
  return Boolean(form.workshop && form.apartment && !submitting.value)
})

function handleWorkshopChange() {
  form.apartment = ''
}

async function handleSubmit() {
  if (!canSubmit.value) {
    return
  }

  submitting.value = true

  try {
    const response = await saveAppConfig(form.workshop, form.apartment)

    if (!response.success) {
      ElMessage.error(response.message || '配置保存失败')
      return
    }

    ElMessage.success('配置保存成功')

    await router.replace({
      name: 'home',
    })
  } catch (error) {
    console.error('保存初始化配置失败:', error)
    ElMessage.error('配置保存失败')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.setup-page {
  width: 100%;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
}

.setup-card {
  width: 420px;
  border-radius: 12px;
}

.setup-header {
  margin-bottom: 28px;
  text-align: center;
}

.setup-header h2 {
  margin: 0 0 8px;
  font-size: 22px;
  font-weight: 600;
}

.setup-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}
</style>
