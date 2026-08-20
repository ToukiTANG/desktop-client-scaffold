import { computed, readonly, ref } from 'vue'

import { getPersonDictionary } from '@/api/person'

import type { DictionaryOption, PersonDictionary } from '@/types'

const dictionary = ref<PersonDictionary>({
  gender: [],
  identity: [],
  specializeClassify: [],
  productionGroupClassify: [],
})

const loading = ref(false)

const loaded = ref(false)

let loadingPromise: Promise<void> | null = null

/**
 * 加载人员业务字典。
 *
 * 整个前端生命周期只请求一次。
 */
async function loadDictionary(): Promise<void> {
  if (loaded.value) {
    return
  }

  /**
   * 如果多个组件同时调用，
   * 复用同一个 Promise，避免重复请求。
   */
  if (loadingPromise) {
    return loadingPromise
  }

  loading.value = true

  loadingPromise = (async () => {
    try {
      const response = await getPersonDictionary()

      if (!response.success) {
        throw new Error(response.message || '获取人员字典失败')
      }

      dictionary.value = response.data

      loaded.value = true
    } finally {
      loading.value = false
      loadingPromise = null
    }
  })()

  return loadingPromise
}

/**
 * 根据 value 获取对应的中文显示文本。
 */
function getOptionLabel(options: DictionaryOption[], value: number | null | undefined): string {
  if (value === null || value === undefined) {
    return '-'
  }

  return options.find((item) => item.value === value)?.label ?? '-'
}

export function usePersonDictionary() {
  const genderOptions = computed(() => dictionary.value.gender)

  const identityOptions = computed(() => dictionary.value.identity)

  const specializeClassifyOptions = computed(() => dictionary.value.specializeClassify)

  const productionGroupClassifyOptions = computed(() => dictionary.value.productionGroupClassify)

  return {
    dictionary: readonly(dictionary),

    loading: readonly(loading),

    loaded: readonly(loaded),

    genderOptions,
    identityOptions,
    specializeClassifyOptions,
    productionGroupClassifyOptions,

    loadDictionary,
    getOptionLabel,
  }
}
