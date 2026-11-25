import { BookOpen, Calendar } from 'lucide-react'
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
            <svg aria-hidden="true" viewBox="0 0 120 120" className={styles.nextArt}>
                <path d="M42 0C55 34 86 58 120 66V0H42Z" fill="#e5effd" />
                <path d="M68 0C78 26 98 44 120 50V0H68Z" fill="#d6e6fc" />
            </svg>
            <h2 id="teacher-next-session" className={styles.nextTitle}>
                <Calendar size={24} strokeWidth={2} className="shrink-0 text-[#0954b5]" aria-hidden="true" />
                Buổi dạy tiếp theo
            </h2>
            {session ? (
                <>
                    <span className="mt-3.5 inline-flex rounded-full bg-[#dceafb] px-3 py-1 text-[12px] leading-4 font-semibold text-[#1a5095]">{session.className}</span>
                    <p className="mt-3.5 flex items-center gap-2 text-[14px] leading-[1.45] font-bold">
                        <Calendar size={16} className="shrink-0 text-[#385574]" aria-hidden="true" />
                        {formatDayMonthYear(session.date)} · {session.timeRange}
                    </p>
                    <p className="mt-2.5 flex items-center gap-2 text-[14px] leading-[1.45] text-[#385574]">
                        <BookOpen size={16} className="shrink-0" aria-hidden="true" />
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
