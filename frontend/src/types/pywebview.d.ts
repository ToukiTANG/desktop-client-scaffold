import type { ApiResponse, AppConfig, AppInfo, } from './index'

export {}

declare global {
  /**
   * Python AppApi 暴露给前端的方法
   */
  interface AppApi {
    /**
     * 通信测试
     */
    ping(): Promise<ApiResponse<string>>

    /**
     * 获取应用信息
     */
    get_app_info(): Promise<ApiResponse<AppInfo>>

    /**
     * 打开本地目录
     */
    open_directory(path: string): Promise<ApiResponse<boolean>>

    /**
     * 获取应用初始化配置
     */
    get_app_config(): Promise<ApiResponse<AppConfig>>

    /**
     * 保存应用初始化配置
     */
    save_app_config(config: AppConfig,): Promise<ApiResponse<AppConfig>>

    /**
     * 统一业务 API 调用入口
     */
    invoke<T = unknown>(module: string, method: string, args?: unknown[]): Promise<ApiResponse<T>>
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
