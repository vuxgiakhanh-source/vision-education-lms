import { useEffect, useId, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { formatLocalDateTimeRange } from '../../../lib/date'
import { getTransferConflict, temporaryTransferService } from './temporaryTransferService'
import type { TransferOptions } from './temporaryTransferService'

type Props = {
    onBack: () => void
    onRefreshSchedule: () => void
    onSuccess: () => void
    onSubmittingChange: (submitting: boolean) => void
}

type LoadState =
    | { status: 'loading' }
    | { status: 'failed' }
    | { status: 'ready'; data: TransferOptions }

const blockedMessages = {
    NO_UPCOMING_SESSION: 'Bạn chưa có buổi học nào để đổi ca.',
    MISSING_TEACHING_WEEK: 'Buổi học này chưa có số tuần dạy nên chưa thể đổi ca.',
    NO_ELIGIBLE_SESSIONS: 'Không còn ca phù hợp để đổi.',
}

const conflictMessages = {
    SOURCE_CHANGED: 'Lịch của bạn đã thay đổi. Hãy chọn lại ca từ danh sách mới.',
    ALREADY_PRESENT: 'Bạn đã được điểm danh ở ca vừa chọn đổi. Danh sách đã chuyển sang buổi có thể đổi tiếp theo.',
    TARGET_UNAVAILABLE: 'Ca này không còn hợp lệ. Hãy chọn một ca khác.',
    SESSION_TIME_CHANGED: 'Ca đã đổi giờ. Hãy kiểm tra giờ mới và xác nhận lại.',
}

export function TemporaryTransferPicker({ onBack, onRefreshSchedule, onSuccess, onSubmittingChange }: Props) {
    const [loadState, setLoadState] = useState<LoadState>({ status: 'loading' })
    const [loadVersion, setLoadVersion] = useState(0)
    const [selectedId, setSelectedId] = useState<number | null>(null)
    const [notice, setNotice] = useState<string | null>(null)
    const [updatedOptionId, setUpdatedOptionId] = useState<number | null>(null)
    const [submitting, setSubmitting] = useState(false)
    const submittingRef = useRef(false)
    const pickerId = useId()
    const noticeId = `${pickerId}-notice`
    const noticeRef = useRef<HTMLParagraphElement>(null)

    useEffect(() => {
        const controller = new AbortController()

        async function loadOptions() {
            try {
                const data = await temporaryTransferService.getOptions(controller.signal)
                if (!controller.signal.aborted) setLoadState({ status: 'ready', data })
            } catch {
                if (!controller.signal.aborted) setLoadState({ status: 'failed' })
            }
        }

        void loadOptions()
        return () => controller.abort()
    }, [loadVersion])

    useEffect(() => {
        if (notice) noticeRef.current?.focus()
    }, [notice])

    function reloadOptions() {
        setLoadState({ status: 'loading' })
        setSelectedId(null)
        setUpdatedOptionId(null)
        setLoadVersion(version => version + 1)
    }

    const data = loadState.status === 'ready' ? loadState.data : null
    const source = data?.source
    const selectedOption = data?.options.find(option => option.session_id === selectedId)

    async function confirm(event: FormEvent<HTMLFormElement>) {
        event.preventDefault()
        if (!data || !source || !selectedOption || submittingRef.current) return

        submittingRef.current = true
        setSubmitting(true)
        onSubmittingChange(true)
        setNotice(null)

        try {
            await temporaryTransferService.confirm(source, selectedOption)
            onSuccess()
        } catch (error) {
            const conflict = getTransferConflict(error)
            if (conflict?.code === 'SESSION_TIME_CHANGED' && conflict.option?.session_id === selectedOption.session_id) {
                const updatedOption = conflict.option
                setLoadState({
                    status: 'ready',
                    data: {
                        ...data,
                        options: data.options
                            .map(option => option.session_id === updatedOption.session_id ? updatedOption : option)
                            .sort((left, right) => left.starts_at.localeCompare(right.starts_at) || left.session_id - right.session_id),
                    },
                })
                setUpdatedOptionId(updatedOption.session_id)
                setNotice(`${conflictMessages.SESSION_TIME_CHANGED} Giờ mới: ${formatLocalDateTimeRange(updatedOption.starts_at, updatedOption.ends_at)}.`)
            } else {
                const message = conflict ? conflictMessages[conflict.code] : undefined
                setNotice(message ?? 'Chưa xác minh được kết quả đổi ca. Vui lòng kiểm tra lại lịch.')
                reloadOptions()
                if (!conflict || conflict.code === 'SOURCE_CHANGED') onRefreshSchedule()
            }
        } finally {
            submittingRef.current = false
            setSubmitting(false)
            onSubmittingChange(false)
        }
    }

    return (
        <form onSubmit={confirm} className="mt-3 space-y-4">
            {source && (
                <div className="rounded-xl bg-slate-50 px-3 py-2 text-sm text-slate-700">
                    <p className="font-semibold">
                        {source.teaching_week !== null ? `Tuần ${source.teaching_week} · ` : ''}
                        {source.topic.trim() || 'Buổi học'}
                    </p>
                    <p className="mt-1">Ca hiện tại: {formatLocalDateTimeRange(source.starts_at, source.ends_at)}</p>
                </div>
            )}

            {notice && <p id={noticeId} ref={noticeRef} tabIndex={-1} role="alert" className="rounded-xl bg-amber-50 p-3 text-sm text-amber-900">{notice}</p>}
            {loadState.status === 'loading' && <p className="text-sm text-slate-600">Đang tải danh sách ca…</p>}
            {loadState.status === 'failed' && (
                <div>
                    <p role="alert" className="text-sm text-red-700">Không tải được danh sách ca. Vui lòng thử lại.</p>
                    <button type="button" onClick={reloadOptions} className="mt-2 min-h-11 rounded-lg bg-brand-light px-4 text-sm font-semibold text-brand-primary focus-visible:outline-2">
                        Thử lại
                    </button>
                </div>
            )}
            {data?.blocked_reason && <p className="text-sm text-slate-700">{blockedMessages[data.blocked_reason]}</p>}
            {data && data.options.length > 0 && (
                <fieldset disabled={submitting} className="space-y-2">
                    <legend className="mb-2 text-sm font-semibold text-slate-800">Chọn ca thay thế</legend>
                    {data.options.map(option => (
                        <label
                            key={option.session_id}
                            htmlFor={`${pickerId}-${option.session_id}`}
                            className="flex min-h-11 cursor-pointer items-center gap-3 rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-800 has-checked:border-brand-primary has-checked:bg-brand-light has-focus-visible:outline-2 has-focus-visible:outline-offset-2 has-focus-visible:outline-brand-primary"
                        >
                            <input
                                id={`${pickerId}-${option.session_id}`}
                                type="radio"
                                name="temporary-transfer-option"
                                value={option.session_id}
                                checked={selectedId === option.session_id}
                                onChange={() => {
                                    setSelectedId(option.session_id)
                                    setNotice(null)
                                }}
                                className="size-4 shrink-0 accent-brand-primary"
                            />
                            <span>
                                {formatLocalDateTimeRange(option.starts_at, option.ends_at)}
                                {option.session_id === source?.original_session_id && (
                                    <span className="block text-xs text-slate-600">Quay về ca gốc</span>
                                )}
                            </span>
                        </label>
                    ))}
                </fieldset>
            )}

            <div className="flex flex-wrap justify-end gap-2">
                <button type="button" onClick={onBack} disabled={submitting} className="min-h-11 rounded-lg bg-brand-light px-4 text-sm font-semibold text-brand-primary focus-visible:outline-2 disabled:opacity-60">
                    Quay lại
                </button>
                <button
                    type="submit"
                    disabled={!selectedOption || submitting}
                    aria-describedby={notice ? noticeId : undefined}
                    className="min-h-11 rounded-lg bg-brand-primary px-4 text-sm font-semibold text-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-primary disabled:opacity-60"
                >
                    {submitting ? 'Đang xác nhận…' : updatedOptionId !== null && updatedOptionId === selectedId ? 'Xác nhận giờ mới' : 'Xác nhận'}
                </button>
            </div>
        </form>
    )
}
