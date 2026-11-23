import { isAxiosError } from 'axios'
import { authenticatedApi } from '../../../auth/session/authenticatedApi'

export type PermanentTransferClass = {
    class_id: number
    class_name: string
}

export type TransferFirstSession = {
    session_id: number
    teaching_week: number
    starts_at: string
    ends_at: string
    topic: string
}

export type PermanentTransferOption = PermanentTransferClass & {
    is_full: boolean
    first_session: TransferFirstSession | null
}

export type PermanentTransferOptions = {
    current_class: PermanentTransferClass | null
    current_enrollment_id: number | null
    completed_through_teaching_week: number | null
    options: PermanentTransferOption[]
}

export type PermanentTransferResult = {
    new_class: PermanentTransferClass
    enrollment_id: number
    transferred_at: string
    first_session: TransferFirstSession | null
}

type PermanentTransferConflict =
    | { code: 'FIRST_SESSION_CHANGED'; first_session: TransferFirstSession | null }
    | { code: 'SOURCE_CHANGED' | 'TARGET_UNAVAILABLE' | 'CLASS_FULL' }

const endpoint = '/schedule/permanent-transfers'
const timeout = 15000

export async function getPermanentTransferOptions(signal: AbortSignal): Promise<PermanentTransferOptions> {
    const { data } = await authenticatedApi.get<PermanentTransferOptions>(`${endpoint}/options`, { signal, timeout })
    return data
}

export async function confirmPermanentTransfer(
    enrollmentId: number, option: PermanentTransferOption,
): Promise<PermanentTransferResult> {
    const session = option.first_session
    const { data } = await authenticatedApi.post<PermanentTransferResult>(endpoint, {
        target_class_id: option.class_id,
        expected_current_enrollment_id: enrollmentId,
        expected_first_session: session && {
            session_id: session.session_id,
            teaching_week: session.teaching_week,
            starts_at: session.starts_at,
            ends_at: session.ends_at,
        },
    }, { timeout })
    return data
}

export function getPermanentTransferConflict(error: unknown): PermanentTransferConflict | undefined {
    if (isAxiosError<{ detail?: PermanentTransferConflict }>(error) && error.response?.status === 409) {
        return error.response.data.detail
    }
}
