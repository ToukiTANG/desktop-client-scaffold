import { callApi } from './bridge'

import type { ApiResponse, MaterialPrice } from '@/types'

/**
 * 获取材料价格列表
 */
export async function getMaterialPrices(): Promise<ApiResponse<MaterialPrice[]>> {
  return await callApi<MaterialPrice[]>('material_price', 'get_material_prices')
}
