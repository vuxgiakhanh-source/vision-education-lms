import React from 'react'
import { Search, Bell, ChevronDown, User } from 'lucide-react'
import type { UserProfile } from '../types/dashboard.types'

interface HeaderProps {
  user: UserProfile
}

export const Header: React.FC<HeaderProps> = ({ user }) => {
  return (
    <header className="flex items-center justify-between gap-4 py-1 select-none">
      {/* Search Bar - Seamless, no harsh border */}
      <div className="relative flex-1 max-w-[480px]">
        <div className="flex items-center bg-white rounded-2xl px-4 py-2.5 shadow-[0_2px_12px_rgba(0,0,0,0.02)] transition-all focus-within:ring-2 focus-within:ring-indigo-100">
          <Search className="w-4 h-4 text-slate-400 shrink-0 mr-3" strokeWidth={2} />
          <input
            type="text"
            placeholder="Tìm kiếm bài học, chủ đề, dạng bài..."
            className="w-full bg-transparent text-sm text-slate-800 placeholder-slate-400 outline-none"
          />
          <kbd className="inline-flex items-center px-2 py-0.5 text-[11px] font-semibold text-slate-500 bg-slate-100/80 rounded-lg shrink-0 ml-2">
            Ctrl K
          </kbd>
        </div>
      </div>

      {/* Right Controls: Notification & User Profile */}
      <div className="flex items-center gap-5">
        {/* Notification Bell */}
        <button
          type="button"
          aria-label="Thông báo"
          className="relative w-10 h-10 rounded-full bg-white shadow-[0_2px_10px_rgba(0,0,0,0.02)] flex items-center justify-center hover:bg-slate-50 text-slate-700 transition-colors"
        >
          <Bell className="w-5 h-5 text-slate-700" strokeWidth={1.8} />
          {/* Red indicator dot */}
          <span className="absolute top-2 right-2 w-2 h-2 rounded-full bg-rose-500 ring-2 ring-white" />
        </button>

        {/* User Profile Dropdown Trigger */}
        <div className="flex items-center gap-2.5 cursor-pointer p-1 rounded-xl hover:bg-white/40 transition-colors">
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
          <ChevronDown className="w-4 h-4 text-slate-600" strokeWidth={2} />
        </div>
      </div>
    </header>
  )
}
