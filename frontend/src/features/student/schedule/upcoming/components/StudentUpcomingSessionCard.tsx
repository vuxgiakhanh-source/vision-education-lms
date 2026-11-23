import { BookOpen, Calendar } from 'lucide-react'
import { formatLocalDateTimeRange } from '../../../../../lib/date'
import type { UpcomingSession } from '../upcomingScheduleService'

interface StudentUpcomingSessionCardProps {
    session: UpcomingSession | null | undefined
    loadError: boolean
}

export function StudentUpcomingSessionCard({ session, loadError }: StudentUpcomingSessionCardProps) {
    return (
        <section className="relative min-h-[170px] min-w-0 overflow-clip rounded-[22px] border border-[#EAEFF5] bg-white p-5 shadow-[0_4px_20px_rgba(20,25,45,0.03)]">
            <svg
                aria-hidden="true"
                viewBox="0 0 120 120"
                className="pointer-events-none absolute -top-3 -right-3 size-28 opacity-75"
            >
                <path d="M42 0C55 34 86 58 120 66V0H42Z" fill="#ECEBFC" />
                <path d="M68 0C78 26 98 44 120 50V0H68Z" fill="#DFDCFA" />
            </svg>

            <div className="relative">
                <div className="flex items-center gap-2">
                    <div className="flex size-7 shrink-0 items-center justify-center rounded-lg bg-[#EEF0FD] text-[#5553E6]">
                        <Calendar aria-hidden="true" className="size-4" strokeWidth={2.2} />
                    </div>
                    <h2 className="text-[15.5px] font-bold tracking-tight text-[#1E293B]">Buổi học tiếp theo</h2>
                </div>

                {session ? (
                    <>
                        <span className="mt-3.5 inline-flex rounded-full bg-[#E8E7FD] px-3 py-1 text-xs font-semibold text-[#4B49D9]">
                            Khối {session.grade}
                        </span>
                        <div className="mt-3.5 space-y-2.5 text-[12.5px] font-medium text-slate-700">
                            <p className="flex items-start gap-2">
                                <Calendar aria-hidden="true" className="mt-0.5 size-4 shrink-0 text-slate-500" />
                                <span className="min-w-0 wrap-break-word">{formatLocalDateTimeRange(session.starts_at, session.ends_at)}</span>
                            </p>
                            <p className="flex items-start gap-2">
                                <BookOpen aria-hidden="true" className="mt-0.5 size-4 shrink-0 text-slate-500" />
                                <span className="min-w-0 wrap-break-word">{session.topic.trim() || 'Buổi học'}</span>
                            </p>
                        </div>
                    </>
                ) : (
                    <p role="status" className="mt-3.5 text-sm leading-relaxed text-slate-600">
                        {loadError ? 'Không tải được buổi học tiếp theo.' : session === undefined ? 'Đang tải lịch…' : 'Chưa có thông tin buổi học tiếp theo.'}
                    </p>
                )}
            </div>
        </section>
    )
}
