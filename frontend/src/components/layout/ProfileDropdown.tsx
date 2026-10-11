import React, { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { User, Settings, LogOut, ChevronDown } from 'lucide-react'
import type { UserProfile } from '../../features/dashboard/types/dashboard.types'

interface ProfileDropdownProps {
  user: UserProfile
}

export const ProfileDropdown: React.FC<ProfileDropdownProps> = ({ user }) => {
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const navigate = useNavigate()

  // Tự động đóng dropdown khi click chuột ra ngoài khoảng trống
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen])

  // Xử lý đăng xuất
  const handleLogout = () => {
    localStorage.removeItem('access_token')
    setIsOpen(false)
    navigate('/login')
  }

  return (
    <div className="relative" ref={dropdownRef}>
      {/* 1. Nút kích hoạt (Trigger) ở góc phải Header */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2.5 cursor-pointer p-1 rounded-xl hover:bg-white/40 transition-colors focus:outline-none"
      >
        <div className="w-9 h-9 rounded-full bg-[#8B5CF6]/20 text-[#7C3AED] flex items-center justify-center font-bold overflow-hidden shadow-xs">
          {user.avatarUrl ? (
            <img src={user.avatarUrl} alt={user.name} className="w-full h-full object-cover" />
          ) : (
            <User className="w-5 h-5 text-[#7C3AED]" strokeWidth={2.2} />
          )}
        </div>
        <span className="text-[14.5px] font-semibold text-slate-800">
          {user.name}
        </span>
        <ChevronDown
          className={`w-4 h-4 text-slate-600 transition-transform duration-200 ${
            isOpen ? 'rotate-180' : ''
          }`}
          strokeWidth={2}
        />
      </button>

      {/* 2. Chiếc thẻ Pop-out khi mở ra (Chuẩn 100% ảnh mẫu) */}
      {isOpen && (
        <div className="absolute right-0 top-[50px] z-50 w-[240px] bg-white rounded-[24px] p-4 shadow-[0_12px_40px_rgba(0,0,0,0.08)] border border-slate-100 select-none animate-in fade-in zoom-in-95 duration-150">
          {/* Mũi tên nhọn (Caret Arrow) chĩa thẳng lên Avatar */}
          <div className="absolute -top-2 right-[118px] w-4 h-4 bg-white rotate-45 border-t border-l border-slate-100" />

          {/* Header Info: Avatar to + Tên + Lớp + Trạng thái */}
          <div className="flex items-center gap-3 relative z-10">
            <div className="w-12 h-12 rounded-full bg-[#EEF2FF] text-[#4F46E5] flex items-center justify-center shrink-0">
              {user.avatarUrl ? (
                <img src={user.avatarUrl} alt={user.name} className="w-full h-full rounded-full object-cover" />
              ) : (
                <User className="w-6 h-6 text-[#4F46E5]" strokeWidth={2.2} />
              )}
            </div>
            <div className="min-w-0">
              <h4 className="text-[15px] font-bold text-slate-900 truncate leading-tight">
                {user.name}
              </h4>
              <p className="text-[12px] text-slate-400 font-medium leading-tight mt-0.5">
                Lớp 12A1
              </p>
              <div className="flex items-center gap-1.5 mt-1">
                <span className="w-2 h-2 rounded-full bg-emerald-500 shrink-0" />
                <span className="text-[11.5px] font-medium text-emerald-500 leading-none">
                  Đang hoạt động
                </span>
              </div>
            </div>
          </div>

          {/* Menu items: Cài đặt */}
          <div className="mt-3.5 pt-2 border-t border-slate-100/90 space-y-0.5">
            <button
              type="button"
              onClick={() => setIsOpen(false)}
              className="w-full flex items-center gap-3 px-2 py-2 rounded-xl text-[13.5px] font-medium text-slate-700 hover:bg-slate-50 transition-colors cursor-pointer text-left"
            >
              <Settings className="w-4 h-4 text-slate-500" strokeWidth={1.8} />
              <span>Cài đặt</span>
            </button>
          </div>

          {/* Divider & Nút Đăng xuất */}
          <div className="mt-1 pt-1 border-t border-slate-100/90">
            <button
              type="button"
              onClick={handleLogout}
              className="w-full flex items-center gap-3 px-2 py-2 rounded-xl text-[13.5px] font-medium text-rose-500 hover:bg-rose-50/60 transition-colors cursor-pointer text-left"
            >
              <LogOut className="w-4 h-4 text-rose-500" strokeWidth={1.8} />
              <span>Đăng xuất</span>
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
