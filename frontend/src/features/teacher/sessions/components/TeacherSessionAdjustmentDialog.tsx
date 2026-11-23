import { isAxiosError } from 'axios'
import { ArrowLeftRight, CalendarRange, CalendarX, Check, Settings2 } from 'lucide-react'
import { useEffect, useRef, useState, type FormEvent } from 'react'
import { formatCenterDate, getSessionShift } from '../../../../lib/date'
import { TeacherSessionDialog, formatClassTitle, formatLessonDate } from './TeacherSessionDialog'
import { moveTeacherSession } from '../move_session/services/moveSessionService'
import { swapTeacherSessions } from '../swap_sessions/services/swapSessionsService'
import type { TeacherSessionRecord } from '../services/teacherSessionService'
import { teachingShiftIds, teachingShifts, type TeachingShift, type TeachingSlot } from '../types/teacherSessionTypes'
import styles from './TeacherSessionDialog.module.css'

type Props = {
    session: TeacherSessionRecord
    sessions: TeacherSessionRecord[]
    onClose: () => void
    onSaved: (message: string) => void
    onReload: () => void
}

type Mode = 'details' | 'move' | 'swap' | 'review'

type AdjustmentPreview =
    | { kind: 'move'; target: TeachingSlot }
    | { kind: 'swap'; target: TeacherSessionRecord }

const panelClass = styles['dialog-section']
const buttonClass = styles['dialog-button']
const primaryClass = `${buttonClass} ${styles['dialog-primary']}`
const footerClass = styles['dialog-footer']

function SlotSummary({ label, slot, isNew = false }: { label: string; slot: { date: string; timeRange: string }; isNew?: boolean }) {
    return (
        <div className={`${styles['reschedule-time']} ${isNew ? styles.new : ''}`}>
            <strong>{label}</strong>
            <time dateTime={slot.date}>{formatLessonDate(slot.date)}</time>
            <span className={styles['time-range']}>{slot.timeRange}</span>
        </div>
    )
}

