import React from 'react'
import {
  Home,
  FileText,
  Calendar,
  BookOpen,
  SquareCheck,
  Lightbulb,
  Settings,
  X,
} from 'lucide-react'
import logoImg from '../../../assets/images/logo.webp'

interface NavItem {
  id: string
  label: string
  icon: React.ElementType
  active?: boolean
}

interface SidebarProps {
  isOpen?: boolean
  onClose?: () => void
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen = false, onClose }) => {
  const navItems: NavItem[] = [
    { id: 'home', label: 'Trang chủ', icon: Home, active: true },
    { id: 'practice', label: 'Luyện đề', icon: FileText },
    { id: 'schedule', label: 'Lịch học', icon: Calendar },
    { id: 'exercises', label: 'Bài tập', icon: BookOpen },
    { id: 'attendance', label: 'Điểm danh', icon: SquareCheck },
    { id: 'summary', label: 'Tóm tắt kiến thức', icon: Lightbulb },
    { id: 'settings', label: 'Cài đặt', icon: Settings },
  ]

  const sidebarContent = (
    <div className="flex flex-col h-full justify-between select-none py-1">
      <div>
        {/* Brand Logo: Cân đối, nhận diện thương hiệu Vision Education sắc nét */}
        <div className="flex items-center justify-between px-2 pt-3 pb-2">
          <div className="flex items-center gap-3">
            <img
              src={logoImg}
              alt="Vision Education"
              className="h-9 sm:h-9.5 w-auto object-contain shrink-0"
            />
            <div className="flex flex-col">
              <span className="text-[16px] font-bold text-slate-900 leading-tight tracking-tight">
                Vision
              </span>
              <span className="text-[13.5px] font-semibold text-slate-500 leading-tight tracking-tight">
                Education
              </span>
            </div>
          </div>

          {/* Close button for mobile drawer */}
          {onClose && (
            <button
              type="button"
              onClick={onClose}
              className="lg:hidden p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
              aria-label="Đóng menu"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>

        {/* Navigation List: Khoảng cách dọc nhịp nhàng, active state tinh tế */}
        <nav className="mt-7 space-y-1.5 px-0.5">
          {navItems.map((item) => {
            const Icon = item.icon
            return (
              <button
                key={item.id}
                type="button"
                className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-[13.5px] transition-all cursor-pointer text-left ${
                  item.active
                    ? 'bg-[#EEF0FD] text-[#5553E6] font-semibold shadow-2xs'
                    : 'text-slate-500 hover:text-slate-900 hover:bg-slate-100/70 font-medium'
                }`}
              >
                <Icon
                  className={`w-[19px] h-[19px] shrink-0 ${
                    item.active ? 'text-[#5553E6]' : 'text-slate-400'
                  }`}
                  strokeWidth={item.active ? 2.2 : 1.8}
                />
                <span className="whitespace-nowrap tracking-tight">{item.label}</span>
              </button>
            )
          })}
        </nav>
      </div>
    </div>
  )

  return (
    <>
      {/* 1. Desktop Sidebar - Thanh thoát, tỷ lệ hài hòa */}
      <aside className="hidden lg:flex w-[215px] xl:w-[235px] 2xl:w-[255px] bg-[#FAFBFD] h-screen border-r border-[#EAEFF5] flex-col p-3.5 xl:p-4 shrink-0 sticky top-0 z-30 transition-all">
        {sidebarContent}
      </aside>

      {/* 2. Mobile Drawer */}
      {isOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div
            className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs transition-opacity"
            onClick={onClose}
          />
          <div className="fixed inset-y-0 left-0 w-64 bg-white shadow-2xl p-4.5 flex flex-col z-50 animate-in slide-in-from-left duration-200">
            {sidebarContent}
          </div>
        </div>
      )}
    </>
  )
}
