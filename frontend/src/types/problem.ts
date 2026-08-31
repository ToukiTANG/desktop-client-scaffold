import type { DictionaryOption, PageResult } from './api'

export interface CheckProblem {
  id: number

  status: number
  decomposed: number
  revised: number
  assessed: number

  checkDepartment: string
  checkPerson: string
  checkType: number
  checkWay: number

  checkStartTime: string
  checkEndTime: string
  submitTime: string

  problemItem: string
  consequences: string
  riskType: string
  riskLevel: number

  problemClassify: number
  problemLabel: number
  problemExtraPoints: string
  problemType: string

  redLine: number
  problemPosition: string

  implementDepartment: string
  dutyDepartment: string
  otherClassify: string

  crossUnit: number
  businessGuidance: number
  outside: number

  problemDescription: string
  deadline: string

  rectificationRequirements: string | null
  rectificationPerson: string | null
  rectificationTime: string | null
  rectificationDescription: string | null

  responsiblePerson: string | null
  reason: string | null

  closeIssuePerson: string | null
  closeIssueEvaluate: string | null
  closeIssueTime: string | null
}

export interface CheckProblemQuery {
  keyword?: string

  status?: number
  checkDepartment?: string
  checkPerson?: string
  checkType?: number
  checkWay?: number

  riskLevel?: number
  problemClassify?: number
  problemLabel?: number
  redLine?: number

  page: number
  pageSize: number
}

export interface ProblemDictionary {
  status: DictionaryOption[]
  decomposed: DictionaryOption[]
  revised: DictionaryOption[]
  assessed: DictionaryOption[]

  checkType: DictionaryOption[]
  checkWay: DictionaryOption[]

  riskLevel: DictionaryOption[]
  problemClassify: DictionaryOption[]
  problemLabel: DictionaryOption[]

  redLine: DictionaryOption[]
  crossUnit: DictionaryOption[]
  businessGuidance: DictionaryOption[]
  outside: DictionaryOption[]
}

export interface ProblemImportError {
  row: number
  message: string
}

export interface ProblemImportResult {
  total: number
  successCount: number
  failureCount: number
  errors: ProblemImportError[]
}

export interface ProblemImportPreviewRow extends Omit<CheckProblem, 'id'> {
  row: number
}

export interface ProblemImportPreviewResult {
  fileName: string
  total: number
  successCount: number
  failureCount: number
  preview: ProblemImportPreviewRow[]
  previewLimit: number
  errors: ProblemImportError[]
}

export type CheckProblemPageResult = PageResult<CheckProblem>
