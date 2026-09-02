import type { ApiResponse, AppInfo } from './index'

export {}

declare global {
  /**
   * Python PersonApi 暴露给前端的方法
   */

  /**
   * Python AppApi
   */
  interface AppApi {
    /**
     * 通信测试
     */
    ping(): Promise<ApiResponse<string>>

    get_app_info(): Promise<ApiResponse<AppInfo>>

    open_directory(path: string): Promise<ApiResponse<boolean>>
  }

  /**
   * PyWebView 注入到 window 上的对象
   */
  interface Window {
    pywebview?: {
      api: AppApi
    }
  }
}
