import { useEffect, useId, useRef, useState } from 'react'
import { ArrowLeftRight, ChevronRight } from 'lucide-react'
import { TemporaryTransferPicker } from '../temporary_transfers/TemporaryTransferPicker'

export function ScheduleTransferButton({ onRefreshSchedule, onOpenPermanentTransfer }: {
    onRefreshSchedule?: () => void
    onOpenPermanentTransfer?: () => void
}) {
    const dialog = useRef<HTMLDialogElement>(null)
    const title = useRef<HTMLHeadingElement>(null)
    const titleId = useId()
    const [pickerOpen, setPickerOpen] = useState(false)
    const [submitting, setSubmitting] = useState(false)
    const [transferComplete, setTransferComplete] = useState(false)

    useEffect(() => {
        if (dialog.current?.open) title.current?.focus()
    }, [pickerOpen])

    return (
        <div className="rounded-[22px] border border-[#EAEFF5] bg-white p-3.5 shadow-[0_4px_20px_rgba(20,25,45,0.03)]">
            <button
                type="button"
                aria-haspopup="dialog"
                onClick={event => {
                    setTransferComplete(false)
                    event.currentTarget.focus()
                    dialog.current?.showModal()
                }}
                className="flex min-h-[52px] w-full cursor-pointer items-center justify-between gap-2 rounded-2xl bg-linear-to-r from-[#4543D0] via-[#4A48D6] to-[#3432B0] px-4 py-2 text-left text-[14.5px] font-semibold text-white shadow-[0_8px_20px_rgba(69,67,208,0.28)] transition-colors hover:from-[#3D3BC4] hover:to-[#2C2AA0] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-primary"
            >
                <span className="flex items-center gap-2.5">
                    <ArrowLeftRight aria-hidden="true" className="size-[18px] shrink-0" strokeWidth={2.2} />
                    <span>Đổi lịch học</span>
                </span>
                <ChevronRight aria-hidden="true" className="size-[18px] shrink-0" strokeWidth={2.2} />
            </button>

            <p role="status" className={transferComplete ? 'mt-2 text-sm font-medium text-green-700' : 'sr-only'}>
                {transferComplete ? 'Đổi ca thành công.' : ''}
            </p>

            <dialog
                ref={dialog}
                aria-labelledby={titleId}
                onCancel={event => {
                    if (submitting) event.preventDefault()
                }}
                onClose={() => {
                    if (!dialog.current?.open) setPickerOpen(false)
                }}
                className="m-auto max-h-[calc(100dvh-2rem)] w-[calc(100%-2rem)] max-w-sm overflow-y-auto overscroll-contain rounded-[22px] border border-[#EAEFF5] bg-white p-5 shadow-xl backdrop:overflow-hidden backdrop:overscroll-contain backdrop:bg-slate-950/40"
            >
                <h2 id={titleId} ref={title} tabIndex={-1} className="text-base font-bold text-slate-800">
                    {pickerOpen ? 'Đổi ca tạm thời' : 'Đổi lịch học'}
                </h2>
                {pickerOpen && onRefreshSchedule ? (
                    <TemporaryTransferPicker
                        onBack={() => setPickerOpen(false)}
                        onRefreshSchedule={onRefreshSchedule}
                        onSubmittingChange={setSubmitting}
                        onSuccess={() => {
                            dialog.current?.close()
                            setTransferComplete(true)
                            onRefreshSchedule()
                        }}
                    />
                ) : (
                    <>
                        <div className="mt-4 grid gap-2">
                            <button
                                type="button"
                                disabled={!onRefreshSchedule}
                                onClick={() => setPickerOpen(true)}
                                className="min-h-11 cursor-pointer rounded-xl border border-slate-200 p-3 text-left text-sm font-medium text-slate-800 hover:bg-brand-light focus-visible:outline-2 focus-visible:outline-brand-primary disabled:cursor-default disabled:text-slate-500 disabled:hover:bg-white"
                            >
                                Đổi tạm thời
                            </button>
                            <button
                                type="button"
                                disabled={!onOpenPermanentTransfer}
                                onClick={() => {
                                    dialog.current?.close()
                                    onOpenPermanentTransfer?.()
                                }}
                                className="min-h-11 cursor-pointer rounded-xl border border-slate-200 p-3 text-left text-sm font-medium text-slate-800 hover:bg-brand-light focus-visible:outline-2 focus-visible:outline-brand-primary disabled:cursor-default disabled:text-slate-500 disabled:hover:bg-white"
                            >
                                Đổi cố định
                            </button>
                        </div>
                        <form method="dialog" className="mt-4 flex justify-end">
                            <button type="submit" className="min-h-11 cursor-pointer rounded-lg bg-brand-light px-4 text-sm font-semibold text-brand-primary focus-visible:outline-2">
                                Đóng
                            </button>
                        </form>
                    </>
                )}
            </dialog>
        </div>
    )
}
