import { getApi } from './bridge'
import type { ApiResponse, AppInfo } from '@/types'

export async function getAppInfo(): Promise<ApiResponse<AppInfo>> {
  const api = await getApi()
  return api.get_app_info()
}

export async function openDirectory(path: string): Promise<ApiResponse<boolean>> {
  const api = await getApi()
  return api.open_directory(path)
}
