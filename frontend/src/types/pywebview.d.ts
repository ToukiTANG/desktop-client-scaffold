import type { ApiResponse, PageResult, Person, PersonForm, PersonQuery } from './index'

export {}

declare global {
  /**
   * Python PersonApi 暴露给前端的方法
   */
  interface PersonApi {
    /**
     * 查询人员列表
     */
    list(params: PersonQuery): Promise<ApiResponse<PageResult<Person>>>

    /**
     * 新增人员
     */
    create(data: PersonForm): Promise<
      ApiResponse<{
        id: number
      }>
    >

    /**
     * 修改人员
     */
    update(personId: number, data: PersonForm): Promise<ApiResponse<null>>

    /**
     * 删除人员
     */
    delete(personId: number): Promise<ApiResponse<null>>
  }

  /**
   * Python AppApi
   */
  interface AppApi {
    /**
     * 通信测试
     */
    ping(): Promise<ApiResponse<string>>

    /**
     * 人员模块
     */
    person: PersonApi
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
