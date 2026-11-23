import { isAxiosError } from 'axios'
import { authenticatedApi } from '../../../auth/session/authenticatedApi'

export type TransferOption = {
    session_id: number
    starts_at: string
    ends_at: string
}

export type PendingTemporaryTransfer = TransferOption & {
    original_session_id: number
    teaching_week: number
    topic: string
    class_name: string
}

export type TransferSource = {
    enrollment_id: number
    original_session_id: number
    current_session_id: number
    teaching_week: number | null
    topic: string
    starts_at: string
    ends_at: string
}

export type TransferOptions = {
    source: TransferSource | null
    options: TransferOption[]
    blocked_reason: 'NO_UPCOMING_SESSION' | 'MISSING_TEACHING_WEEK' | 'NO_ELIGIBLE_SESSIONS' | null
}

type TransferConflict = {
    code: 'SOURCE_CHANGED' | 'ALREADY_PRESENT' | 'TARGET_UNAVAILABLE' | 'SESSION_TIME_CHANGED'
    option?: TransferOption
}

const endpoint = '/schedule/temporary-transfers'
const timeout = 15000

export const temporaryTransferService = {
    async getOptions(signal: AbortSignal) {
        const { data } = await authenticatedApi.get<TransferOptions>(`${endpoint}/options`, { signal, timeout })
        return data
    },

    async confirm(source: TransferSource, option: TransferOption) {
        await authenticatedApi.put(`${endpoint}/${source.original_session_id}`, {
            expected_enrollment_id: source.enrollment_id,
            expected_current_session_id: source.current_session_id,
            target_session_id: option.session_id,
            expected_target_starts_at: option.starts_at,
            expected_target_ends_at: option.ends_at,
        }, { timeout })
    },

    async getPendingConfirmations(signal: AbortSignal) {
        const { data } = await authenticatedApi.get<PendingTemporaryTransfer[]>(`${endpoint}/pending`, { signal, timeout })
        return data
    },

    async reconfirm(transfer: PendingTemporaryTransfer) {
        await authenticatedApi.put(`${endpoint}/${transfer.original_session_id}/reconfirm`, {
            target_session_id: transfer.session_id,
            expected_target_starts_at: transfer.starts_at,
            expected_target_ends_at: transfer.ends_at,
        }, { timeout })
    },
}

export function getTransferConflict(error: unknown): TransferConflict | undefined {
    if (isAxiosError<{ detail?: TransferConflict }>(error) && error.response?.status === 409) {
        return error.response.data.detail
    }
}
