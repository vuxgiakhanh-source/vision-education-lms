import { authenticatedApi } from '../../../auth/session/authenticatedApi'

export type ExamBankChoice = { paper_id: number; title: string }

export async function listExamBankChoices(signal?: AbortSignal): Promise<ExamBankChoice[]> {
    const { data } = await authenticatedApi.get<ExamBankChoice[]>('/teacher/exam-bank/papers', { signal })
    return data
}
