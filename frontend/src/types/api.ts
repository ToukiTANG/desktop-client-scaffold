export interface ApiResponse<T = unknown> {
  success: boolean

  data: T

  message: string | null
}

export interface PageResult<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
}

export interface AppInfo {
  version: string
  dataDir: string
  logDir: string
}