export function TeacherSessionAdjustmentDialog({ session, sessions, onClose, onSaved, onReload }: Props) {
    const stepHeading = useRef<HTMLHeadingElement>(null)
    const previousMode = useRef<Mode>('details')
    const [mode, setMode] = useState<Mode>('details')
    const today = formatCenterDate(new Date())
    const [date, setDate] = useState(() => session.date < today ? today : session.date)
    const [shift, setShift] = useState<TeachingShift>(() => getSessionShift(session.startsAt))
    const [swapId, setSwapId] = useState<number | null>(null)
    const [adjustment, setAdjustment] = useState<AdjustmentPreview | null>(null)
    const [saving, setSaving] = useState(false)
    const submissionPending = useRef(false)
    const [saveError, setSaveError] = useState<{ message: string; reload?: boolean }>()
    const swapTarget = adjustment?.kind === 'swap' ? adjustment.target : undefined
    const targetSlot = adjustment?.kind === 'move' ? {
        date: adjustment.target.date,
        timeRange: teachingShifts[adjustment.target.shift].hours.join(' – '),
    } : swapTarget
    const adjustmentButton = `${buttonClass} ${styles['adjustment-button']}`

    useEffect(() => {
        if (previousMode.current !== mode) stepHeading.current?.focus()
        previousMode.current = mode
    }, [mode])

    function reviewAdjustment(event: FormEvent<HTMLFormElement>) {
        event.preventDefault()
        if (mode === 'swap') {
            const other = sessions.find(item => item.id === swapId)
            if (!other) return
            setAdjustment({ kind: 'swap', target: other })
        } else {
            setAdjustment({ kind: 'move', target: { date, shift } })
        }
        setSaveError(undefined)
        setMode('review')
    }

    async function saveAdjustment(event: FormEvent<HTMLFormElement>) {
        event.preventDefault()
        if (!adjustment || submissionPending.current || saveError?.reload) return
        submissionPending.current = true
        setSaving(true)
        setSaveError(undefined)

        try {
            if (adjustment.kind === 'swap') {
                await swapTeacherSessions(session, adjustment.target)
            } else {
                await moveTeacherSession(session, adjustment.target)
            }
            onSaved('Đã lưu điều chỉnh lịch dạy.')
        } catch (error) {
            if (isAxiosError<{ detail?: string | { code?: string; message?: string } }>(error)) {
                const detail = error.response?.data?.detail
                if (typeof detail === 'string') {
                    setSaveError({ message: detail, reload: error.response?.status === 404 })
                    return
                }
                if (detail?.code === 'SESSION_TIME_CHANGED' && detail.message) {
                    setSaveError({ message: detail.message, reload: true })
                    return
                }
            }
            setSaveError({ message: 'Chưa xác nhận được kết quả lưu. Vui lòng thử lại.' })
        } finally {
            submissionPending.current = false
            setSaving(false)
        }
    }

    return (
        <TeacherSessionDialog
            session={session}
            onClose={onClose}
            saving={saving}
            headingRef={mode === 'details' ? stepHeading : undefined}
            actions={
                <section className={panelClass}>
                    <div className={styles['dialog-section-head']}><h3><Settings2 aria-hidden="true" />Điều chỉnh buổi học</h3></div>
                    <div className={styles['dialog-adjustments']}>
                        <button className={adjustmentButton} type="button" onClick={() => setMode('swap')}><ArrowLeftRight aria-hidden="true" /><span><strong>Hoán đổi hai buổi</strong><small>Đổi chỗ hai buổi đã xếp</small></span></button>
                        <button className={adjustmentButton} type="button" onClick={() => setMode('move')}><CalendarRange aria-hidden="true" /><span><strong>Dời buổi</strong><small>Chọn ngày hoặc ca khác</small></span></button>
                        <button className={adjustmentButton} type="button" disabled><CalendarX aria-hidden="true" /><span><strong>Cho nghỉ buổi này</strong><small>Chỉ áp dụng cho buổi này</small></span></button>
                    </div>
                </section>
            }
        >
            {mode === 'details' ? undefined : (mode === 'move' || mode === 'swap') ? (
                <form method="post" onSubmit={reviewAdjustment} aria-labelledby="teacher-adjustment-heading">
                    <div className={styles['dialog-body']}>
                        <section className={`${panelClass} ${styles['reschedule-section']}`} aria-labelledby="teacher-adjustment-heading">
                            <div className={styles['reschedule-heading']}>
                                <h3 id="teacher-adjustment-heading" ref={stepHeading} tabIndex={-1}>{mode === 'move' ? 'Dời buổi' : 'Hoán đổi hai buổi'}</h3>
                                <span className={styles['dialog-status']}>Bước 1 / 2</span>
                            </div>
                            {mode === 'move' ? (
                                <>
                                    <div className={styles['reschedule-date']}>
                                        <label htmlFor="teacher-move-date">Ngày dạy mới</label>
                                        <input id="teacher-move-date" type="date" required min={today} max="9999-12-26" value={date} onChange={event => setDate(event.target.value)} />
                                    </div>
                                    <fieldset className={styles['reschedule-shifts']}>
                                        <legend>Ca dạy mới</legend>
                                        <div className={styles['reschedule-options']}>
                                            {teachingShiftIds.map(option => (
                                                <label key={option} className={styles['reschedule-option']}>
                                                    <input type="radio" name="teachingShift" value={option} checked={shift === option} onChange={() => setShift(option)} />
                                                    <span><strong>Ca {teachingShifts[option].label.split(' · ')[1].toLowerCase()}</strong><small>{teachingShifts[option].hours.join(' – ')}</small></span>
                                                </label>
                                            ))}
                                        </div>
                                    </fieldset>
                                </>
                            ) : (
                                <div className={styles['swap-select']}>
                                    <label htmlFor="teacher-swap-target">Buổi muốn hoán đổi</label>
                                    <select id="teacher-swap-target" required value={swapId ?? ''} onChange={event => setSwapId(event.target.value ? Number(event.target.value) : null)}>
                                        <option value="">Chọn buổi dạy</option>
                                        {sessions.filter(item => item.id !== session.id).map(item => (
                                            <option key={item.id} value={item.id}>{item.className} · {formatLessonDate(item.date)} · {item.timeRange}</option>
                                        ))}
                                    </select>
                                </div>
                            )}
                        </section>
                    </div>
                    <footer className={`${footerClass} ${styles['reschedule-footer']}`}>
                        <button className={`${buttonClass} ${styles['dialog-back']}`} type="button" onClick={() => setMode('details')}>Quay lại</button>
                        <button className={primaryClass} type="submit">Xem thay đổi</button>
                    </footer>
                </form>
            ) : targetSlot && (
                <form method="post" onSubmit={saveAdjustment} aria-labelledby="teacher-adjustment-review" aria-busy={saving}>
                    <div className={styles['dialog-body']}>
                        <section className={`${panelClass} ${styles['reschedule-section']}`}>
                            <div className={styles['reschedule-heading']}>
                                <h3 id="teacher-adjustment-review" ref={stepHeading} tabIndex={-1}>{swapTarget ? 'Kiểm tra lịch của hai buổi' : 'Kiểm tra lịch dạy mới'}</h3>
                                <span className={styles['dialog-status']}>Bước 2 / 2</span>
                            </div>
                            <p className="text-sm text-slate-700">Đây là các khung giờ bạn chọn. Khi lưu, bài học được xếp theo thứ tự tuần dạy của từng lớp.</p>
                            {swapTarget && <p className={styles['swap-review-title']}>{formatClassTitle(session.className)}</p>}
                            <div className={styles['reschedule-comparison']}>
                                <SlotSummary label="Giờ hiện tại" slot={session} />
                                <SlotSummary label="Khung giờ chọn" slot={targetSlot} isNew />
                            </div>
                            {swapTarget && (
                                <>
                                    <p className={styles['swap-review-title']}>{formatClassTitle(swapTarget.className)}</p>
                                    <div className={styles['reschedule-comparison']}>
                                        <SlotSummary label="Giờ hiện tại" slot={swapTarget} />
                                        <SlotSummary label="Khung giờ chọn" slot={session} isNew />
                                    </div>
                                </>
                            )}
                            {saveError && <p role="alert" className="mt-3 text-sm text-[#991b1b]">{saveError.message}</p>}
                        </section>
                    </div>
                    <footer className={`${footerClass} ${styles['reschedule-footer']}`}>
                        <button className={`${buttonClass} ${styles['dialog-back']}`} type="button" disabled={saving} onClick={() => setMode(swapTarget ? 'swap' : 'move')}>Quay lại</button>
                        {saveError?.reload ? (
                            <button className={primaryClass} type="button" onClick={() => onReload()}>Tải lại lịch</button>
                        ) : (
                            <button className={`${primaryClass} disabled:opacity-50`} type="submit" disabled={saving}>
                                <Check size={16} aria-hidden="true" />
                                {saving ? 'Đang lưu…' : swapTarget ? 'Xác nhận hoán đổi' : 'Xác nhận dời buổi'}
                            </button>
                        )}
                    </footer>
                </form>
            )}
        </TeacherSessionDialog>
    )
}
