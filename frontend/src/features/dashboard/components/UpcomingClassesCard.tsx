import React from 'react'
import {
  CalendarDays,
  Clock,
  MapPin,
  User,
  MoreVertical,
  ArrowRight,
} from 'lucide-react'
import type { UpcomingClassItem } from '../types/dashboard.types'

interface UpcomingClassesCardProps {
  classes: UpcomingClassItem[]
}

export const UpcomingClassesCard: React.FC<UpcomingClassesCardProps> = ({
  classes,
}) => {
  return (
    <div className="bg-white rounded-[26px] p-5 shadow-[0_4px_24px_rgba(0,0,0,0.02)] flex flex-col justify-between select-none">
      {/* Header */}
      <div className="flex items-center justify-between pb-3">
        <div className="flex items-center gap-2">
          <CalendarDays className="w-5 h-5 text-[#4F46E5]" strokeWidth={2.2} />
          <h2 className="text-[15px] font-bold text-slate-900">Buổi học sắp tới</h2>
          <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-[#EEF2FF] text-[#4F46E5]">
            {classes.length}
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

      {/* Class List - Exact lavender date pill matching screenshot */}
      <div className="space-y-3 pt-1">
        {classes.map((item) => (
          <div
            key={item.id}
            className="flex items-center justify-between py-1.5 px-1 rounded-2xl hover:bg-slate-50/50 transition-all"
          >
            {/* Left: Date block + Class details */}
            <div className="flex items-center gap-4 min-w-0">
              {/* Date Block in soft lavender */}
              <div className="w-14 h-14 rounded-2xl bg-[#EEF2FF] flex flex-col items-center justify-center shrink-0">
                <span className="text-[11px] font-bold text-[#4F46E5] uppercase">
                  {item.dayOfWeek}
                </span>
                <span className="text-[15px] font-extrabold text-slate-900 leading-tight">
                  {item.date}
                </span>
              </div>

              {/* Class Info */}
              <div className="min-w-0">
                <h3 className="text-[13.5px] font-bold text-slate-900 truncate mb-1">
                  {item.topic}
                </h3>
                <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-[11.5px] text-slate-500">
                  <span className="flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5 text-slate-400" strokeWidth={2} />
                    {item.time}
                  </span>
                  <span className="flex items-center gap-1">
                    <MapPin className="w-3.5 h-3.5 text-slate-400" strokeWidth={2} />
                    {item.room}
                  </span>
                  <span className="flex items-center gap-1">
                    <User className="w-3.5 h-3.5 text-slate-400" strokeWidth={2} />
                    {item.teacher}
                  </span>
                </div>
              </div>
            </div>

            {/* Right: CTA button & Menu */}
            <div className="flex items-center gap-2 shrink-0 pl-2">
              <button
                type="button"
                className="px-4 py-2 text-xs font-semibold text-[#4F46E5] bg-[#EEF2FF] hover:bg-[#E0E7FF] rounded-xl transition-colors whitespace-nowrap"
              >
                Xem chi tiết
              </button>
              <button
                type="button"
                aria-label="Thao tác"
                className="text-slate-300 hover:text-slate-600 p-1"
              >
                <MoreVertical className="w-4 h-4" strokeWidth={2} />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
