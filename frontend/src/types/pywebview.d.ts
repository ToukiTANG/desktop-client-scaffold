export {}

declare global {
  interface AppApi {
    ping(): Promise<{
      code: number
      message: string
    }>

    hello(name: string): Promise<{
      code: number
      message: string
    }>

    get_system_info(): Promise<{
      code: number
      data: {
        system: string
        release: string
        machine: string
        python_version: string
      }
    }>
  }

  interface Window {
    pywebview?: {
      api: AppApi
    }
  }
}
