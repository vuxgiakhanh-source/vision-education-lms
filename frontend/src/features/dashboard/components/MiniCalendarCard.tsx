import React from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import type { CalendarDayItem } from '../types/dashboard.types'

interface MiniCalendarCardProps {
  days: CalendarDayItem[]
  currentMonthYear?: string
}

export const MiniCalendarCard: React.FC<MiniCalendarCardProps> = ({
  days,
  currentMonthYear = 'Tháng 9, 2024',
}) => {
  const weekDays = ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN']

  return (
    <div
      className="bg-white rounded-[20px] shadow-[0_2px_12px_rgba(20,25,45,0.03)] border border-[#EAEFF5] flex flex-col gap-2 select-none"
      style={{ padding: 'var(--cal-pad)' }}
    >
      {/* Header: Tháng 9, 2024 + Chevrons điều hướng */}
      <div className="flex items-center justify-between pb-1">
        <h3 className="text-[13.5px] sm:text-[14px] wide:text-[16px] font-bold text-slate-800 tracking-tight">
          {currentMonthYear}
        </h3>
        <div className="flex items-center gap-0.5 text-slate-500">
          <button
            type="button"
            aria-label="Tháng trước"
            className="w-7 h-7 rounded-lg hover:bg-slate-100 flex items-center justify-center transition-colors cursor-pointer text-slate-500 hover:text-slate-800"
          >
            <ChevronLeft className="w-4 h-4" strokeWidth={2} />
          </button>
          <button
            type="button"
            aria-label="Tháng sau"
            className="w-7 h-7 rounded-lg hover:bg-slate-100 flex items-center justify-center transition-colors cursor-pointer text-slate-500 hover:text-slate-800"
          >
            <ChevronRight className="w-4 h-4" strokeWidth={2} />
          </button>
        </div>
      </div>

      {/* Hàng các thứ trong tuần: T2 - CN */}
      <div className="grid grid-cols-7 text-center text-[11px] sm:text-[11.5px] font-bold text-slate-500 pb-1">
        {weekDays.map((d) => (
          <div key={d} className="py-0.5">
            {d}
          </div>
        ))}
      </div>

      {/* Lưới các ngày trong tháng */}
      <div className="grid grid-cols-7 text-center text-[12px] sm:text-[12.5px] wide:text-[14px] gap-y-0.5">
        {days.map((item, index) => {
          let dayClasses = 'text-slate-300 font-normal'
          if (item.isCurrentMonth) {
            dayClasses = 'text-slate-800 font-semibold'
          }

          return (
            <div
              key={`${item.day}-${index}`}
              className="flex flex-col items-center justify-center relative"
              style={{ height: 'var(--cal-cell-h)' }}
            >
              {item.isSelected ? (
                <div className="w-7 h-7 sm:w-6 sm:h-6 wide:w-7 wide:h-7 wide:text-[13px] ultrawide:text-[14px] rounded-full bg-[#5553E6] text-white font-bold flex items-center justify-center shadow-xs text-[12px]">
                  {item.day}
                </div>
              ) : item.isHighlighted ? (
                <div className="w-7 h-7 sm:w-6 sm:h-6 wide:w-7 wide:h-7 wide:text-[13px] ultrawide:text-[14px] rounded-full bg-[#EEF0FD] text-[#5553E6] font-bold flex flex-col items-center justify-center relative text-[12px]">
                  <span>{item.day}</span>
                  <span className="w-1.5 h-1.5 rounded-full bg-[#5553E6] absolute bottom-0.5" />
                </div>
              ) : (
                <div className="w-7 h-7 sm:w-6 sm:h-6 wide:w-7 wide:h-7 wide:text-[13px] ultrawide:text-[14px] rounded-full hover:bg-slate-100 flex flex-col items-center justify-center transition-colors cursor-pointer">
                  <span className={dayClasses}>{item.day}</span>
                  {item.hasEventDot && item.isCurrentMonth && (
                    <span className="w-1.5 h-1.5 rounded-full bg-[#5553E6] -mt-0.5" />
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
