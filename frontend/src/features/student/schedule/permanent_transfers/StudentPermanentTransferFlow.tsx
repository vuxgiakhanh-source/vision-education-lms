import { ArrowLeft, ArrowRight, BookOpen, CalendarDays, Check, Info } from 'lucide-react'
import { useEffect, useId, useRef, useState, type FormEvent } from 'react'
import { formatLocalDateTimeRange } from '../../../../lib/date'
import type { UpcomingSession } from '../upcoming/upcomingScheduleService'
import {
    confirmPermanentTransfer,
    getPermanentTransferConflict,
    getPermanentTransferOptions,
    type PermanentTransferOptions,
    type PermanentTransferResult,
    type TransferFirstSession,
} from './permanentTransferService'

type Props = {
    upcoming?: UpcomingSession | null
    upcomingError: boolean
    onExit: () => void
    onRefreshSchedule: () => void
    onSuccess: (result: PermanentTransferResult) => void
}

type Step = 1 | 2 | 3
type LoadState = { status: 'loading' | 'failed' } | { status: 'ready'; data: PermanentTransferOptions }

const steps = ['Lớp hiện tại', 'Chọn lớp mới', 'Xác nhận']
const headings = ['Kiểm tra lớp hiện tại', 'Chọn lớp mới', 'Xác nhận đổi lớp']
const primaryButton = 'inline-flex min-h-12 items-center justify-center gap-2 rounded-xl bg-[#272487] px-5 py-2.5 text-sm font-semibold text-white hover:bg-[#211E72] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-primary disabled:opacity-55'
const secondaryButton = 'inline-flex min-h-12 items-center justify-center gap-2 rounded-xl border border-indigo-200 bg-white px-5 py-2.5 text-sm font-semibold text-slate-800 hover:bg-indigo-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-primary disabled:opacity-55'
const conflictMessages = {
    SOURCE_CHANGED: 'Lớp hiện tại đã thay đổi. Hãy kiểm tra lại trước khi tiếp tục.',
    TARGET_UNAVAILABLE: 'Lớp này không còn nhận chuyển. Hãy chọn lớp khác.',
    CLASS_FULL: 'Lớp này vừa hết chỗ. Hãy chọn lớp khác.',
}
const classCardColors = {
    current: ['border-indigo-100 bg-indigo-50/60', 'border-indigo-100 bg-indigo-100/60 text-indigo-950'],
    previous: ['border-rose-100 bg-rose-50/50', 'border-rose-100 bg-rose-100/60 text-rose-950'],
    new: ['border-emerald-200 bg-emerald-50/50', 'border-emerald-100 bg-emerald-100/60 text-emerald-900'],
}

function describeSession(session: TransferFirstSession | null) {
    if (!session) return 'Chưa có lịch học'
    return `Tuần ${session.teaching_week} · ${formatLocalDateTimeRange(session.starts_at, session.ends_at)}`
}

function ClassCard({ label, name, schedule, topic, tone }: {
    label: string
    name: string
    schedule: string
    topic?: string
    tone: keyof typeof classCardColors
}) {
    const [cardColor, headingColor] = classCardColors[tone]
    return (
        <div className={`min-w-0 overflow-hidden rounded-2xl border ${cardColor}`}>
            <p className={`flex items-center gap-2 border-b px-4 py-3 text-sm font-semibold ${headingColor}`}>
                <BookOpen aria-hidden="true" className="size-4 shrink-0" /> {label}
            </p>
            <div className="space-y-2 p-4">
                <p className="wrap-anywhere text-base font-bold text-slate-950">{name}</p>
                <p className="flex items-start gap-2 text-sm text-slate-700">
                    <CalendarDays aria-hidden="true" className="mt-0.5 size-4 shrink-0" />
                    <span className="min-w-0 wrap-anywhere">{schedule}</span>
                </p>
                {topic && <p className="wrap-anywhere text-sm text-slate-700">{topic}</p>}
            </div>
        </div>
    )
}

