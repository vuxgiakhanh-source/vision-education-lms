import { BookOpen } from 'lucide-react'
import { formatDayMonth } from '../../../../../lib/date'
import { teachingShifts } from '../../../sessions/types/teacherSessionTypes'
import type { TeacherSession } from '../../types/teacherScheduleTypes'
import styles from '../../components/TeacherSchedule.module.css'

type Props = {
    session: TeacherSession
    weekday: string
    onSelect: (session: TeacherSession) => void
}

export function TeacherWeeklySessionCard({ session, weekday, onSelect }: Props) {
    const { id, className, date, shift, teachingWeek, topic } = session
    return (
        <button
            type="button"
            data-session-id={id}
            className={styles.session}
            onClick={() => onSelect(session)}
            aria-label={`${className}, ${weekday} ${formatDayMonth(date)}, ${teachingShifts[shift].label}, ${topic}`}
        >
            <span className="flex items-center gap-1.5 text-[10px] font-medium text-[#385d86]">
                <span className="grid size-[17px] shrink-0 place-items-center rounded-md bg-[#dbe8fa] text-[#1e5898]">
                    <BookOpen size={12} aria-hidden="true" />
                </span>
                {teachingWeek !== undefined && `Tuần ${teachingWeek}`}
            </span>
            <strong className="mt-1.5 block text-[13px] leading-tight font-extrabold tracking-[-.035em]">{className}</strong>
            <span className="mt-1 block text-[12px] leading-snug tracking-[-.025em] text-[#345476]">{topic}</span>
        </button>
    )
}
