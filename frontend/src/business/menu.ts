import type { Component } from 'vue'

export interface BusinessMenuItem {
  index: string
  label: string
  icon?: Component
}

export const businessMenuItems: BusinessMenuItem[] = []