export function StudentPermanentTransferFlow({ upcoming, upcomingError, onExit, onRefreshSchedule, onSuccess }: Props) {
    const [step, setStep] = useState<Step>(1)
    const [loadState, setLoadState] = useState<LoadState>({ status: 'loading' })
    const [loadVersion, setLoadVersion] = useState(0)
    const [selectedId, setSelectedId] = useState<number | null>(null)
    const [notice, setNotice] = useState<string>()
    const [needsReconfirmation, setNeedsReconfirmation] = useState(false)
    const [submitting, setSubmitting] = useState(false)
    const submittingRef = useRef(false)
    const heading = useRef<HTMLHeadingElement>(null)
    const alert = useRef<HTMLParagraphElement>(null)
    const formId = useId()

    const data = loadState.status === 'ready' ? loadState.data : undefined
    const current = data?.current_class
    const selected = data?.options.find(option => option.class_id === selectedId)
    const currentSchedule = upcoming
        ? formatLocalDateTimeRange(upcoming.starts_at, upcoming.ends_at)
        : upcomingError ? 'Không tải được lịch học' : upcoming === null ? 'Chưa có lịch học' : 'Đang tải lịch học…'

    useEffect(() => {
        const controller = new AbortController()
        getPermanentTransferOptions(controller.signal)
            .then(data => {
                if (!controller.signal.aborted) setLoadState({ status: 'ready', data })
            })
            .catch(() => {
                if (!controller.signal.aborted) setLoadState({ status: 'failed' })
            })
        return () => controller.abort()
    }, [loadVersion])

    useEffect(() => {
        heading.current?.focus()
    }, [step])

    useEffect(() => {
        if (notice) alert.current?.focus()
    }, [notice])

    function goBack() {
        if (submittingRef.current) return
        if (step === 1) {
            onExit()
            return
        }
        setNotice(undefined)
        setStep(step === 3 ? 2 : 1)
    }

    function reloadOptions(nextStep: Step) {
        setLoadState({ status: 'loading' })
        setStep(nextStep)
        setSelectedId(null)
        setNeedsReconfirmation(false)
        setLoadVersion(version => version + 1)
    }

    async function confirm(event: FormEvent<HTMLFormElement>) {
        event.preventDefault()
        if (!data?.current_enrollment_id || !selected || selected.is_full || submittingRef.current) return

        submittingRef.current = true
        setSubmitting(true)
        setNotice(undefined)
        try {
            const result = await confirmPermanentTransfer(data.current_enrollment_id, selected)
            onSuccess(result)
        } catch (error) {
            const conflict = getPermanentTransferConflict(error)
            if (conflict?.code === 'FIRST_SESSION_CHANGED') {
                setLoadState({
                    status: 'ready',
                    data: {
                        ...data,
                        options: data.options.map(option => option.class_id === selected.class_id
                            ? { ...option, first_session: conflict.first_session }
                            : option),
                    },
                })
                setNeedsReconfirmation(true)
                setNotice('Buổi học đầu tiên đã thay đổi. Hãy kiểm tra lịch mới và xác nhận lại.')
            } else if (conflict) {
                setNotice(conflictMessages[conflict.code])
                reloadOptions(conflict.code === 'SOURCE_CHANGED' ? 1 : 2)
                if (conflict.code === 'SOURCE_CHANGED') onRefreshSchedule()
            } else {
                setNotice('Chưa xác nhận được kết quả. Hãy kiểm tra lớp hiện tại trước khi thử lại.')
                reloadOptions(1)
                onRefreshSchedule()
            }
        } finally {
            submittingRef.current = false
            setSubmitting(false)
        }
    }

    return (
        <section className="w-full min-w-0 rounded-[24px] border border-indigo-100 bg-white p-4 shadow-[0_8px_30px_rgba(40,45,95,0.05)] sm:p-6 lg:p-8">
            <header className="flex flex-col gap-4 border-b border-indigo-100 pb-5 lg:flex-row lg:items-center lg:justify-between">
                <div className="flex min-w-0 items-center gap-3">
                    <button
                        type="button"
                        aria-label={step === 1 ? 'Về lịch học' : 'Về bước trước'}
                        disabled={submitting}
                        onClick={goBack}
                        className="grid size-12 shrink-0 place-items-center rounded-full border border-indigo-100 bg-white text-indigo-950 hover:bg-indigo-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-primary disabled:opacity-55"
                    >
                        <ArrowLeft aria-hidden="true" className="size-5" />
                    </button>
                    <h1 className="text-xl font-bold tracking-tight text-slate-950 sm:text-2xl">Đổi ca cố định</h1>
                </div>
                <ol aria-label="Tiến trình đổi lớp" className="grid min-w-0 grid-cols-3 gap-2 sm:gap-5">
                    {steps.map((label, index) => (
                        <li
                            key={label}
                            aria-current={step === index + 1 ? 'step' : undefined}
                            className="flex min-w-0 flex-col items-start gap-1.5 text-xs font-semibold text-slate-700 sm:flex-row sm:items-center sm:text-sm"
                        >
                            <span aria-hidden="true" className={`grid size-7 shrink-0 place-items-center rounded-full border ${step === index + 1 ? 'border-[#272487] bg-[#272487] text-white' : 'border-indigo-200 bg-indigo-50 text-indigo-900'}`}>
                                {index + 1 < step ? <Check className="size-4" /> : index + 1}
                            </span>
                            <span>{label}</span>
                        </li>
                    ))}
                </ol>
            </header>

            <div className="mt-6">
                <h2 id={formId} ref={heading} tabIndex={-1} className="text-lg font-bold text-slate-950 focus:outline-none sm:text-xl">
                    {headings[step - 1]}
                </h2>
                {notice && (
                    <p ref={alert} tabIndex={-1} role="alert" className="mt-3 rounded-xl bg-amber-50 px-4 py-3 text-sm font-medium text-amber-950">
                        {notice}
                    </p>
                )}
                {loadState.status === 'loading' && <p role="status" className="mt-4 text-sm text-slate-700">Đang tải danh sách lớp…</p>}
                {loadState.status === 'failed' && (
                    <div className="mt-4 space-y-3">
                        <p role="alert" className="text-sm text-red-800">Không tải được danh sách lớp.</p>
                        <button type="button" onClick={() => reloadOptions(step)} className={secondaryButton}>Thử lại</button>
                    </div>
                )}
                {data && !current && <p className="mt-4 text-sm text-slate-700">Bạn chưa có lớp hiện tại để chuyển.</p>}

                {step === 1 && current && (
                    <div className="mt-4 space-y-5">
                        <ClassCard label="Lớp hiện tại" name={current.class_name} schedule={currentSchedule} topic={upcoming?.topic} tone="current" />
                        <div className="flex justify-end">
                            <button type="button" onClick={() => setStep(2)} className={primaryButton}>
                                Chọn lớp mới <ArrowRight aria-hidden="true" className="size-4" />
                            </button>
                        </div>
                    </div>
                )}

                {step === 2 && current && data && (
                    <form aria-labelledby={formId} className="mt-4" onSubmit={event => {
                        event.preventDefault()
                        if (selected && !selected.is_full) {
                            setNotice(undefined)
                            setStep(3)
                        }
                    }}>
                        <fieldset className="space-y-2.5">
                            <legend className="sr-only">Lớp muốn chuyển đến</legend>
                            {data.options.length === 0 && <p className="text-sm text-slate-700">Chưa có lớp khác để chuyển.</p>}
                            {data.options.map(option => (
                                <label key={option.class_id} className={`flex min-h-[72px] min-w-0 items-center gap-3 rounded-xl border px-3 py-3 sm:px-4 ${option.is_full ? 'border-slate-200 bg-slate-50' : selectedId === option.class_id ? 'cursor-pointer border-indigo-500 bg-indigo-50' : 'cursor-pointer border-indigo-100 hover:bg-indigo-50/60'}`}>
                                    <input
                                        type="radio"
                                        name="target_class_id"
                                        value={option.class_id}
                                        required
                                        disabled={option.is_full}
                                        checked={option.class_id === selectedId}
                                        onChange={() => {
                                            setSelectedId(option.class_id)
                                            setNotice(undefined)
                                            setNeedsReconfirmation(false)
                                        }}
                                        className="size-4 shrink-0 focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-brand-primary"
                                    />
                                    <span className="min-w-0 grow">
                                        <span className="block wrap-anywhere font-semibold text-slate-950">{option.class_name}</span>
                                        <span className="mt-1 block wrap-anywhere text-sm text-slate-700">{describeSession(option.first_session)}</span>
                                    </span>
                                    {option.is_full && <span className="shrink-0 rounded-full bg-rose-100 px-2 py-1 text-xs font-semibold text-rose-900">Lớp đầy</span>}
                                </label>
                            ))}
                        </fieldset>
                        <div className="mt-6 flex flex-wrap justify-between gap-3">
                            <button type="button" onClick={goBack} className={secondaryButton}>Quay lại</button>
                            {data.options.some(option => !option.is_full) && (
                                <button type="submit" className={primaryButton}>
                                    Tiếp tục <ArrowRight aria-hidden="true" className="size-4" />
                                </button>
                            )}
                        </div>
                    </form>
                )}

                {step === 3 && current && selected && (
                    <form aria-labelledby={formId} method="post" onSubmit={confirm} className="mt-4 space-y-5">
                        <div className="grid items-stretch gap-3 md:grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)] md:gap-4">
                            <ClassCard label="Lớp hiện tại" name={current.class_name} schedule={currentSchedule} topic={upcoming?.topic} tone="previous" />
                            <ArrowRight aria-hidden="true" className="hidden size-5 self-center text-indigo-800 md:block" />
                            <ClassCard label="Lớp mới" name={selected.class_name} schedule={describeSession(selected.first_session)} topic={selected.first_session?.topic} tone="new" />
                        </div>
                        <p className="flex items-start gap-2 rounded-xl bg-indigo-50 px-4 py-3 text-sm text-indigo-950">
                            <Info aria-hidden="true" className="mt-0.5 size-4 shrink-0" />
                            <span>{selected.first_session ? 'Lớp mới sẽ áp dụng ngay sau khi xác nhận.' : 'Bạn vẫn có thể chuyển lớp. Lịch học sẽ hiển thị khi lớp mới có buổi phù hợp.'}</span>
                        </p>
                        <div className="flex flex-wrap justify-between gap-3">
                            <button type="button" disabled={submitting} onClick={goBack} className={secondaryButton}>Quay lại</button>
                            <button type="submit" disabled={submitting} className={primaryButton}>
                                {submitting ? 'Đang chuyển lớp…' : needsReconfirmation ? 'Xác nhận lại' : 'Xác nhận chuyển lớp'}
                                <ArrowRight aria-hidden="true" className="size-4" />
                            </button>
                        </div>
                    </form>
                )}
            </div>
        </section>
    )
}
