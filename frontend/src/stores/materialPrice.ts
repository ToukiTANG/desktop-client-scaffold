import { reactive, readonly } from 'vue'

import { getMaterialPrices } from '@/api/materialPrice'

import type { MaterialPrice } from '@/types'

interface MaterialPriceState {
  materials: MaterialPrice[]
  loading: boolean
  loaded: boolean
  error: string | null
  loadedAt: Date | null
}

const state = reactive<MaterialPriceState>({
  materials: [],
  loading: false,
  loaded: false,
  error: null,
  loadedAt: null,
})

let loadingPromise: Promise<boolean> | null = null

async function loadMaterialPrices(force = false): Promise<boolean> {
  // 已加载过，不重复访问 NAS
  if (state.loaded && !force) {
    return true
  }

  // 防止启动阶段多个组件同时触发导致重复请求
  if (loadingPromise) {
    return await loadingPromise
  }

  loadingPromise = doLoadMaterialPrices()

  try {
    return await loadingPromise
  } finally {
    loadingPromise = null
  }
}

async function doLoadMaterialPrices(): Promise<boolean> {
  state.loading = true
  state.error = null

  try {
    const response = await getMaterialPrices()

    if (!response.success) {
      state.materials = []
      state.error = response.message || '材料价格表读取失败'

      return false
    }

    state.materials = response.data ?? []
    state.loaded = true
    state.loadedAt = new Date()

    return true
  } catch (error) {
    console.error('Failed to load material prices:', error)

    state.materials = []
    state.error = '材料价格表读取失败'

    return false
  } finally {
    state.loading = false
  }
}

async function refreshMaterialPrices(): Promise<boolean> {
  return await loadMaterialPrices(true)
}

export const materialPriceStore = {
  state: readonly(state),
  load: loadMaterialPrices,
  refresh: refreshMaterialPrices,
}
