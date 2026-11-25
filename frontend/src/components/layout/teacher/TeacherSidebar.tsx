'use client'

import Image from 'next/image'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Calculator, CalendarDays, ChartNoAxesColumn, FileText, House, MonitorCheck, Settings, Users } from 'lucide-react'
import logo from '../../../assets/images/logo.webp'
import learning from '../../../assets/images/teacher-sidebar-learning.png'

const teacherNavigation = [
    { label: 'Trang chủ', icon: House, href: '/teacher-dashboard' },
    { label: 'Lịch dạy', icon: CalendarDays, href: '/teacher-schedule' },
    { label: 'Lớp học', icon: Calculator },
    { label: 'Học sinh', icon: Users },
    { label: 'Phòng thi ảo', icon: MonitorCheck, href: '/teacher-exams' },
    { label: 'Tài liệu', icon: FileText },
    { label: 'Báo cáo', icon: ChartNoAxesColumn },
    { label: 'Cài đặt', icon: Settings },
]

export function TeacherSidebar({ onNavigate }: { onNavigate?: () => void }) {
    const pathname = usePathname()

    return (
        <aside className="flex h-full flex-col border-r border-[#dbe5f2] bg-[#f0f5fc] px-4 text-[#173b65]">
            <Link data-teacher-brand href="/teacher-dashboard" onClick={onNavigate} className="flex h-[104px] shrink-0 items-center gap-3 px-1.5 pb-2 leading-[1.15]">
                <Image src={logo} alt="" width={57} height={38} className="h-[38px] w-[57px] object-contain [filter:hue-rotate(-27deg)_saturate(.92)_brightness(.96)]" priority />
                <span className="text-[15px] tracking-[-.035em]"><strong className="block font-extrabold text-[#092547]">Vision</strong>Education</span>
            </Link>
            <nav aria-label="Menu giáo viên" className="grid gap-[6px]">
                {teacherNavigation.map(({ label, icon: Icon, href }) => {
                    const row = (
                        <>
                            <Icon size={18} strokeWidth={1.8} aria-hidden="true" />
                            <span>{label}</span>
                        </>
                    )
                    const itemClass = 'flex h-10 items-center gap-3.5 rounded-[13px] px-3.5 text-left text-[13.5px] font-medium tracking-[-.035em]'

                    const isActive = href && (href === pathname || pathname.startsWith(href + '/'))
                    return href ? (
                        <Link key={label} href={href} aria-current={isActive ? 'page' : undefined} onClick={onNavigate} className={`${itemClass} ${isActive ? 'border-l-[3px] border-[#377bbd] bg-[#dfeaf9] pl-[11px] font-bold text-[#10457e]' : 'hover:bg-[#e6eef9]'}`}>
                            {row}
                        </Link>
                    ) : (
                        <span key={label} className={itemClass} aria-disabled="true">{row}</span>
                    )
                })}
            </nav>
            <div className="mt-auto pt-4 pb-[26px] pl-2.5 opacity-90">
                <Image src={learning} alt="" width={64} height={88} unoptimized className="h-auto w-16 [clip-path:inset(55%_29%_0_0)] [filter:hue-rotate(-27deg)]" />
            </div>
        </aside>
    )
}

