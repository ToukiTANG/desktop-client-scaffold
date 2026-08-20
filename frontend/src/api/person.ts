import { getApi } from './bridge'

import type { ApiResponse, PageResult, Person, PersonForm, PersonQuery } from '@/types'

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
