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
} from 'lucide-react'
import {
  WEEK_DAYS,
  SHIFT_DEFINITIONS,
  MOCK_SESSIONS,
  UPCOMING_SESSION,
} from '../mock/schedule.mock'
import type { ScheduleSessionItem, ShiftType } from '../types/schedule.types'

export const ScheduleOptionA: React.FC = () => {
  const [currentWeek, setCurrentWeek] = useState(9)
  const [selectedMobileDay, setSelectedMobileDay] = useState('T3')

  const getSession = (dayOfWeek: string, shiftId: ShiftType): ScheduleSessionItem | undefined => {
    return MOCK_SESSIONS.find((s) => s.dayOfWeek === dayOfWeek && s.shiftId === shiftId)
  }

  const getShiftIcon = (shiftId: ShiftType) => {
    switch (shiftId) {
      case 'morning':
        return <SunMedium className="w-5 h-5 text-sky-500 mb-0.5" strokeWidth={2.2} />
      case 'afternoon':
        return <Sunset className="w-5 h-5 text-amber-500 mb-0.5" strokeWidth={2.2} />
      case 'evening':
        return <Moon className="w-5 h-5 text-indigo-500 mb-0.5" strokeWidth={2.2} />
    }
  }

  return (
    <div className="grid grid-cols-1 xl:grid-cols-[minmax(0,1fr)_280px] gap-4 sm:gap-5 items-start w-full font-sans select-none">
      {/* KHỐI TRÁI: LƯỚI LỊCH HỌC CHÍNH (Bản ưng số 3 - 142px Gốc Nguyên Bản) */}
      <section className="bg-white rounded-[22px] sm:rounded-[24px] border border-[#EAEFF5] shadow-[0_4px_20px_rgba(20,25,45,0.03)] p-4 sm:p-5 select-none min-w-0 flex flex-col">
        {/* Header của thẻ Lịch học */}
        <div className="flex flex-wrap items-center justify-between gap-3 pb-4 shrink-0">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-[#EEF0FD] text-[#5553E6] flex items-center justify-center shrink-0">
              <CalendarDays className="w-4.5 h-4.5" strokeWidth={2.2} />
            </div>
            <div>
              <h1 className="text-[19px] sm:text-[21px] font-bold text-[#1E293B] tracking-tight">
                Lịch học
              </h1>
            </div>
          </div>

          {/* Điều hướng tuần: < Tuần 9 • 09 – 15/11/2026 > */}
          <div className="flex items-center gap-1.5 sm:gap-2">
            <button
              type="button"
              onClick={() => setCurrentWeek((w) => Math.max(1, w - 1))}
              className="w-8 h-8 rounded-full bg-white border border-[#EAEFF5] hover:bg-slate-50 flex items-center justify-center text-slate-600 transition-colors cursor-pointer shadow-sm"
              aria-label="Tuần trước"
            >
              <ChevronLeft className="w-4 h-4" strokeWidth={2.2} />
            </button>
            <div className="px-3 sm:px-4 py-1.5 rounded-full bg-white border border-[#EAEFF5] text-[12px] sm:text-[13px] font-semibold text-[#1E293B] shadow-sm whitespace-nowrap">
              Tuần {currentWeek} · 09 – 15/11/2026
            </div>
            <button
              type="button"
              onClick={() => setCurrentWeek((w) => w + 1)}
              className="w-8 h-8 rounded-full bg-white border border-[#EAEFF5] hover:bg-slate-50 flex items-center justify-center text-slate-600 transition-colors cursor-pointer shadow-sm"
              aria-label="Tuần sau"
            >
              <ChevronRight className="w-4 h-4" strokeWidth={2.2} />
            </button>
          </div>
        </div>

        {/* 1. MOBILE VIEW (<768px): Chọn ngày bằng tab, xem ca học dạng card đứng tiện lợi */}
        <div className="md:hidden flex flex-col gap-3">
          {/* Thanh tab 7 ngày */}
          <div className="grid grid-cols-7 gap-1.5 pb-1">
            {WEEK_DAYS.map((day) => {
              const isSelected = day.dayOfWeek === selectedMobileDay
              return (
                <button
                  key={day.dayOfWeek}
                  type="button"
                  onClick={() => setSelectedMobileDay(day.dayOfWeek)}
                  className={`py-2 rounded-xl flex flex-col items-center justify-center transition-all cursor-pointer ${
                    isSelected
                      ? 'bg-gradient-to-b from-[#4543D4] to-[#312FB5] text-white shadow-[0_4px_12px_rgba(69,67,212,0.28)]'
                      : 'bg-[#F3F5FA] text-[#1E293B] hover:bg-[#EAEFF8]'
                  }`}
                >
                  <span className="text-[12px] font-bold leading-tight">{day.dayOfWeek}</span>
                  <span
                    className={`text-[10.5px] font-medium leading-tight mt-0.5 ${
                      isSelected ? 'text-white/90' : 'text-slate-500'
                    }`}
                  >
                    {day.dateStr}
                  </span>
                </button>
              )
            })}
          </div>

          {/* Danh sách 3 ca học của ngày được chọn */}
          <div className="space-y-2.5 pt-1">
            {SHIFT_DEFINITIONS.map((shift) => {
              const session = getSession(selectedMobileDay, shift.id)
              return (
                <div
                  key={shift.id}
                  className={`rounded-2xl p-3.5 border transition-all ${
                    session?.tagType === 'user'
                      ? 'bg-[#EAE9FC] border-[#3E3C8E] shadow-sm'
                      : session
                      ? 'bg-[#F8F9FE] border-[#E5E9F2]'
                      : 'bg-[#FAFBFD] border-[#EFF2F7] opacity-70'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      {getShiftIcon(shift.id)}
                      <span className="text-[13.5px] font-bold text-[#1E293B]">
                        {shift.label}
                      </span>
                      <span className="text-xs text-slate-500 font-medium">
                        ({shift.timeRange})
                      </span>
                    </div>

                    {session?.tagType === 'user' && (
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-[#4341CC] text-white text-[11px] font-semibold">
                        <Check className="w-3 h-3 stroke-[2.8]" />
                        <span>Ca của bạn</span>
                      </span>
                    )}
                    {session?.tagType === 'same_lesson' && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full bg-[#D8D6F8] text-[#4B47B5] text-[11px] font-semibold">
                        Cùng bài
                      </span>
                    )}
                  </div>

                  {session ? (
                    <div className="pl-7">
                      <p className="text-[14px] font-bold text-[#1E293B]">{session.topic}</p>
                      <p className="text-xs text-slate-500 mt-0.5">Phòng {session.room}</p>
                    </div>
                  ) : (
                    <p className="text-xs text-slate-400 pl-7 italic">Không có ca học</p>
                  )}
                </div>
              )
            })}
          </div>
        </div>

        {/* 2. TABLET & DESKTOP VIEW (>=768px): Chiều cao hàng 142px chuẩn Bản ưng số 3 */}
        <div className="hidden md:flex flex-col min-w-0">
          <div className="grid grid-cols-[96px_repeat(7,minmax(0,1fr))] lg:grid-cols-[112px_repeat(7,minmax(0,1fr))] grid-rows-[48px_repeat(3,142px)] gap-1.5">
            {/* Hàng 0: Header các cột ngày */}
            <div className="rounded-2xl bg-[#F3F5FA]" />

            {/* Cột 1 đến 7: Thứ & Ngày */}
            {WEEK_DAYS.map((day) => (
              <div
                key={day.dayOfWeek}
                className={`rounded-2xl flex flex-col items-center justify-center transition-all ${
                  day.isHighlighted
                    ? 'bg-gradient-to-b from-[#4543D4] to-[#312FB5] text-white shadow-[0_6px_16px_rgba(69,67,212,0.28)]'
                    : 'bg-[#F3F5FA] text-[#1E293B]'
                }`}
              >
                <span
                  className={`text-[13px] 2xl:text-[14px] font-bold leading-tight ${
                    day.isHighlighted ? 'text-white' : 'text-[#1E293B]'
                  }`}
                >
                  {day.dayOfWeek}
                </span>
                <span
                  className={`text-[11px] 2xl:text-[12px] font-medium leading-tight mt-0.5 ${
                    day.isHighlighted ? 'text-white/90' : 'text-slate-500'
                  }`}
                >
                  {day.dateStr}
                </span>
              </div>
            ))}

            {/* Các hàng ca học (Ca 1, Ca 2, Ca 3) */}
            {SHIFT_DEFINITIONS.map((shift) => (
              <React.Fragment key={shift.id}>
                {/* Cột tiêu đề Ca bên trái */}
                <div
                  className={`rounded-2xl p-1.5 2xl:p-2.5 flex flex-col items-center justify-center text-center gap-1 select-none ${
                    shift.id === 'morning'
                      ? 'bg-[#EAF2FF]'
                      : shift.id === 'afternoon'
                      ? 'bg-[#FFF3E6]'
                      : 'bg-[#ECECFE]'
                  }`}
                >
                  {getShiftIcon(shift.id)}
                  <span className="text-[11.5px] 2xl:text-[13px] font-bold text-[#1E293B] leading-snug whitespace-nowrap">
                    {shift.label}
                  </span>
                  <span className="text-[11px] 2xl:text-[12px] font-medium text-slate-600 leading-tight whitespace-nowrap">
                    {shift.timeRange}
                  </span>
                </div>

                {/* 7 ô theo 7 ngày */}
                {WEEK_DAYS.map((day) => {
                  const session = getSession(day.dayOfWeek, shift.id)

                  if (!session) {
                    // Ô trống: mảng phẳng bento #F5F6FB không viền
                    return (
                      <div
                        key={`${day.dayOfWeek}-${shift.id}`}
                        className="rounded-2xl bg-[#F5F6FB] transition-colors"
                      />
                    )
                  }

                  if (session.tagType === 'user') {
                    // Ô "Ca của bạn" - Nền tím pastel, viền tím sắc sảo, badge chuẩn
                    return (
                      <div
                        key={session.id}
                        className="rounded-2xl bg-[#EAE9FC] border-[1.5px] border-[#3E3C8E] px-1 py-3 flex flex-col items-center justify-center gap-2 lg:gap-2.5 text-center shadow-[0_2px_10px_rgba(85,83,230,0.08)] cursor-pointer transition-transform hover:-translate-y-0.5 min-w-0"
                      >
                        <span className="inline-flex items-center gap-1 px-1.5 2xl:px-2 py-0.5 rounded-full bg-[#4341CC] text-white text-[10.5px] 2xl:text-[11px] font-semibold leading-none whitespace-nowrap max-w-full">
                          <Check className="w-2.5 h-2.5 stroke-[2.8]" />
                          <span>Ca của bạn</span>
                        </span>
                        <span className="text-[12px] 2xl:text-[13px] font-semibold text-[#1E293B] leading-snug">
                          <span className="block">Hàm số</span>
                          <span className="block">bậc hai</span>
                        </span>
                      </div>
                    )
                  }

                  // Ô "Cùng bài": mảng pastel phẳng mềm, badge đồng bộ
                  let badgeBg = 'bg-[#D8D6F8] text-[#4B47B5]'
                  let cardBg = 'bg-[#ECEBFC] hover:bg-[#E4E2FA]'

                  if (shift.id === 'afternoon') {
                    badgeBg = 'bg-[#FDE6C4] text-[#B46914]'
                    cardBg = 'bg-[#FFF4E5] hover:bg-[#FDEBD2]'
                  } else if (shift.id === 'evening') {
                    badgeBg = 'bg-[#CEEFD8] text-[#1D7A43]'
                    cardBg = 'bg-[#ECFAF0] hover:bg-[#DFF5E6]'
                  }

                  return (
                    <div
                      key={session.id}
                      className={`rounded-2xl px-1 py-3 flex flex-col items-center justify-center gap-2 lg:gap-2.5 text-center cursor-pointer transition-all hover:-translate-y-0.5 min-w-0 ${cardBg}`}
                    >
                      <span className={`inline-flex items-center px-1.5 2xl:px-2 py-0.5 rounded-full text-[10.5px] 2xl:text-[11px] font-semibold leading-none whitespace-nowrap ${badgeBg}`}>
                        Cùng bài
                      </span>
                      <span className="text-[12px] 2xl:text-[13px] font-semibold text-[#1E293B] leading-snug">
                        <span className="block">Hàm số</span>
                        <span className="block">bậc hai</span>
                      </span>
                    </div>
                  )
                })}
              </React.Fragment>
            ))}
          </div>
        </div>
      </section>

      {/* KHỐI PHẢI: BUỔI HỌC TIẾP THEO & NÚT ĐỔI LỊCH (Bản ưng số 3) */}
      <aside className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-1 gap-3 content-start items-start self-start min-w-0 select-none">
        {/* Thẻ Buổi học tiếp theo */}
        <div className="bg-white rounded-[22px] border border-[#EAEFF5] shadow-[0_4px_20px_rgba(20,25,45,0.03)] p-5 relative overflow-hidden">
          <svg viewBox="0 0 120 120" className="absolute -top-3 -right-3 w-28 h-28 pointer-events-none opacity-75" fill="none" aria-hidden="true">
            <path d="M42 0C55 34 86 58 120 66V0H42Z" fill="#ECEBFC" />
            <path d="M68 0C78 26 98 44 120 50V0H68Z" fill="#DFDCFA" />
          </svg>

          <div className="relative z-10">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-[#EEF0FD] text-[#5553E6] flex items-center justify-center shrink-0">
                <CalendarDays className="w-4 h-4" strokeWidth={2.2} />
              </div>
              <h2 className="text-[15.5px] font-bold text-[#1E293B] tracking-tight">
                Buổi học tiếp theo
              </h2>
            </div>

            <div className="mt-3.5">
              <span className="inline-flex items-center px-3 py-1 rounded-full bg-[#E8E7FD] text-[#4B49D9] text-[12px] font-semibold">
                {UPCOMING_SESSION.subject} {UPCOMING_SESSION.grade}
              </span>
            </div>

            <div className="mt-3.5 space-y-2.5">
              <div className="w-full flex items-center gap-2 text-left text-[12.5px] font-medium text-slate-700 hover:text-[#5553E6] transition-colors cursor-pointer">
                <Calendar className="w-4 h-4 text-slate-500 shrink-0" strokeWidth={1.9} />
                <span className="truncate">
                  {UPCOMING_SESSION.dateDisplay} · {UPCOMING_SESSION.timeRange}
                </span>
                <ChevronRight className="w-4 h-4 text-slate-400 ml-auto shrink-0" strokeWidth={2} />
              </div>

              <div className="flex items-center gap-2 text-[12.5px] font-medium text-slate-700">
                <MapPin className="w-4 h-4 text-slate-500 shrink-0" strokeWidth={1.9} />
                <span>P.{UPCOMING_SESSION.room}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Nút Đổi lịch học 3D gradient */}
        <div className="bg-white rounded-[22px] border border-[#EAEFF5] shadow-[0_4px_20px_rgba(20,25,45,0.03)] p-3.5">
          <button
            type="button"
            className="w-full h-[52px] rounded-[16px] bg-gradient-to-r from-[#4543D0] via-[#4A48D6] to-[#3432B0] hover:from-[#3D3BC4] hover:to-[#2C2AA0] text-white font-semibold text-[14.5px] px-4 flex items-center justify-between shadow-[0_8px_20px_rgba(69,67,208,0.28)] transition-all cursor-pointer whitespace-nowrap"
          >
            <span className="flex items-center gap-2.5 whitespace-nowrap">
              <ArrowLeftRight className="w-[18px] h-[18px] shrink-0" strokeWidth={2.2} />
              <span>Đổi lịch học</span>
            </span>
            <ChevronRight className="w-[18px] h-[18px] shrink-0" strokeWidth={2.2} />
          </button>
        </div>
      </aside>
    </div>
  )
}
