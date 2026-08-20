export interface Person {
  id: number
  name: string
  department: string
  jobTitle: string

  identity: number
  specializeClassify: number
  education: string | null
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

export interface DictionaryOption {
  value: number
  label: string
}

export interface PersonDictionary {
  gender: DictionaryOption[]
  identity: DictionaryOption[]
  specializeClassify: DictionaryOption[]
  productionGroupClassify: DictionaryOption[]
}

export interface PersonImportError {
  row: number
  message: string
}

export interface PersonImportResult {
  total: number
  successCount: number
  failureCount: number
  errors: PersonImportError[]
}

/**
 * Excel 预览中的单条人员数据。
 *
 * row 是 Excel 原始行号，
 * 其他字段与 PersonForm 一致。
 */
export interface PersonImportPreviewRow extends PersonForm {
  row: number
}

/**
 * Excel 解析错误。
 */
export interface PersonImportPreviewError {
  row: number
  message: string
}

/**
 * Excel 文件解析预览结果。
 */
export interface PersonImportPreviewResult {
  fileName: string

  /**
   * Excel 实际数据总条数。
   */
  total: number

  /**
   * 校验通过条数。
   */
  successCount: number

  /**
   * 校验失败条数。
   */
  failureCount: number

  /**
   * 返回给前端用于预览的数据。
   *
   * 后端目前最多返回 100 条。
   */
  preview: PersonImportPreviewRow[]

  /**
   * 最大预览条数。
   */
  previewLimit: number

  /**
   * 错误数据。
   */
  errors: PersonImportPreviewError[]
}
