import React from 'react'
import { Search, Bell, Menu } from 'lucide-react'
import type { UserProfile } from '../types/dashboard.types'
import { ProfileDropdown } from '../../../components/layout/ProfileDropdown'

interface HeaderProps {
  user: UserProfile
  onOpenMobileMenu?: () => void
}

export const Header: React.FC<HeaderProps> = ({ user, onOpenMobileMenu }) => {
  return (
    <header className="flex items-center justify-between gap-2 sm:gap-6 py-0 select-none w-full">
      {/* Mobile Hamburger Button */}
      <button
        type="button"
        onClick={onOpenMobileMenu}
        aria-label="Mở menu"
        className="lg:hidden p-2 rounded-xl bg-white shadow-xs border border-slate-200/60 text-slate-700 hover:bg-slate-50 transition-colors shrink-0 cursor-pointer"
      >
        <Menu className="w-5 h-5" strokeWidth={2} />
      </button>

      {/* Search Input Bar - Dạng Pill bo tròn hoàn toàn theo ảnh mẫu */}
      <div className="flex-1 min-w-0 max-w-[580px] lg:max-w-[640px] xl:max-w-[680px]">
        <div className="flex items-center h-[42px] sm:h-[50px] bg-white rounded-full px-3.5 sm:px-5 shadow-[0_2px_12px_rgba(0,0,0,0.03)] border border-[#EDF1F8] focus-within:border-[#4F46E5]/40 focus-within:ring-3 focus-within:ring-[#4F46E5]/10 transition-all">
          <Search className="w-4.5 h-4.5 sm:w-5 sm:h-5 text-[#94A3B8] shrink-0 mr-2 sm:mr-3.5" strokeWidth={2.2} />
          <input
            type="text"
            placeholder="Tìm kiếm bài học, khóa học..."
            className="w-full bg-transparent text-[13px] sm:text-[14.5px] font-medium text-[#1E293B] placeholder-[#94A3B8] outline-none truncate"
          />
        </div>
      </div>

      {/* Right Actions: Chuông thông báo nét đậm + Profile */}
      <div className="flex items-center gap-1.5 sm:gap-5 shrink-0">
        <button
          type="button"
          aria-label="Thông báo"
          className="relative w-8.5 h-8.5 sm:w-9 sm:h-9 rounded-full flex items-center justify-center text-[#191D23] hover:text-[#4F46E5] hover:bg-slate-100 transition-all cursor-pointer shrink-0"
        >
          <Bell className="w-4.5 h-4.5 sm:w-5 sm:h-5 text-[#191D23]" strokeWidth={2.2} />
          <span className="absolute top-1 sm:top-1.5 right-1 sm:right-1.5 w-2 h-2 rounded-full bg-[#EF4444] ring-2 ring-[#F8FAFD]" />
        </button>

        {/* Thông tin người dùng */}
        <ProfileDropdown user={user} />
      </div>
    </header>
  )
}
