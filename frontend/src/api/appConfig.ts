import { getApi } from './bridge'
import type { ApiResponse, AppConfig, AppConfigStatus } from '@/types'

/**
 * 获取应用初始化配置状态
 */
export async function getAppConfig(): Promise<ApiResponse<AppConfigStatus>> {
  const api = await getApi()
  return api.get_app_config()
}

/**
 * 保存应用初始化配置
 */
export async function saveAppConfig(
  workshop: string,
  apartment: string,
): Promise<ApiResponse<AppConfig>> {
  const api = await getApi()

  return api.save_app_config(workshop, apartment)
}
