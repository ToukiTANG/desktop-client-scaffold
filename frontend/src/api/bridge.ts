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

