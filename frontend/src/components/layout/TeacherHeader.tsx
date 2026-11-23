'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useState } from 'react'
import { Bell, ChevronDown, Menu, Search } from 'lucide-react'
import { useAuthProfile } from '../../features/auth/guards/AuthGuard'

const dashboardSections = [
    { label: 'Lịch dạy hôm nay', href: '#lich-day-hom-nay' },
    { label: 'Học sinh cần chú ý', href: '#hoc-sinh-can-chu-y' },
    { label: 'Việc cần làm', href: '#viec-can-lam' },
    { label: 'Chuyên cần tuần này', href: '#chuyen-can-tuan-nay' },
]

function normalizeSearch(value: string) {
    return value.toLowerCase().normalize('NFD').replace(/\p{Diacritic}/gu, '').replaceAll('đ', 'd').trim()
}

export function TeacherHeader({ menuOpen, onOpenMenu }: { menuOpen: boolean; onOpenMenu: () => void }) {
    const profile = useAuthProfile()
    const router = useRouter()
    const [search, setSearch] = useState('')
    const [searchOpen, setSearchOpen] = useState(false)
    const teacherName = profile?.full_name || 'Giáo viên'
    const initials = teacherName.trim().split(/\s+/).slice(-2).map(word => word[0]).join('').toUpperCase()
    const query = normalizeSearch(search)
    const results = query ? dashboardSections.filter(section => normalizeSearch(section.label).includes(query)) : []

    function logout() {
        localStorage.removeItem('access_token')
        router.replace('/login')
    }

    const iconButton = 'grid size-10 shrink-0 place-items-center rounded-full hover:bg-[#e6eef9] max-[480px]:size-8'
    const popoverClass = 'fixed top-16 right-4 left-auto m-0 w-72 max-w-[calc(100vw-2rem)] rounded-2xl border border-[#e6edf7] bg-white p-4 text-[#091a38] shadow-[0_12px_24px_#21457918]'

    return (
    <header className="relative z-10 flex min-h-[62px] items-center justify-between gap-2.5 bg-[#f2f5fb] px-[clamp(1rem,1.48vw+0.38rem,1.93rem)] py-1 text-[#091a38] max-lg:px-3 max-[480px]:min-h-[54px] max-[480px]:gap-1.5">
        <button type="button" aria-label="Mở menu" aria-controls="teacher-mobile-menu" aria-expanded={menuOpen} className={`${iconButton} lg:hidden`} onClick={onOpenMenu}>
            <Menu size={21} aria-hidden="true" />
        </button>
        <div className="relative min-w-0 flex-1 lg:max-w-[39.2rem]" onBlur={event => { if (!event.currentTarget.contains(event.relatedTarget)) setSearchOpen(false) }}>
            <form role="search" className="flex min-h-12 items-center gap-3.5 rounded-full border border-[#e4ecf8] bg-[#fbfcfe] px-[17px] text-[#314d72] shadow-[0_5px_12px_#274a7808] focus-within:border-[#8cb8ef] max-[480px]:min-h-10 max-[480px]:gap-1.5 max-[480px]:px-2.5" onSubmit={event => { event.preventDefault(); setSearchOpen(true) }}>
                <Search className="size-[23px] shrink-0 max-[480px]:size-4" strokeWidth={1.8} aria-hidden="true" />
                <input type="search" aria-label="Tìm kiếm" value={search} onChange={event => { setSearch(event.target.value); setSearchOpen(true) }} onFocus={() => setSearchOpen(true)} onKeyDown={event => { if (event.key === 'Escape') setSearchOpen(false) }} className="min-w-0 flex-1 bg-transparent py-2 text-[15.5px] tracking-[-.04em] outline-none placeholder:text-[#526a8b] max-[480px]:text-[13px]" placeholder="Tìm kiếm lớp học, học sinh, bài tập, tài liệu..." />
            </form>
            {searchOpen && query && (
                <ul className="absolute inset-x-0 top-[calc(100%+0.5rem)] z-20 rounded-2xl border border-[#e6edf7] bg-white p-2 text-sm shadow-lg">
                    {results.length ? results.map(result => (
                        <li key={result.href}><Link href={`/teacher-dashboard${result.href}`} onClick={() => setSearchOpen(false)} className="block rounded-md px-3 py-2 hover:bg-[#eaf2fd]">{result.label}</Link></li>
                    )) : <li className="px-3 py-2 text-[#536b8d]">Không tìm thấy mục phù hợp.</li>}
                </ul>
            )}
        </div>
        <div className="flex shrink-0 items-center gap-6 max-lg:gap-2 max-[480px]:gap-1.5">
            <button type="button" aria-label="Thông báo" popoverTarget="teacher-notifications" className={`relative ${iconButton}`}>
                <Bell className="size-[26px] max-[480px]:size-5" strokeWidth={1.8} aria-hidden="true" />
                <span className="absolute top-[5px] right-[1px] size-3 rounded-full border-2 border-white bg-[#fa515b]" aria-hidden="true" />
            </button>
            <button type="button" popoverTarget="teacher-profile" aria-label={`Tài khoản ${teacherName}`} className="flex items-center gap-3.5">
                <span aria-hidden="true" className="grid size-[48px] place-items-center rounded-full bg-[linear-gradient(145deg,#e2eafb,#f2f5fc)] text-[20px] font-extrabold tracking-[-.08em] text-[#153568] max-[480px]:size-[37px] max-[480px]:text-base">{initials}</span>
                <strong className="hidden whitespace-nowrap text-[16px] font-extrabold tracking-[-.045em] sm:inline">GV. {teacherName}</strong>
                <ChevronDown size={13} className="hidden sm:block" aria-hidden="true" />
            </button>
            <div id="teacher-notifications" popover="auto" className={popoverClass}>
                <h2 className="font-bold">Thông báo</h2>
                <p className="mt-2 text-sm text-[#536b8d]">Xác nhận điểm danh buổi 4 (12B).</p>
            </div>
            <div id="teacher-profile" popover="auto" className={popoverClass}>
                <h2 className="font-bold">GV. {teacherName}</h2>
                <p className="mt-1 text-sm text-[#536b8d]">Giáo viên</p>
                <button type="button" onClick={logout} className="mt-3 rounded-md px-2 py-1 text-sm font-semibold text-[#941a35] hover:bg-[#f9e2ec]">Đăng xuất</button>
            </div>
        </div>
    </header>
    )
}
