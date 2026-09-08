import type { ApiResponse } from '@/types'

function waitForPyWebView(): Promise<void> {
  if (window.pywebview?.api) {
    return Promise.resolve()
  }

  return new Promise((resolve) => {
    window.addEventListener(
      'pywebviewready',
      () => {
        resolve()
      },
      {
        once: true,
      },
    )
  })
}

export async function getApi(): Promise<AppApi> {
  await waitForPyWebView()

  const api = window.pywebview?.api

  if (!api) {
    throw new Error('PyWebView API is unavailable')
  }

  return api
}

/**
 * 调用 Python 业务 API。
 */
export async function callApi<T>(module: string, method: string, ...args: unknown[]): Promise<ApiResponse<T>> {
  const api = await getApi()

  return await api.invoke<T>(module, method, args)
}
