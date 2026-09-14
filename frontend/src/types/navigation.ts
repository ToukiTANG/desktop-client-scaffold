import type { Component } from 'vue'

export interface AppMenuItem {
  index: string
  label: string
  icon?: Component
  children?: AppMenuItem[]
}
