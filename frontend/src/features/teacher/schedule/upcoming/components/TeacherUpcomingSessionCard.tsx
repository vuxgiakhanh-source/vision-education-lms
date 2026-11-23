import { BookOpen, CalendarDays } from 'lucide-react'
import { formatDayMonthYear } from '../../../../../lib/date'
import styles from '../../components/TeacherSchedule.module.css'
import type { TeacherSession } from '../../types/teacherScheduleTypes'

type Props = {
    session: TeacherSession | null | undefined
    loadError: boolean
}

export function TeacherUpcomingSessionCard({ session, loadError }: Props) {
    return (
        <aside aria-labelledby="teacher-next-session" className={styles.nextCard}>
            <h2 id="teacher-next-session" className="flex items-center gap-3.5 text-[20px] leading-tight font-extrabold tracking-[-.055em] max-[480px]:text-base">
                <CalendarDays size={22} strokeWidth={2} className="shrink-0 text-[#0758bd]" aria-hidden="true" />
                Buổi dạy tiếp theo
            </h2>
            {session ? (
                <>
                    <span className="mt-5 inline-flex rounded-full bg-[#dbe8f9] px-3 py-1 text-[12px] leading-4 font-semibold text-[#1d528d]">{session.className}</span>
                    <p className="mt-3.5 flex items-center gap-2 text-[14px] font-bold">
                        <CalendarDays size={16} className="shrink-0 text-[#36587b]" aria-hidden="true" />
                        {formatDayMonthYear(session.date)} · {session.timeRange}
                    </p>
                    <p className="mt-2 flex items-start gap-2 text-[13px] text-[#29476e]">
                        <BookOpen size={16} className="mt-0.5 shrink-0" aria-hidden="true" />
                        {session.topic}
                    </p>
                </>
            ) : (
                <p role="status" className="mt-4 text-sm text-[#29476e]">
                    {loadError ? 'Không tải được buổi dạy tiếp theo.' : session === null ? 'Chưa có buổi dạy sắp tới.' : 'Đang tải buổi dạy tiếp theo…'}
                </p>
            )}
        </aside>
    )
}
