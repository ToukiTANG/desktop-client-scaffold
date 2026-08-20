export interface Person {
  id: number
  name: string
  department: string
  jobTitle: string

  identity: number
  specializeClassify: number
  education: string
  gender: number

  productionGroupClassify: number | null

  createTime: string
}

export interface PersonForm {
  name: string
  department: string
  jobTitle: string

  identity: number | null
  specializeClassify: number | null
  education: string
  gender: number | null

  productionGroupClassify: number | null
}

export interface PersonQuery {
  keyword?: string
  department?: string

  identity?: number
  specializeClassify?: number
  education?: string
  gender?: number
  productionGroupClassify?: number

  page: number
  pageSize: number
}

export interface PageResult<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
}
