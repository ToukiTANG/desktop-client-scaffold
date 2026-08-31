import { getApi } from './bridge'

import type {
  ApiResponse,
  CheckProblem,
  CheckProblemQuery,
  PageResult,
  ProblemDictionary,
  ProblemImportPreviewResult,
  ProblemImportResult,
} from '@/types'

export async function getProblemList(
  params: CheckProblemQuery,
): Promise<ApiResponse<PageResult<CheckProblem>>> {
  const api = await getApi()

  return api.problem.list(params)
}

export async function getProblemDictionary(): Promise<ApiResponse<ProblemDictionary>> {
  const api = await getApi()

  return api.problem.get_dictionary()
}

export async function selectProblemImportFile(): Promise<
  ApiResponse<ProblemImportPreviewResult | null>
> {
  const api = await getApi()

  return api.problem.select_import_file()
}

export async function confirmProblemImport(): Promise<ApiResponse<ProblemImportResult>> {
  const api = await getApi()

  return api.problem.confirm_import()
}
