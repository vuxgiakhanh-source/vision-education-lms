import React from 'react'
import {
  Home,
  FileText,
  CalendarCheck,
  UserCheck,
  Lightbulb,
  Settings,
} from 'lucide-react'

import logoImg from '../../../assets/images/logo.webp'

interface NavItem {
  id: string
  label: string
  icon: React.ElementType
  active?: boolean
  opticalOffset?: string
}

export const Sidebar: React.FC = () => {
  const navItems: NavItem[] = [
    { id: 'home', label: 'Trang chủ', icon: Home, active: true },
    { id: 'practice', label: 'Luyện đề', icon: FileText, opticalOffset: '-translate-x-[0.5px]' },
    { id: 'schedule', label: 'Lịch học', icon: CalendarCheck },
    { id: 'exercises', label: 'Bài tập', icon: FileText, opticalOffset: '-translate-x-[0.5px]' },
    { id: 'attendance', label: 'Điểm danh', icon: UserCheck, opticalOffset: 'translate-x-[1px]' },
    { id: 'summary', label: 'Tóm tắt kiến thức', icon: Lightbulb, opticalOffset: '-translate-x-[3px]' },
  ]

  return (
    <aside className="w-[192px] min-w-[192px] bg-white rounded-[26px] shadow-[0_4px_24px_rgba(0,0,0,0.02)] flex flex-col justify-between px-3.5 py-4 select-none shrink-0 h-full z-20">
      <div className="space-y-5">
        {/* Logo & Brand - Centered and aligned */}
        <div className="flex flex-col items-center justify-center pt-1">
          <div className="relative flex items-center justify-center">
            <img
              src={logoImg}
              alt="Vision Education"
              className="h-8 w-auto object-contain"
            />
          </div>
          <span className="mt-1 text-[13px] font-bold text-slate-900 tracking-tight text-center">
            Vision Education
          </span>
        </div>

        {/* Navigation List - Left edge optical alignment for all icons */}
        <nav className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon
            return (
              <button
                key={item.id}
                type="button"
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-[12.5px] font-medium transition-all ${
                  item.active
                    ? 'bg-[#EEF2FF] text-[#4F46E5] font-semibold'
                    : 'text-slate-700 hover:bg-slate-50 hover:text-slate-900'
                }`}
              >
                {/* Fixed-width icon slot with precise left-edge optical offset */}
                <span className="w-5 h-5 flex items-center justify-center shrink-0">
                  <Icon
                    className={`w-[18px] h-[18px] ${item.opticalOffset || ''} ${
                      item.active ? 'text-[#4F46E5] fill-[#4F46E5]' : 'text-slate-700'
                    }`}
                    strokeWidth={1.8}
                  />
                </span>
                <span className="whitespace-nowrap">{item.label}</span>
              </button>
            )
          })}
        </nav>
      </div>

      {/* Settings at Bottom with subtle top divider */}
      <div className="pt-2 border-t border-slate-100/90">
        <button
          type="button"
          className="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-[12.5px] font-medium text-slate-700 hover:bg-slate-50 hover:text-slate-900 transition-colors"
        >
          <span className="w-5 h-5 flex items-center justify-center shrink-0">
            <Settings className="w-[18px] h-[18px] text-slate-700" strokeWidth={1.8} />
          </span>
          <span className="whitespace-nowrap">Cài đặt</span>
        </button>
      </div>
    </aside>
  )
}
