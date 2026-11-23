import { CalendarDays, ChevronLeft, ChevronRight, MoveHorizontal } from 'lucide-react'
import { addCalendarDays, formatDayMonth, formatWeekLabel } from '../../../../../lib/date'
import { teachingShiftIds, teachingShifts } from '../../../sessions/types/teacherSessionTypes'
import type { TeacherSession } from '../../types/teacherScheduleTypes'
import { TeacherWeeklySessionCard } from './TeacherWeeklySessionCard'
import styles from '../../components/TeacherSchedule.module.css'

const weekdays = ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN']
const shiftIconClass = 'mb-0.5 size-[26px] shrink-0'
const shiftIcons = {
    morning: (
        <svg viewBox="0 0 32 32" fill="none" aria-hidden="true" className={shiftIconClass}>
            <path d="M16 6V8.5M9.5 8.8L11.2 10.5M22.5 8.8L20.8 10.5M5.8 15H8.3M23.7 15H26.2" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" />
            <path d="M10.5 19C10.5 15.962 12.962 13.5 16 13.5C19.038 13.5 21.5 15.962 21.5 19H10.5Z" fill="currentColor" />
            <path d="M6.5 20.5H25.5" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" />
            <path d="M10 24.5H22" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" />
        </svg>
    ),
    afternoon: (
        <svg viewBox="0 0 32 32" fill="none" aria-hidden="true" className={shiftIconClass}>
            <circle cx={16} cy={16} r={5.5} fill="currentColor" />
            <path d="M16 5.5V8M16 24V26.5M5.5 16H8M24 16H26.5M8.6 8.6L10.4 10.4M21.6 21.6L23.4 23.4M23.4 8.6L21.6 10.4M10.4 21.6L8.6 23.4" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" />
        </svg>
    ),
    evening: (
        <svg viewBox="0 0 32 32" aria-hidden="true" className={shiftIconClass}>
            <path d="M22.8 20.3C21.5 20.9 20 21.2 18.5 21.2C13.1 21.2 8.8 16.9 8.8 11.5C8.8 9.8 9.2 8.2 10 6.8C7.1 8.3 5.2 11.3 5.2 14.7C5.2 19.7 9.3 23.8 14.3 23.8C18 23.8 21.2 21.6 22.6 18.4C22.7 19 22.8 19.7 22.8 20.3Z" fill="currentColor" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round" />
        </svg>
    ),
}

type TeacherWeeklyGridProps = {
    weekStart: string
    highlightedDate: string
    sessions: TeacherSession[]
    notice?: string
    onWeekChange: (weekStart: string) => void
    onSelectSession: (session: TeacherSession) => void
}

export function TeacherWeeklyGrid({ weekStart, highlightedDate, sessions, notice, onWeekChange, onSelectSession }: TeacherWeeklyGridProps) {
    const dates = weekdays.map((day, index) => ({ day, date: addCalendarDays(weekStart, index) }))
    const sessionsBySlot = new Map<string, TeacherSession[]>()
    for (const session of sessions) {
        const slot = `${session.date}:${session.shift}`
        const slotSessions = sessionsBySlot.get(slot)
        if (slotSessions) slotSessions.push(session)
        else sessionsBySlot.set(slot, [session])
    }

    return (
        <section className={styles.weekPanel} aria-labelledby="teacher-schedule-title">
            <header className={styles.weekHeader}>
                <div className="flex items-center gap-2.5">
                    <span className="grid size-8 shrink-0 place-items-center rounded-[11px] bg-[#eaf2ff] text-[#0856bd]">
                        <CalendarDays size={18} strokeWidth={2.2} aria-hidden="true" />
                    </span>
                    <h1 id="teacher-schedule-title" className="text-[21px] leading-tight font-extrabold tracking-[-.05em]">Lịch dạy</h1>
                </div>
                <div className={styles.weekControls}>
                    <button type="button" className={styles.weekButton} aria-label="Tuần trước" onClick={() => onWeekChange(addCalendarDays(weekStart, -7))}>
                        <ChevronLeft size={16} aria-hidden="true" />
                    </button>
                    <span role="status" className="rounded-full bg-white px-4 py-2 text-[13px] leading-4 font-semibold whitespace-nowrap text-[#142d52]">
                        {formatWeekLabel(weekStart)}
                    </span>
                    <button type="button" className={styles.weekButton} aria-label="Tuần sau" onClick={() => onWeekChange(addCalendarDays(weekStart, 7))}>
                        <ChevronRight size={16} aria-hidden="true" />
                    </button>
                </div>
            </header>
            {notice && <p role="status" className="mb-3 text-sm text-[#345476]">{notice}</p>}
            <p className={styles.scrollHint}><MoveHorizontal size={14} aria-hidden="true" />Cuộn ngang để xem các ngày còn lại</p>
            <div className={styles.tableScroll} role="region" aria-label="Lưới lịch dạy theo tuần" tabIndex={0}>
                <table className={styles.weekTable}>
                    <caption className="sr-only">Các ca dạy từ {formatWeekLabel(weekStart)}</caption>
                    <thead>
                        <tr>
                            <th scope="col" className={styles.corner}><span className="sr-only">Ca dạy</span></th>
                            {dates.map(({ day, date }) => (
                                <th key={date} scope="col" data-highlight={date === highlightedDate || undefined} className={styles.day}>
                                    <span>{day}</span>
                                    <time dateTime={date}>{formatDayMonth(date)}</time>
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {teachingShiftIds.map(shift => (
                                <tr key={shift}>
                                    <th scope="row" className={styles.shift} data-shift={shift}>
                                        <div>
                                            {shiftIcons[shift]}
                                            <strong>{teachingShifts[shift].label}</strong>
                                            <span>{teachingShifts[shift].hours.join(' – ')}</span>
                                        </div>
                                    </th>
                                    {dates.map(({ day, date }) => {
                                        const slotSessions = sessionsBySlot.get(`${date}:${shift}`) ?? []
                                        return (
                                            <td key={date} data-highlight={date === highlightedDate || undefined} className={styles.slot}>
                                                {slotSessions.length > 0 && (
                                                    <div className={styles.slotSessions}>
                                                        {slotSessions.map(session => (
                                                            <TeacherWeeklySessionCard
                                                                key={session.id}
                                                                session={session}
                                                                weekday={day}
                                                                onSelect={onSelectSession}
                                                            />
                                                        ))}
                                                    </div>
                                                )}
                                            </td>
                                        )
                                    })}
                                </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </section>
    )
}
