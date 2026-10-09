import React from 'react'
import {
  Bell,
  ArrowRight,
  FileText,
  CalendarCheck,
  Megaphone,
  Star,
} from 'lucide-react'
import type { DashboardNotification } from '../types/dashboard.types'

interface NotificationCardProps {
  notifications: DashboardNotification[]
}

export const NotificationCard: React.FC<NotificationCardProps> = ({
  notifications,
}) => {
  const getNotificationIcon = (type: DashboardNotification['type']) => {
    switch (type) {
      case 'exam':
        return <FileText className="w-4 h-4 text-[#4F46E5]" strokeWidth={2.2} />
      case 'calendar':
        return <CalendarCheck className="w-4 h-4 text-[#2563EB]" strokeWidth={2.2} />
      case 'material':
        return <Megaphone className="w-4 h-4 text-[#4F46E5]" strokeWidth={2.2} />
      case 'achievement':
        return <Star className="w-4 h-4 text-[#4F46E5] fill-[#4F46E5]" strokeWidth={2.2} />
      default:
        return <Bell className="w-4 h-4 text-[#4F46E5]" strokeWidth={2.2} />
    }
  }

  const getIconBackground = (type: DashboardNotification['type']) => {
    if (type === 'calendar') return 'bg-[#EFF6FF]'
    return 'bg-[#EEF2FF]'
  }

  return (
    <div className="bg-white rounded-[26px] p-5 shadow-[0_4px_24px_rgba(0,0,0,0.02)] flex flex-col justify-between select-none">
      {/* Header */}
      <div className="flex items-center justify-between pb-3">
        <div className="flex items-center gap-2">
          <Bell className="w-5 h-5 text-slate-800" strokeWidth={2} />
          <h2 className="text-[15px] font-bold text-slate-900">Thông báo mới</h2>
          <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-[#EEF2FF] text-[#4F46E5]">
            {notifications.length}
          </span>
        </div>
        <button
          type="button"
          className="text-xs font-semibold text-[#4F46E5] hover:text-[#4338CA] flex items-center gap-1 transition-colors"
        >
          <span>Xem tất cả</span>
          <ArrowRight className="w-3.5 h-3.5" strokeWidth={2.2} />
        </button>
      </div>

      {/* Notifications List */}
      <div className="space-y-3 pt-1">
        {notifications.map((item) => (
          <div
            key={item.id}
            className="flex items-start justify-between gap-3 p-1 rounded-2xl hover:bg-slate-50/60 transition-all cursor-pointer"
          >
            {/* Left: Icon + Content */}
            <div className="flex items-start gap-3 min-w-0">
              <div
                className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 mt-0.5 ${getIconBackground(
                  item.type
                )}`}
              >
                {getNotificationIcon(item.type)}
              </div>
              <div className="min-w-0">
                <p className="text-[13px] font-bold text-slate-900 truncate">
                  {item.title}
                </p>
                <p className="text-[11.5px] text-slate-500 line-clamp-1 mt-0.5">
                  {item.description}
                </p>
              </div>
            </div>

            {/* Right: Time Ago & Unread indicator */}
            <div className="flex items-center gap-2 shrink-0 pt-1">
              <span className="text-[11px] text-slate-400">{item.timeAgo}</span>
              {item.isUnread && (
                <span className="w-2 h-2 rounded-full bg-[#4F46E5] shrink-0" />
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
