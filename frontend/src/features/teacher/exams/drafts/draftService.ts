import { isAxiosError } from 'axios'
import { authenticatedApi } from '../../../auth/session/authenticatedApi'

export type ExamDraftFields = {
    paper_id: number | null
    title: string | null
    description: string | null
    opens_at: string | null
    closes_at: string | null
    duration_minutes: number | null
}

export type ExamDraft = ExamDraftFields & {
    exam_id: number
    version: number
    autosave_key: string | null
    schedule_inputs?: Partial<Record<ScheduleField, string>> | null
}

export type ScheduleField = 'opens_at' | 'closes_at'

export const emptyExamDraft: ExamDraftFields = {
    paper_id: null,
    title: null,
    description: null,
    opens_at: null,
    closes_at: null,
    duration_minutes: null,
}

export function newExamFields(): ExamDraftFields {
    const tomorrow = new Date(Date.now() + 86_400_000)
    const date = new Intl.DateTimeFormat('sv-SE', { timeZone: 'Asia/Ho_Chi_Minh' }).format(tomorrow)
    return {
        ...emptyExamDraft,
        opens_at: date + 'T08:00:00',
        closes_at: date + 'T08:45:00',
        duration_minutes: 45,
    }
}

const examsUrl = '/teacher/exams'

export async function listExamDrafts(signal?: AbortSignal): Promise<ExamDraft[]> {
    return (await authenticatedApi.get<ExamDraft[]>(`${examsUrl}/drafts`, { signal })).data
}

export async function getExamDraft(id: number, signal?: AbortSignal): Promise<ExamDraft> {
    return (await authenticatedApi.get<ExamDraft>(`${examsUrl}/${id}`, { signal })).data
}

export async function getExamDraftByKey(key: string, signal: AbortSignal): Promise<ExamDraft> {
    return (
        await authenticatedApi.get<ExamDraft>(`${examsUrl}/drafts/by-key/${encodeURIComponent(key)}`, {
            signal,
        })
    ).data
}

export async function createExamDraft(fields: ExamDraftFields, key: string): Promise<number> {
    const { data } = await authenticatedApi.post<{ exam_id: number }>(examsUrl, {
        ...toRequest(fields),
        autosave_key: key,
    })
    return data.exam_id
}

export async function updateExamDraft(
    id: number,
    version: number,
    fields: ExamDraftFields,
): Promise<ExamDraft> {
    return (
        await authenticatedApi.put<ExamDraft>(`${examsUrl}/${id}`, { ...toRequest(fields), version })
    ).data
}

export async function deleteExamDraft(id: number): Promise<void> {
    await authenticatedApi.delete(`${examsUrl}/${id}`)
}

export function draftErrorStatus(error: unknown): number | undefined {
    return isAxiosError(error) ? error.response?.status : undefined
}

export function splitSchedule(value: string | null): [date: string, time: string] {
    const [date = '', time = ''] = value?.split('T', 2) ?? []
    const seconds = time.slice(5, 8)
    return [
        date,
        seconds && seconds !== ':00' && /^:\d{2}$/.test(seconds) ? time.slice(0, 8) : time.slice(0, 5),
    ]
}

export function joinSchedule(date: string, time: string): string | null {
    return date || time ? date + 'T' + time : null
}

export function toDraftFields(
    exam: ExamDraftFields & Pick<ExamDraft, 'schedule_inputs'>,
): ExamDraftFields {
    const centerInputTime = (field: ScheduleField) =>
        joinSchedule(...splitSchedule(exam[field] ?? exam.schedule_inputs?.[field] ?? null))
    return {
        paper_id: exam.paper_id,
        title: exam.title?.trim() || null,
        description: exam.description || null,
        opens_at: centerInputTime('opens_at'),
        closes_at: centerInputTime('closes_at'),
        duration_minutes: exam.duration_minutes,
    }
}

function toRequest(input: ExamDraftFields) {
    const fields = toDraftFields(input)
    const schedule_inputs: Partial<Record<ScheduleField, string>> = {}
    const timestamps = { opens_at: fields.opens_at, closes_at: fields.closes_at }
    for (const field of ['opens_at', 'closes_at'] as const) {
        const value = timestamps[field]
        if (value && splitSchedule(value).some((part) => !part)) {
            schedule_inputs[field] = value
            timestamps[field] = null
        }
    }
    return {
        ...fields,
        ...timestamps,
        schedule_inputs: Object.keys(schedule_inputs).length ? schedule_inputs : null,
    }
}

export function draftValidationMessage(error: unknown): string {
    if (!isAxiosError<{ detail?: { msg?: string }[] }>(error)) return ''
    const detail = error.response?.data?.detail
    return (
        (Array.isArray(detail) && detail[0]?.msg?.replace(/^Value error, /, '')) ||
        'Kiểm tra lại thông tin kỳ thi.'
    )
}
