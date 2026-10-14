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

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    setIsOpen(false)
    navigate('/login')
  }

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Nút kích hoạt: Avatar dạng hình tròn mềm mại, đồng bộ với brand primary #5553E6 */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 sm:gap-2.5 cursor-pointer p-1 rounded-xl sm:rounded-2xl hover:bg-white/70 transition-colors focus:outline-none"
      >
        <div className="w-9 h-9 sm:w-9.5 sm:h-9.5 rounded-full bg-[#EEF0FD] text-[#5553E6] border border-[#5553E6]/15 flex items-center justify-center font-bold overflow-hidden shrink-0 shadow-2xs">
          {user.avatarUrl ? (
            <img src={user.avatarUrl} alt={user.name} className="w-full h-full object-cover" />
          ) : (
            <User className="w-5 h-5 text-[#5553E6] fill-[#5553E6]" />
          )}
        </div>
        <span className="hidden sm:inline text-[13.5px] sm:text-[14px] font-semibold text-slate-800 whitespace-nowrap">
          {user.name}
        </span>
        <ChevronDown
          className={`hidden sm:inline w-3.5 h-3.5 text-slate-400 transition-transform duration-200 ${
            isOpen ? 'rotate-180' : ''
          }`}
          strokeWidth={2}
        />
      </button>

      {/* Pop-out Card */}
      {isOpen && (
        <div className="absolute right-0 top-[48px] sm:top-[52px] z-50 w-[230px] bg-white rounded-2xl p-3.5 shadow-[0_12px_36px_rgba(20,25,45,0.08)] border border-[#EAEFF5] select-none animate-in fade-in zoom-in-95 duration-150">
          {/* Header Info */}
          <div className="flex items-center gap-2.5">
            <div className="w-10 h-10 rounded-full bg-[#EEF0FD] text-[#5553E6] flex items-center justify-center shrink-0 border border-[#5553E6]/15 font-semibold text-[14px]">
              {user.avatarUrl ? (
                <img src={user.avatarUrl} alt={user.name} className="w-full h-full rounded-full object-cover" />
              ) : (
                <User className="w-5 h-5 text-[#5553E6]" strokeWidth={2} />
              )}
            </div>
            <div className="min-w-0">
              <h4 className="text-[14px] font-bold text-slate-800 truncate leading-tight">
                {user.name}
              </h4>
              <p className="text-[11.5px] text-slate-400 font-medium leading-tight mt-0.5">
                Lớp 12A1
              </p>
              <div className="flex items-center gap-1.5 mt-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 shrink-0" />
                <span className="text-[11px] font-medium text-emerald-600 leading-none">
                  Đang hoạt động
                </span>
              </div>
            </div>
          </div>

          {/* Menu items */}
          <div className="mt-3 pt-2 border-t border-slate-100 space-y-0.5">
            <button
              type="button"
              onClick={() => setIsOpen(false)}
              className="w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-xl text-[13px] font-medium text-slate-700 hover:bg-slate-50 transition-colors cursor-pointer text-left"
            >
              <Settings className="w-4 h-4 text-slate-400" strokeWidth={1.8} />
              <span>Cài đặt</span>
            </button>
          </div>

          {/* Divider & Nút Đăng xuất */}
          <div className="mt-1 pt-1 border-t border-slate-100">
            <button
              type="button"
              onClick={handleLogout}
              className="w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-xl text-[13px] font-medium text-rose-600 hover:bg-rose-50/70 transition-colors cursor-pointer text-left"
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
