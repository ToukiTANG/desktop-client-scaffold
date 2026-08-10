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

async function getApi(): Promise<AppApi> {
  await waitForPyWebView()

  const api = window.pywebview?.api

  if (!api) {
    throw new Error('PyWebView API is unavailable')
  }

  return api
}

export async function ping() {
  const api = await getApi()

  return api.ping()
}

export async function hello(name: string) {
  const api = await getApi()

  return api.hello(name)
}

export async function getSystemInfo() {
  const api = await getApi()

  return api.get_system_info()
}
