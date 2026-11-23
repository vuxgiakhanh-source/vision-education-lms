import { useEffect, useRef, useState } from 'react'
import { formatLocalDateTimeRange } from '../../../../lib/date'
import { getTransferConflict, temporaryTransferService, type PendingTemporaryTransfer } from './temporaryTransferService'

type Props = {
    scheduleRevision: number
    onConfirmed: () => void
}

export function StudentPendingTransferConfirmations({ scheduleRevision, onConfirmed }: Props) {
    const [transfers, setTransfers] = useState<PendingTemporaryTransfer[]>([])
    const [loadError, setLoadError] = useState(false)
    const [notice, setNotice] = useState('')
    const [savingId, setSavingId] = useState<number>()
    const [reloadVersion, setReloadVersion] = useState(0)
    const submitting = useRef(false)

    useEffect(() => {
        const request = new AbortController()
        temporaryTransferService.getPendingConfirmations(request.signal)
            .then(data => {
                if (request.signal.aborted) return
                setTransfers(data)
                setLoadError(false)
            })
            .catch(() => {
                if (!request.signal.aborted) setLoadError(true)
            })
        return () => request.abort()
    }, [reloadVersion, scheduleRevision])

    async function reconfirm(transfer: PendingTemporaryTransfer) {
        if (submitting.current) return
        submitting.current = true
        setSavingId(transfer.original_session_id)
        setNotice('')
        try {
            await temporaryTransferService.reconfirm(transfer)
            setTransfers(previous => previous.filter(item => item.original_session_id !== transfer.original_session_id))
            setNotice(`Đã xác nhận giờ học mới của Tuần ${transfer.teaching_week}.`)
            onConfirmed()
        } catch (error) {
            const conflict = getTransferConflict(error)
            if (conflict?.code === 'SESSION_TIME_CHANGED' || conflict?.code === 'TARGET_UNAVAILABLE') {
                setTransfers(previous => previous.filter(item => item.original_session_id !== transfer.original_session_id))
                setNotice('Ca học đã thay đổi. Kiểm tra lại danh sách trước khi xác nhận.')
                setReloadVersion(version => version + 1)
            } else {
                setNotice('Chưa xác nhận được giờ học mới. Vui lòng thử lại.')
            }
        } finally {
            submitting.current = false
            setSavingId(undefined)
        }
    }

    return (
        <>
            <div role="status" className={notice ? 'rounded-xl bg-slate-50 px-3 py-2 text-sm text-slate-700' : 'sr-only'}>
                {notice || (transfers.length > 0 ? 'Có ca học bù đổi giờ cần xác nhận.' : '')}
            </div>
            {loadError && (
                <div className="rounded-xl bg-amber-50 px-3 py-2 text-sm text-amber-900">
                    Không tải được thông báo đổi giờ.{' '}
                    <button type="button" className="font-semibold underline" onClick={() => setReloadVersion(version => version + 1)}>
                        Thử lại
                    </button>
                </div>
            )}
            {transfers.length > 0 && (
                <section aria-label="Ca học bù cần xác nhận" className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-950">
                    <h2 className="font-semibold">Ca học bù đã đổi giờ</h2>
                    <ul className="mt-2 space-y-3">
                        {transfers.map(transfer => (
                            <li key={transfer.original_session_id} className="flex flex-wrap items-center justify-between gap-2">
                                <div>
                                    <p className="font-semibold">Tuần {transfer.teaching_week} · {transfer.class_name}</p>
                                    {transfer.topic.trim() && <p>{transfer.topic}</p>}
                                    <p>{formatLocalDateTimeRange(transfer.starts_at, transfer.ends_at)}</p>
                                </div>
                                <button
                                    type="button"
                                    disabled={loadError || savingId !== undefined}
                                    onClick={() => void reconfirm(transfer)}
                                    className="min-h-11 rounded-lg bg-brand-primary px-4 font-semibold text-white focus-visible:outline-2 focus-visible:outline-offset-2 disabled:opacity-60"
                                >
                                    {savingId === transfer.original_session_id ? 'Đang xác nhận…' : 'Xác nhận giờ mới'}
                                </button>
                            </li>
                        ))}
                    </ul>
                </section>
            )}
        </>
    )
}
