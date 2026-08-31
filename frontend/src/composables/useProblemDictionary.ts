import { computed, readonly, ref } from 'vue'

import { getProblemDictionary } from '@/api/problem'
import type { DictionaryOption, ProblemDictionary } from '@/types'

const dictionary = ref<ProblemDictionary>({
  status: [],
  decomposed: [],
  revised: [],
  assessed: [],
  checkType: [],
  checkWay: [],
  riskLevel: [],
  problemClassify: [],
  problemLabel: [],
  redLine: [],
  crossUnit: [],
  businessGuidance: [],
  outside: [],
})

const loading = ref(false)
const loaded = ref(false)

let loadingPromise: Promise<void> | null = null

async function loadDictionary(): Promise<void> {
  if (loaded.value) {
    return
  }

  if (loadingPromise) {
    return loadingPromise
  }

  loading.value = true

  loadingPromise = (async () => {
    try {
      const response = await getProblemDictionary()

      if (!response.success || !response.data) {
        throw new Error(response.message || '加载问题字典失败')
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

function getOptionLabel(options: DictionaryOption[], value: number | null | undefined): string {
  if (value === null || value === undefined) {
    return '-'
  }

  return options.find((item) => item.value === value)?.label ?? '-'
}

export function useProblemDictionary() {
  const statusOptions = computed(() => dictionary.value.status)
  const decomposedOptions = computed(() => dictionary.value.decomposed)
  const revisedOptions = computed(() => dictionary.value.revised)
  const assessedOptions = computed(() => dictionary.value.assessed)

  const checkTypeOptions = computed(() => dictionary.value.checkType)
  const checkWayOptions = computed(() => dictionary.value.checkWay)

  const riskLevelOptions = computed(() => dictionary.value.riskLevel)
  const problemClassifyOptions = computed(() => dictionary.value.problemClassify)
  const problemLabelOptions = computed(() => dictionary.value.problemLabel)

  const redLineOptions = computed(() => dictionary.value.redLine)
  const crossUnitOptions = computed(() => dictionary.value.crossUnit)
  const businessGuidanceOptions = computed(() => dictionary.value.businessGuidance)
  const outsideOptions = computed(() => dictionary.value.outside)

  return {
    dictionary: readonly(dictionary),
    loading: readonly(loading),
    loaded: readonly(loaded),

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
  }
}
