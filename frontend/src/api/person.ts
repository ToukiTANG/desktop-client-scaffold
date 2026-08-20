import { getApi } from './bridge'

import type {
  ApiResponse,
  PageResult,
  Person,
  PersonDictionary,
  PersonForm,
  PersonImportPreviewResult,
  PersonImportResult,
  PersonQuery,
} from '@/types'

/**
 * 查询人员列表
 */
export async function getPersonList(params: PersonQuery): Promise<ApiResponse<PageResult<Person>>> {
  const api = await getApi()

  return await api.person.list(params)
}

/**
 * 新增人员
 */
export async function createPerson(data: PersonForm): Promise<ApiResponse<{ id: number }>> {
  const api = await getApi()

  return await api.person.create(data)
}

/**
 * 修改人员
 */
export async function updatePerson(personId: number, data: PersonForm): Promise<ApiResponse<null>> {
  const api = await getApi()

  return await api.person.update(personId, data)
}

/**
 * 删除人员
 */
export async function deletePerson(personId: number): Promise<ApiResponse<null>> {
  const api = await getApi()

  return await api.person.delete(personId)
}

/**
 * 打开系统文件选择窗口，
 * 并由 Python 解析 Excel，
 * 返回预览结果。
 */
export async function selectPersonImportFile(): Promise<
  ApiResponse<PersonImportPreviewResult | null>
> {
  const api = await getApi()

  return await api.person.select_import_file()
}

/**
 * 确认导入当前已经选择并预览过的 Excel。
 */
export async function confirmPersonImport(): Promise<ApiResponse<PersonImportResult>> {
  const api = await getApi()

  return await api.person.confirm_import()
}

/**
 * 获取人员相关固定业务字典。
 */
export async function getPersonDictionary(): Promise<ApiResponse<PersonDictionary>> {
  const api = await getApi()

  return await api.person.get_dictionary()
}
