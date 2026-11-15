import React, { useState } from 'react'
import {
  CalendarDays,
  ChevronLeft,
  ChevronRight,
  SunMedium,
  Sunset,
  Moon,
  Check,
  Calendar,
  MapPin,
  ArrowLeftRight,
  Sparkles,
} from 'lucide-react'
import {
  WEEK_DAYS,
  SHIFT_DEFINITIONS,
  MOCK_SESSIONS,
  UPCOMING_SESSION,
} from '../mock/schedule.mock'
import type { ScheduleSessionItem, ShiftType } from '../types/schedule.types'

export const ScheduleOptionB: React.FC = () => {
  const [currentWeek, setCurrentWeek] = useState(9)
  const [selectedDay, setSelectedDay] = useState('T3')

  const getSession = (dayOfWeek: string, shiftId: ShiftType): ScheduleSessionItem | undefined => {
    return MOCK_SESSIONS.find((s) => s.dayOfWeek === dayOfWeek && s.shiftId === shiftId)
  }

  const getShiftIcon = (shiftId: ShiftType) => {
    switch (shiftId) {
      case 'morning':
        return <SunMedium className="w-5 h-5 sm:w-6 sm:h-6 text-sky-500" />
      case 'afternoon':
        return <Sunset className="w-5 h-5 sm:w-6 sm:h-6 text-amber-500" />
      case 'evening':
        return <Moon className="w-5 h-5 sm:w-6 sm:h-6 text-indigo-500" />
    }
  }

  const selectedDayInfo = WEEK_DAYS.find((d) => d.dayOfWeek === selectedDay)

  return (
    <div className="w-full flex flex-col xl:flex-row gap-5 xl:gap-6 items-start font-sans">
      {/* KHỐI CHÍNH LỊCH HỌC */}
      <div className="flex-1 w-full bg-white rounded-3xl p-4 sm:p-6 md:p-7 border border-[#EAEFF5] shadow-xs">
        {/* Header Lịch học & Chuyển tuần */}
        <div className="flex flex-wrap items-center justify-between gap-3 mb-5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-[#EEF0FD] border border-[#5553E6]/20 flex items-center justify-center text-[#5553E6]">
              <CalendarDays className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
                Lịch học
              </h2>
              <p className="text-xs text-slate-400 hidden sm:block">
                Xem lịch học cố định và các ca học thay thế trong tuần
              </p>
            </div>
          </div>

          {/* Điều hướng tuần */}
          <div className="flex items-center gap-2 bg-[#F8FAFD] border border-slate-200/90 rounded-full px-2.5 py-1 text-slate-700 shadow-2xs">
            <button
              type="button"
              onClick={() => setCurrentWeek((w) => Math.max(1, w - 1))}
              className="p-1 hover:bg-slate-200/70 rounded-full text-slate-500 hover:text-slate-800 transition-colors cursor-pointer"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="text-xs sm:text-[13.5px] font-semibold text-slate-800 px-1 select-none">
              Tuần {currentWeek} · 09 – 15/11/2026
            </span>
            <button
              type="button"
              onClick={() => setCurrentWeek((w) => w + 1)}
              className="p-1 hover:bg-slate-200/70 rounded-full text-slate-500 hover:text-slate-800 transition-colors cursor-pointer"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* 1. CHẾ ĐỘ HIỂN THỊ TRÊN MÀN HÌNH LỚN (DESKTOP >= 1024px) - BÁM SÁT MOCKUP */}
        <div className="hidden lg:grid grid-cols-8 gap-3 sm:gap-3.5">
          {/* Header ô trống */}
          <div className="h-14" />

          {/* Các cột ngày */}
          {WEEK_DAYS.map((day) => (
            <div
              key={day.dayOfWeek}
              className={`flex flex-col items-center justify-center h-14 rounded-2xl transition-all ${
                day.isHighlighted
                  ? 'bg-[#26227B] text-white shadow-md'
                  : 'bg-[#F8FAFD] text-slate-700'
              }`}
            >
              <span
                className={`text-[13px] font-bold ${
                  day.isHighlighted ? 'text-white' : 'text-slate-800'
                }`}
              >
                {day.dayOfWeek}
              </span>
              <span
                className={`text-[11px] mt-0.5 ${
                  day.isHighlighted ? 'text-indigo-200 font-medium' : 'text-slate-400 font-medium'
                }`}
              >
                {day.dateStr}
              </span>
            </div>
          ))}

          {/* 3 Hàng ca học */}
          {SHIFT_DEFINITIONS.map((shift) => (
            <React.Fragment key={shift.id}>
              {/* Thẻ mô tả Ca */}
              <div
                className={`h-28 sm:h-32 rounded-2xl p-2.5 sm:p-3 flex flex-col items-center justify-center text-center select-none ${shift.bgLight} border ${shift.borderColor}`}
              >
                {getShiftIcon(shift.id)}
                <span className={`text-[12.5px] sm:text-[13px] font-bold leading-tight mt-1 ${shift.textColor}`}>
                  {shift.label}
                </span>
                <span className="text-[10px] sm:text-[11px] font-medium text-slate-500 mt-1">
                  {shift.timeRange}
                </span>
              </div>

              {/* 7 ô tương ứng */}
              {WEEK_DAYS.map((day) => {
                const session = getSession(day.dayOfWeek, shift.id)

                if (!session) {
                  return (
                    <div
                      key={`${day.dayOfWeek}-${shift.id}`}
                      className="h-28 sm:h-32 rounded-2xl bg-[#F8FAFD]/60 border border-slate-100 hover:border-slate-200 transition-colors"
                    />
                  )
                }

                if (session.tagType === 'user') {
                  return (
                    <div
                      key={session.id}
                      className="h-28 sm:h-32 rounded-2xl bg-[#EEF0FD] border-2 border-[#5553E6] p-2.5 flex flex-col justify-between shadow-xs relative"
                    >
                      <div className="inline-flex items-center gap-1 bg-[#26227B] text-white text-[10px] font-semibold px-2 py-0.5 rounded-full self-start shadow-2xs">
                        <Check className="w-3 h-3 stroke-[3]" />
                        <span>{session.tagLabel}</span>
                      </div>
                      <div className="mt-1">
                        <p className="text-[13px] font-bold text-slate-900 leading-snug">
                          {session.topic}
                        </p>
                      </div>
                      <div className="h-1" />
                    </div>
                  )
                }

                // Cùng bài
                let badgeBg = 'bg-purple-100 text-purple-800'
                let cardBg = 'bg-[#F6EFFE] border-purple-200/70'

                if (shift.id === 'afternoon') {
                  badgeBg = 'bg-amber-100 text-amber-800'
                  cardBg = 'bg-[#FFF7ED] border-amber-200/70'
                } else if (shift.id === 'evening') {
                  badgeBg = 'bg-emerald-100 text-emerald-800'
                  cardBg = 'bg-[#F0FDF4] border-emerald-200/70'
                }

                return (
                  <div
                    key={session.id}
                    className={`h-28 sm:h-32 rounded-2xl p-2.5 flex flex-col justify-between border ${cardBg} hover:scale-[1.02] transition-transform`}
                  >
                    <div className={`text-[10px] font-semibold px-2 py-0.5 rounded-md self-center ${badgeBg}`}>
                      {session.tagLabel}
                    </div>
                    <div className="text-center mt-1">
                      <p className="text-[13px] font-bold text-slate-800 leading-snug">
                        {session.topic}
                      </p>
                    </div>
                    <div className="h-1" />
                  </div>
                )
              })}
            </React.Fragment>
          ))}
        </div>

        {/* 2. CHẾ ĐỘ HIỂN THỊ TRÊN MÀN HÌNH NHỎ (MOBILE / TABLET < 1024px) - THÍCH ỨNG ADAPTIVE */}
        <div className="block lg:hidden">
          {/* Thanh chọn ngày (Day Picker) lướt ngang */}
          <div className="flex items-center gap-2 overflow-x-auto pb-3 pt-1 -mx-2 px-2 no-scrollbar">
            {WEEK_DAYS.map((day) => {
              const isSelected = selectedDay === day.dayOfWeek
              const hasUserSession = MOCK_SESSIONS.some(
                (s) => s.dayOfWeek === day.dayOfWeek && s.tagType === 'user'
              )
              const hasAltSession = MOCK_SESSIONS.some(
                (s) => s.dayOfWeek === day.dayOfWeek && s.tagType === 'same_lesson'
              )

              return (
                <button
                  key={day.dayOfWeek}
                  type="button"
                  onClick={() => setSelectedDay(day.dayOfWeek)}
                  className={`flex-1 min-w-[56px] py-2.5 px-2 rounded-2xl flex flex-col items-center justify-center transition-all cursor-pointer relative ${
                    isSelected
                      ? 'bg-[#26227B] text-white shadow-md scale-105'
                      : 'bg-[#F8FAFD] text-slate-700 hover:bg-slate-100'
                  }`}
                >
                  <span className={`text-xs font-bold ${isSelected ? 'text-white' : 'text-slate-800'}`}>
                    {day.dayOfWeek}
                  </span>
                  <span
                    className={`text-[11px] mt-0.5 font-medium ${
                      isSelected ? 'text-indigo-200' : 'text-slate-400'
                    }`}
                  >
                    {day.dateStr}
                  </span>

                  {/* Chấm tròn biểu thị có buổi học */}
                  {hasUserSession && (
                    <span className="w-1.5 h-1.5 rounded-full bg-[#5553E6] absolute bottom-1.5" />
                  )}
                  {hasAltSession && !hasUserSession && (
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-400 absolute bottom-1.5" />
                  )}
                </button>
              )
            })}
          </div>

          {/* Tiêu đề ngày được chọn */}
          <div className="mt-4 mb-3 flex items-center justify-between px-1">
            <span className="text-sm font-bold text-slate-800">
              Lịch học {selectedDayInfo?.dayOfWeek} ({selectedDayInfo?.dateStr})
            </span>
            <span className="text-xs text-slate-400">3 ca học</span>
          </div>

          {/* Danh sách 3 ca của ngày được chọn dạng thẻ dọc */}
          <div className="space-y-3">
            {SHIFT_DEFINITIONS.map((shift) => {
              const session = getSession(selectedDay, shift.id)

              if (!session) {
                return (
                  <div
                    key={shift.id}
                    className="p-3.5 rounded-2xl bg-[#F8FAFD] border border-slate-100 flex items-center justify-between"
                  >
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded-xl ${shift.bgLight}`}>
                        {getShiftIcon(shift.id)}
                      </div>
                      <div>
                        <p className="text-xs font-bold text-slate-700">{shift.label}</p>
                        <p className="text-[11px] text-slate-400">{shift.timeRange}</p>
                      </div>
                    </div>
                    <span className="text-xs text-slate-400 font-medium">Không có ca</span>
                  </div>
                )
              }

              if (session.tagType === 'user') {
                return (
                  <div
                    key={shift.id}
                    className="p-4 rounded-2xl bg-[#EEF0FD] border-2 border-[#5553E6] shadow-sm flex flex-col gap-2"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className="p-1.5 rounded-lg bg-white/80">
                          {getShiftIcon(shift.id)}
                        </div>
                        <div>
                          <p className="text-xs font-bold text-slate-900">{shift.label}</p>
                          <p className="text-[11px] text-slate-500">{shift.timeRange}</p>
                        </div>
                      </div>
                      <span className="inline-flex items-center gap-1 bg-[#26227B] text-white text-[10.5px] font-semibold px-2.5 py-1 rounded-full shadow-2xs">
                        <Check className="w-3 h-3 stroke-[3]" />
                        {session.tagLabel}
                      </span>
                    </div>

                    <div className="pt-2 border-t border-[#5553E6]/15 flex items-center justify-between">
                      <div>
                        <p className="text-[14px] font-bold text-slate-900">{session.topic}</p>
                        <p className="text-xs text-slate-500">Phòng: {session.room}</p>
                      </div>
                      <span className="text-xs font-semibold text-[#5553E6]">Đang học</span>
                    </div>
                  </div>
                )
              }

              // Ca Cùng bài
              return (
                <div
                  key={shift.id}
                  className="p-4 rounded-2xl bg-[#F6EFFE] border border-purple-200/80 shadow-xs flex flex-col gap-2"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="p-1.5 rounded-lg bg-white/80">
                        {getShiftIcon(shift.id)}
                      </div>
                      <div>
                        <p className="text-xs font-bold text-slate-900">{shift.label}</p>
                        <p className="text-[11px] text-slate-500">{shift.timeRange}</p>
                      </div>
                    </div>
                    <span className="inline-flex items-center gap-1 bg-purple-200 text-purple-800 text-[10.5px] font-semibold px-2 py-0.5 rounded-md">
                      <Sparkles className="w-3 h-3" />
                      {session.tagLabel}
                    </span>
                  </div>

                  <div className="pt-2 border-t border-purple-200/60 flex items-center justify-between">
                    <div>
                      <p className="text-[14px] font-bold text-slate-800">{session.topic}</p>
                      <p className="text-xs text-slate-500">Phòng: {session.room}</p>
                    </div>
                    <button
                      type="button"
                      className="text-xs font-semibold text-[#5553E6] bg-white px-3 py-1.5 rounded-xl border border-indigo-100 shadow-2xs hover:bg-[#EEF0FD]"
                    >
                      Đổi sang ca này
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* KHỐI BÊN PHẢI */}
      <div className="w-full xl:w-[310px] shrink-0 flex flex-col gap-4">
        {/* Thẻ Buổi học tiếp theo */}
        <div className="w-full bg-white rounded-3xl p-5 sm:p-6 border border-[#EAEFF5] shadow-xs relative overflow-hidden">
          <div className="absolute -top-10 -right-10 w-36 h-36 rounded-full bg-gradient-to-br from-indigo-200/50 via-purple-100/40 to-transparent blur-md pointer-events-none" />

          <div className="flex items-center gap-2.5 relative z-10">
            <div className="w-8 h-8 rounded-lg bg-[#EEF0FD] flex items-center justify-center text-[#5553E6]">
              <CalendarDays className="w-4 h-4" />
            </div>
            <h3 className="font-bold text-slate-900 text-[15px]">
              Buổi học tiếp theo
            </h3>
          </div>

          <div className="mt-4 relative z-10">
            <span className="inline-block px-3 py-1 rounded-full bg-[#EEF0FD] text-[#5553E6] font-semibold text-xs">
              {UPCOMING_SESSION.subject} {UPCOMING_SESSION.grade}
            </span>
          </div>

          <div className="mt-4 flex items-center justify-between text-slate-700 hover:text-slate-900 transition-colors cursor-pointer group relative z-10">
            <div className="flex items-center gap-2 text-xs sm:text-[13px] font-medium">
              <Calendar className="w-4 h-4 text-slate-400 group-hover:text-[#5553E6] transition-colors" />
              <span>
                {UPCOMING_SESSION.dateDisplay} · {UPCOMING_SESSION.timeRange}
              </span>
            </div>
            <ChevronRight className="w-4 h-4 text-slate-400 group-hover:translate-x-0.5 transition-transform" />
          </div>

          <div className="mt-2.5 flex items-center gap-2 text-slate-500 text-xs sm:text-[13px] font-medium relative z-10">
            <MapPin className="w-4 h-4 text-slate-400" />
            <span>{UPCOMING_SESSION.room}</span>
          </div>
        </div>

        {/* Nút Đổi lịch học lớn */}
        <button
          type="button"
          className="w-full bg-gradient-to-r from-[#242084] via-[#352DB8] to-[#5553E6] text-white font-semibold text-base py-4 px-5 rounded-2xl shadow-lg shadow-indigo-600/20 hover:shadow-indigo-600/30 hover:brightness-105 active:scale-[0.99] transition-all flex items-center justify-between cursor-pointer"
        >
          <div className="flex items-center gap-3">
            <ArrowLeftRight className="w-5 h-5" />
            <span>Đổi lịch học</span>
          </div>
          <ChevronRight className="w-5 h-5" />
        </button>
      </div>
    </div>
  )
}
