import type { RouteLocationRaw } from 'vue-router'

export interface BusinessSettingItem {
  title: string
  description?: string
  actionLabel: string
  to: RouteLocationRaw
}

export const businessSettingItems: BusinessSettingItem[] = []
