<template>
  <div class="desktop-window">
    <header class="titlebar">
      <div class="drag" @mousedown="beginDrag" @dblclick="control('toggle_maximize')">
        <span class="logo" aria-hidden="true"
          ><svg viewBox="0 0 24 24">
            <rect x="5" y="3" width="15" height="18" rx="2" />
            <path d="M9 3v18M3 7h4M3 12h4M3 17h4" /></svg
        ></span>
        <span class="name">{{ name }}</span>
      </div>
      <span v-if="error" class="error" role="status">{{ error }}</span>
      <nav aria-label="窗口控制">
        <button :disabled="!ready" aria-label="最小化" title="最小化" @click="control('minimize')">
          <svg viewBox="0 0 16 16"><path d="M3 8h10" /></svg>
        </button>
        <button :disabled="!ready" :aria-label="maximized ? '还原' : '最大化'" :title="maximized ? '还原' : '最大化'" @click="control('toggle_maximize')">
          <svg viewBox="0 0 16 16">
            <path v-if="maximized" d="M5 5V3h8v8h-2M3 5h8v8H3z" />
            <rect v-else x="3" y="3" width="10" height="10" />
          </svg>
        </button>
        <button :disabled="!ready" class="close" aria-label="关闭" title="关闭" @click="control('close')">
          <svg viewBox="0 0 16 16"><path d="m3 3 10 10M13 3 3 13" /></svg>
        </button>
      </nav>
    </header>
    <div class="content"><slot /></div>
    <template v-if="ready && !maximized"
      ><div v-for="edge in edges" :key="edge" :class="['resize', 'edge-' + edge]" aria-hidden="true" @mousedown.left.prevent="control('resize', edge)"
    /></template>
  </div>
</template>
<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref } from 'vue'
import { getApi } from '@/api/bridge'
const name = ref(document.title),
  maximized = ref(true),
  ready = ref(false),
  error = ref('')
const edges = ['left', 'right', 'top', 'bottom', 'top-left', 'top-right', 'bottom-left', 'bottom-right']
let api: AppApi | undefined
let timer: ReturnType<typeof setInterval> | undefined
let disposed = false,
  checking = false
let stopDrag = () => {}
async function refreshState() {
  if (!api || checking || disposed) return
  checking = true
  try {
    const response = await api.window_control('state')
    if (response.success && response.data) maximized.value = response.data.maximized
  } catch {
    /* The host may be closing. */
  } finally {
    checking = false
  }
}
async function control(action: string, edge = '') {
  if (!ready.value || !api) return
  try {
    const response = await api.window_control(action, edge)
    error.value = response.success ? '' : response.message || '窗口操作失败'
    await refreshState()
  } catch {
    error.value = '窗口连接暂不可用'
  }
}
function beginDrag(event: MouseEvent) {
  if (event.button !== 0 || !ready.value || event.detail > 1) return
  stopDrag()
  const { screenX, screenY } = event
  const move = (next: MouseEvent) => {
    if (!(next.buttons & 1)) {
      stopDrag()
      return
    }
    if (Math.abs(next.screenX - screenX) + Math.abs(next.screenY - screenY) < 4) return
    stopDrag()
    void control('move')
  }
  const stop = () => {
    window.removeEventListener('mousemove', move)
    window.removeEventListener('mouseup', stop)
  }
  stopDrag = stop
  window.addEventListener('mousemove', move)
  window.addEventListener('mouseup', stop, { once: true })
}
onMounted(async () => {
  try {
    api = await getApi()
    if (disposed) return
    const info = await api.get_app_info()
    if (disposed) return
    if (info.success && info.data) name.value = info.data.name
    ready.value = typeof api.window_control === 'function'
    if (!ready.value) return
    await refreshState()
    if (disposed) return
    timer = setInterval(refreshState, 750)
    window.addEventListener('focus', refreshState)
  } catch {
    error.value = '窗口初始化失败'
  }
})
onBeforeUnmount(() => {
  disposed = true
  if (timer) clearInterval(timer)
  stopDrag()
  window.removeEventListener('focus', refreshState)
})
</script>
<style scoped>
.desktop-window {
  position: fixed;
  inset: 0;
  overflow: hidden;
  min-width: 0;
  box-sizing: border-box;
  height: 100%;
  display: flex;
  flex-direction: column;
  min-height: 0;
  background: #fff;
}
.titlebar {
  height: 36px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  background: var(--window-bar-background, #fff);
  color: var(--window-bar-color, #183653);
  border-bottom: 1px solid #e4edf4;
  user-select: none;
}
.drag {
  display: flex;
  align-items: center;
  gap: 9px;
  height: 100%;
  flex: 1;
  min-width: 0;
  padding-left: 14px;
}
.logo {
  width: 22px;
  height: 22px;
  border-radius: 5px;
  background: var(--window-accent, #227db5);
  display: flex;
  align-items: center;
  justify-content: center;
}
.logo svg {
  width: 16px;
  height: 16px;
  stroke: #fff;
  fill: none;
  stroke-width: 1.2;
}
.name {
  font-size: 13px;
  font-weight: 600;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}
.error {
  color: #b42318;
  font-size: 12px;
}
nav {
  display: flex;
  height: 100%;
}
button {
  width: 46px;
  border: 0;
  background: transparent;
  color: inherit;
  display: grid;
  place-items: center;
  cursor: default;
}
button svg {
  width: 14px;
  height: 14px;
  stroke: currentColor;
  stroke-width: 1.1;
  fill: none;
}
button:hover {
  background: #e9f4fc;
}
button:focus-visible {
  outline: 2px solid #227db5;
  outline-offset: -3px;
}
button.close:hover {
  background: #c42b1c;
  color: #fff;
}
button:disabled {
  opacity: 0.4;
}
.content {
  flex: 1;
  min-height: 0;
  overflow: hidden;
}
.resize {
  position: fixed;
  z-index: 10000;
}
.edge-left,
.edge-right {
  top: 6px;
  bottom: 6px;
  width: 5px;
  cursor: ew-resize;
}
.edge-left {
  left: 0;
}
.edge-right {
  right: 0;
}
.edge-top,
.edge-bottom {
  left: 6px;
  right: 6px;
  height: 5px;
  cursor: ns-resize;
}
.edge-top {
  top: 0;
}
.edge-bottom {
  bottom: 0;
}
.edge-top-left,
.edge-top-right,
.edge-bottom-left,
.edge-bottom-right {
  width: 6px;
  height: 6px;
}
.edge-top-left {
  top: 0;
  left: 0;
  cursor: nwse-resize;
}
.edge-top-right {
  top: 0;
  right: 0;
  cursor: nesw-resize;
}
.edge-bottom-left {
  bottom: 0;
  left: 0;
  cursor: nesw-resize;
}
.edge-bottom-right {
  bottom: 0;
  right: 0;
  cursor: nwse-resize;
}
</style>
