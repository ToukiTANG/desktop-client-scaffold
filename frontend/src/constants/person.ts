export const genderOptions = [
  {
    label: '男',
    value: 0,
  },
  {
    label: '女',
    value: 1,
  },
]

export const identityOptions = [
  {
    label: '干部',
    value: 0,
  },
  {
    label: '干部（领导）',
    value: 1,
  },
  {
    label: '工人',
    value: 2,
  },
  {
    label: '工人代干',
    value: 3,
  },
  {
    label: '工人锻炼',
    value: 4,
  },
]

export const specializeClassifyOptions = [
  {
    label: '段部',
    value: 0,
  },
  {
    label: '房建',
    value: 1,
  },
  {
    label: '公寓',
    value: 2,
  },
]

export const productionGroupClassifyOptions = [
  {
    label: '普速铁路房建设备巡检维修人员',
    value: 0,
  },
  {
    label: '高速铁路房建设备巡检维修人员',
    value: 1,
  },
  {
    label: '行车公寓人员',
    value: 2,
  },
]

export interface OptionItem {
  label: string
  value: number
}

export function getOptionLabel(options: OptionItem[], value: number | null | undefined): string {
  if (value === null || value === undefined) {
    return '-'
  }

  return options.find((item) => item.value === value)?.label ?? '-'
}
