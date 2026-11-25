'use client'

import { useRef, useState, type ReactNode } from 'react'
import { X } from 'lucide-react'
import { TeacherHeader } from './TeacherHeader'
import { TeacherSidebar } from './TeacherSidebar'

export function TeacherDashboardLayout({ children }: { children: ReactNode }) {
    const drawer = useRef<HTMLDialogElement>(null)
    const [menuOpen, setMenuOpen] = useState(false)

    function openMenu() {
        drawer.current?.showModal()
        setMenuOpen(true)
    }

    function closeMenu() {
        drawer.current?.close()
    }

    return (
        <div data-teacher-shell className="min-h-dvh bg-[linear-gradient(155deg,#f4f7fc,#edf2fa)] font-sans text-[#101d35] lg:grid lg:grid-cols-[220px_minmax(0,1fr)] wide:grid-cols-[248px_minmax(0,1fr)]">
            <div data-teacher-sidebar className="sticky top-0 hidden h-dvh lg:block">
                <TeacherSidebar />
            </div>
            <dialog ref={drawer} id="teacher-mobile-menu" aria-label="Menu giáo viên" onClose={() => setMenuOpen(false)} onClick={event => { if (event.target === event.currentTarget) closeMenu() }} className="fixed top-0 left-0 m-0 h-dvh max-h-none w-64 max-w-[90vw] bg-transparent p-0 backdrop:bg-slate-900/35 lg:hidden">
                <button type="button" onClick={closeMenu} aria-label="Đóng menu" className="absolute top-4 right-3 grid size-9 place-items-center rounded-full hover:bg-[#e6eef9]">
                    <X size={19} aria-hidden="true" />
                </button>
                <TeacherSidebar onNavigate={closeMenu} />
            </dialog>
            <div data-teacher-content className="min-w-0">
                <TeacherHeader menuOpen={menuOpen} onOpenMenu={openMenu} />
                {children}
            </div>
        </div>
    )
}
