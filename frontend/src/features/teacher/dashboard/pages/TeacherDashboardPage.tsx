'use client'

import Image from 'next/image'
import { useState, type CSSProperties, type ReactNode } from 'react'
import {
    ArrowRight, Bell, CalendarDays, ChartNoAxesColumnIncreasing, ChartPie, ChevronDown,
    ChevronLeft, ChevronRight, CircleAlert, GraduationCap, SquareCheck, TriangleAlert, Users,
    type LucideIcon,
} from 'lucide-react'
import { addCalendarDays } from '../../../../lib/date'
import dashboardBanner from '../assets/dashboard-banner.webp'
import {
    attendanceByClass, studentsToWatch, teacherMetrics, teacherTasks, teachingDate, teachingSessions,
} from '../mock/teacherDashboardMock'
import styles from './TeacherDashboardPage.module.css'

const metricIcons = { violet: Users, sky: CalendarDays, amber: TriangleAlert, green: ChartPie }
const weekdays = ['CN', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7']
type AttendanceClass = keyof typeof attendanceByClass

function DashboardPanel({ id, title, icon: Icon, action, children }: {
    id: string
    title: string
    icon: LucideIcon
    action: ReactNode
    children: ReactNode
}) {
    return (
        <section id={id} aria-labelledby={`${id}-title`} className={`${styles.panel} scroll-mt-4`}>
            <div className={styles.panelHead}>
                <h2 id={`${id}-title`} className="flex min-w-0 items-center gap-2.5 font-extrabold">
                    <Icon aria-hidden="true" className="size-[1em] shrink-0 text-[#1665ad]" strokeWidth={1.8} />
                    {title}
                </h2>
                {action}
            </div>
            {children}
        </section>
    )
}

export function TeacherDashboardPage() {
    const [date, setDate] = useState(teachingDate)
    const [attendanceClass, setAttendanceClass] = useState<AttendanceClass>('all')
    const visibleSessions = date === teachingDate ? teachingSessions : []
    const weekday = weekdays[new Date(`${date}T00:00:00`).getDay()]
    const attendance = attendanceByClass[attendanceClass]
    const total = attendance.present + attendance.excused + attendance.absent
    const rate = Math.round(100 * attendance.present / total)
    const attendanceRows = [
        { label: 'Có mặt:', value: attendance.present, color: '#32ab77' },
        { label: 'Xin phép:', value: attendance.excused, color: '#ffbd23' },
        { label: 'Vắng:', value: attendance.absent, color: '#fa5f76' },
    ]
    const linkStyle = 'inline-flex shrink-0 items-center gap-1 whitespace-nowrap text-[.91rem] font-semibold tracking-[-.035em] text-[#135eaa] max-[480px]:text-xs'

    return (
        <main className={styles.dashboard}>
            <header className={styles.banner}>
                <span className={styles.bannerArt}>
                    <Image src={dashboardBanner} alt="" fill priority sizes="(max-width: 1023px) 60vw, 65vw" className="object-fill" />
                </span>
                <span className={styles.bannerIcon}>
                    <GraduationCap aria-hidden="true" className="size-[3.05rem] max-[752px]:size-9" strokeWidth={1.8} />
                </span>
                <div className="relative min-w-0">
                    <h1>Dashboard giáo viên</h1>
                    <p>Theo dõi lịch dạy, lớp học và công việc trong ngày</p>
                </div>
            </header>
            <div className={styles.grid}>
                <section aria-label="Tổng quan" className={styles.metrics}>
                    {teacherMetrics.map(metric => {
                        const Icon = metricIcons[metric.tone]
                        return (
                            <div key={metric.label} className={`${styles.panel} ${styles.metric}`} data-tone={metric.tone}>
                                <span className={styles.metricIcon}>
                                    <Icon aria-hidden="true" className="size-[55%]" strokeWidth={1.8} />
                                </span>
                                <div className="min-w-0">
                                    <p>{metric.label}</p>
                                    <strong>{metric.value}</strong>
                                </div>
                                <ChevronRight size={13} aria-hidden="true" className="ml-auto shrink-0 text-[#263e65] max-[570px]:hidden" />
                            </div>
                        )
                    })}
                </section>

                <DashboardPanel id="lich-day-hom-nay" title={date === teachingDate ? 'Lịch dạy hôm nay' : 'Lịch dạy'} icon={CalendarDays} action={
                    <div className="flex shrink-0 items-center gap-2 whitespace-nowrap text-[.82rem] font-semibold tracking-[-.035em] text-[#143253]">
                        <button type="button" aria-label="Ngày trước" onClick={() => setDate(value => addCalendarDays(value, -1))} className={styles.dateButton}><ChevronLeft size={14} aria-hidden="true" /></button>
                        <time dateTime={date}>{weekday}, {date.split('-').reverse().join('/')}</time>
                        <button type="button" aria-label="Ngày sau" onClick={() => setDate(value => addCalendarDays(value, 1))} className={styles.dateButton}><ChevronRight size={14} aria-hidden="true" /></button>
                    </div>
                }>
                    <ul className="border-t border-[#e2eaf7]">
                        {visibleSessions.map(session => (
                            <li key={session.name} data-tone={session.tone} className={styles.session}>
                                <span className={styles.sessionTime}>{session.time}</span>
                                <div className="min-w-0">
                                    <strong className="block text-[.89rem] leading-tight font-extrabold tracking-[-.065em]">{session.name}</strong>
                                    <div className="mt-0.5 flex flex-wrap gap-1.5 text-[.76rem] font-semibold tracking-[-.025em]">
                                        <span className={styles.shift}>{session.shift}</span>
                                        {session.upcoming && <span className="rounded-full bg-[#e9f4ff] px-2 py-0.5 text-[#185ba2]">Sắp tới</span>}
                                    </div>
                                </div>
                            </li>
                        ))}
                    </ul>
                    {!visibleSessions.length && <p className="py-8 text-center text-sm text-[#536b8d]">Chưa có lịch dạy ngày này.</p>}
                </DashboardPanel>

                <DashboardPanel id="hoc-sinh-can-chu-y" title="Học sinh cần chú ý" icon={Users} action={
                    <button type="button" disabled className={linkStyle}>Xem chi tiết <ArrowRight size={13} aria-hidden="true" /></button>
                }>
                    <ul className="border-t border-[#e2eaf7]">
                        {studentsToWatch.map(student => (
                            <li key={student.name} className={styles.student}>
                                <span aria-hidden="true" className={styles.studentAvatar}>
                                    {student.name.split(' ').at(-1)?.[0]}
                                </span>
                                <div className={styles.studentName}>
                                    <strong>{student.name}</strong><p>{student.group}</p>
                                </div>
                                <span className={styles.studentReason}><CircleAlert size={13} aria-hidden="true" className="shrink-0 text-[#f16b78]" />{student.reason}</span>
                                <button type="button" disabled className={styles.reminder}><Bell size={12} aria-hidden="true" />Nhắc nhở</button>
                            </li>
                        ))}
                    </ul>
                </DashboardPanel>

                <DashboardPanel id="viec-can-lam" title="Việc cần làm" icon={SquareCheck} action={
                    <button type="button" disabled className={linkStyle}>Xem tất cả <ChevronRight size={13} aria-hidden="true" /></button>
                }>
                    <div className="divide-y divide-[#e8edf8] border-t border-[#e8edf8]">
                        {teacherTasks.map(task => (
                            <label key={task.id} className={styles.task}>
                                <span aria-hidden="true" className="h-[77%] w-1 rounded-full" style={{ backgroundColor: task.color }} />
                                <input type="checkbox" className="peer size-[14px] accent-[#2068b2]" />
                                <span className="text-[.89rem] leading-tight font-extrabold tracking-[-.05em] peer-checked:text-[#536b8d] peer-checked:line-through">{task.title}</span>
                                {task.badge && <span className="rounded-full bg-[#f9e2ec] px-2 py-0.5 text-[.81rem] font-semibold tracking-[-.025em] whitespace-nowrap text-[#a23147]">{task.badge}</span>}
                            </label>
                        ))}
                    </div>
                </DashboardPanel>

                <DashboardPanel id="chuyen-can-tuan-nay" title="Chuyên cần tuần này" icon={ChartNoAxesColumnIncreasing} action={
                    <label className="relative inline-flex shrink-0 items-center">
                        <span className="sr-only">Lọc chuyên cần theo lớp</span>
                        <select value={attendanceClass} onChange={event => setAttendanceClass(event.target.value as AttendanceClass)} className="cursor-pointer appearance-none pr-5 text-[.93rem] font-semibold text-[#183556]">
                            <option value="all">Tất cả lớp</option>
                            <option value="12A">Toán 12A</option>
                            <option value="12B">Toán 12B</option>
                            <option value="11C">Toán 11C</option>
                        </select>
                        <ChevronDown size={13} aria-hidden="true" className="pointer-events-none absolute right-0" />
                    </label>
                }>
                    <div className={styles.attendance} aria-live="polite">
                        <div className={styles.dial} style={{ '--dial-fill': `${rate * .695}%` } as CSSProperties}>
                            <strong>{rate}%</strong><span>Chuyên cần</span>
                        </div>
                        <ul className="grid min-w-0 gap-1.5 text-[.87rem] font-semibold tracking-[-.04em]">
                            {attendanceRows.map(row => (
                                <li key={row.label} className="flex items-center justify-between gap-1.5 whitespace-nowrap">
                                    <span className="flex items-center gap-2"><span aria-hidden="true" className="size-[9px] shrink-0 rounded-full" style={{ backgroundColor: row.color }} />{row.label}</span>
                                    <strong>{row.value}/{total}</strong>
                                </li>
                            ))}
                        </ul>
                    </div>
                </DashboardPanel>
            </div>
        </main>
    )
}
