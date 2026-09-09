import type { Component } from 'vue'

export interface BusinessMenuItem {
  index: string
  label: string
  icon?: Component
}

// 增加菜单示例
// export const businessMenuItems: BusinessMenuItem[] = [
//   {
//     index: '/material-price',
//     label: '材料价格',
//     icon: Coin,
//   },
// ]

export const businessMenuItems: BusinessMenuItem[] = []
