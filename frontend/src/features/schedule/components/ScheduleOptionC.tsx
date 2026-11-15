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
  X,
  Clock,
  Sparkles,
  Info,
  CheckCircle2,
  CalendarRange,
} from 'lucide-react'
import {
  WEEK_DAYS,
  SHIFT_DEFINITIONS,
  MOCK_SESSIONS,
  UPCOMING_SESSION,
} from '../mock/schedule.mock'
import type { ScheduleSessionItem, ShiftType } from '../types/schedule.types'

export const ScheduleOptionC: React.FC = () => {
  const [currentWeek, setCurrentWeek] = useState(9)
  const [selectedSession, setSelectedSession] = useState<ScheduleSessionItem | null>(null)
  const [isChangeModalOpen, setIsChangeModalOpen] = useState(false)
  const [changeType, setChangeType] = useState<'temporary' | 'permanent' | null>(null)
  const [swapSuccessMessage, setSwapSuccessMessage] = useState<string | null>(null)

  const getSession = (dayOfWeek: string, shiftId: ShiftType): ScheduleSessionItem | undefined => {
    return MOCK_SESSIONS.find((s) => s.dayOfWeek === dayOfWeek && s.shiftId === shiftId)
  }

  const getShiftIcon = (shiftId: ShiftType) => {
    switch (shiftId) {
      case 'morning':
        return <SunMedium className="w-5 h-5 text-sky-500 mb-1" />
      case 'afternoon':
        return <Sunset className="w-5 h-5 text-amber-500 mb-1" />
      case 'evening':
        return <Moon className="w-5 h-5 text-indigo-500 mb-1" />
    }
  }

  const handleConfirmSwap = (targetSession: ScheduleSessionItem) => {
    setSelectedSession(null)
    setIsChangeModalOpen(false)
    setSwapSuccessMessage(
      `Đã chuyển tạm thời buổi học sang ${targetSession.dayOfWeek} (${targetSession.timeRange}, Phòng ${targetSession.room}). Buổi gốc đã ghi nhận để cô điểm danh!`
    )
    setTimeout(() => {
      setSwapSuccessMessage(null)
    }, 6000)
  }

  return (
    <div className="w-full flex flex-col lg:flex-row gap-4 xl:gap-5 items-start font-sans relative">
      {/* Toast thông báo thành công */}
      {swapSuccessMessage && (
        <div className="fixed bottom-6 right-6 z-50 bg-[#26227B] text-white px-5 py-3.5 rounded-2xl shadow-xl flex items-center gap-3 animate-in fade-in slide-in-from-bottom-4 duration-300 max-w-md">
          <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
          <p className="text-xs sm:text-[13px] leading-snug">{swapSuccessMessage}</p>
          <button
            type="button"
            onClick={() => setSwapSuccessMessage(null)}
            className="p-1 hover:bg-white/10 rounded-lg text-white/70"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* KHỐI TRÁI: LƯỚI LỊCH */}
      <div className="flex-1 min-w-0 w-full bg-white rounded-[28px] sm:rounded-[32px] p-4 sm:p-5 lg:p-6 border border-slate-100 shadow-[0_4px_30px_rgba(0,0,0,0.02)]">
        {/* Header */}
        <div className="flex flex-wrap items-center justify-between gap-3 mb-5">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-2xl bg-[#EEF0FD] flex items-center justify-center text-[#4F46E5] shrink-0">
              <CalendarDays className="w-5 h-5" strokeWidth={2.2} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
                  Lịch học
                </h2>
                <span className="text-[10.5px] font-semibold bg-emerald-50 text-emerald-700 px-2.5 py-0.5 rounded-full border border-emerald-200/60 hidden sm:inline-block">
                  Tương tác đổi ca
                </span>
              </div>
            </div>
          </div>

          {/* Điều hướng tuần */}
          <div className="flex items-center gap-1.5 sm:gap-2 bg-[#F5F7FB] rounded-full px-3 py-1 sm:py-1.5 text-slate-700 shadow-2xs">
            <button
              type="button"
              onClick={() => setCurrentWeek((w) => Math.max(1, w - 1))}
              className="p-1 hover:bg-slate-200/70 rounded-full text-slate-500 hover:text-slate-800 transition-colors cursor-pointer"
            >
              <ChevronLeft className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
            </button>
            <span className="text-xs sm:text-[13px] font-semibold text-slate-800 px-1 select-none">
              Tuần {currentWeek} · 09 – 15/11/2026
            </span>
            <button
              type="button"
              onClick={() => setCurrentWeek((w) => w + 1)}
              className="p-1 hover:bg-slate-200/70 rounded-full text-slate-500 hover:text-slate-800 transition-colors cursor-pointer"
            >
              <ChevronRight className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
            </button>
          </div>
        </div>

        {/* Lưới tuần 8 cột */}
        <div className="w-full overflow-x-auto pb-1 -mx-0.5 px-0.5">
          <div className="min-w-[620px] lg:min-w-0 grid grid-cols-[82px_repeat(7,minmax(0,1fr))] sm:grid-cols-[90px_repeat(7,minmax(0,1fr))] gap-2 sm:gap-2.5">
            {/* Hàng 0 */}
            <div className="h-13 sm:h-14" />
            {WEEK_DAYS.map((day) => (
              <div
                key={day.dayOfWeek}
                className={`flex flex-col items-center justify-center h-13 sm:h-14 rounded-2xl transition-all ${
                  day.isHighlighted
                    ? 'bg-[#25208F] text-white shadow-md'
                    : 'text-slate-700'
                }`}
              >
                <span
                  className={`text-[13px] sm:text-[13.5px] font-bold ${
                    day.isHighlighted ? 'text-white' : 'text-slate-900'
                  }`}
                >
                  {day.dayOfWeek}
                </span>
                <span
                  className={`text-[10.5px] sm:text-[11px] mt-0.5 ${
                    day.isHighlighted ? 'text-indigo-200 font-medium' : 'text-slate-400 font-medium'
                  }`}
                >
                  {day.dateStr}
                </span>
              </div>
            ))}

            {/* 3 Hàng ca */}
            {SHIFT_DEFINITIONS.map((shift) => (
              <React.Fragment key={shift.id}>
                {/* Header ca */}
                <div
                  className={`h-24 sm:h-28 rounded-2xl p-1.5 sm:p-2 flex flex-col items-center justify-center text-center select-none ${
                    shift.id === 'morning'
                      ? 'bg-[#EAF5FE] text-sky-950'
                      : shift.id === 'afternoon'
                      ? 'bg-[#FFF2E5] text-amber-950'
                      : 'bg-[#F2EDFD] text-indigo-950'
                  }`}
                >
                  {getShiftIcon(shift.id)}
                  <span className="text-[11.5px] sm:text-[12.5px] font-bold leading-tight mt-0.5">
                    {shift.label}
                  </span>
                  <span className="text-[9.5px] sm:text-[10.5px] font-medium text-slate-500 mt-0.5 whitespace-nowrap">
                    {shift.timeRange}
                  </span>
                </div>

                {/* 7 ô */}
                {WEEK_DAYS.map((day) => {
                  const session = getSession(day.dayOfWeek, shift.id)

                  if (!session) {
                    return (
                      <div
                        key={`${day.dayOfWeek}-${shift.id}`}
                        className="h-24 sm:h-28 rounded-2xl bg-[#F5F6FA] transition-colors"
                      />
                    )
                  }

                  if (session.tagType === 'user') {
                    return (
                      <button
                        type="button"
                        key={session.id}
                        onClick={() => setSelectedSession(session)}
                        className="h-24 sm:h-28 rounded-2xl bg-[#EDE8FD] border-2 border-[#332EB8] p-1.5 sm:p-2 flex flex-col items-center justify-start text-center relative shadow-xs cursor-pointer group"
                      >
                        <div className="inline-flex items-center gap-1 bg-[#25208F] text-white text-[9px] sm:text-[10px] font-semibold px-2 py-0.5 rounded-full shadow-2xs">
                          <Check className="w-2.5 h-2.5 stroke-[3]" />
                          <span>{session.tagLabel}</span>
                        </div>
                        <div className="mt-2 sm:mt-2.5">
                          <p className="text-[12px] sm:text-[13px] font-bold text-slate-900 leading-tight">
                            Hàm số
                          </p>
                          <p className="text-[12px] sm:text-[13px] font-bold text-slate-900 leading-tight mt-0.5">
                            bậc hai
                          </p>
                        </div>
                      </button>
                    )
                  }

                  // Ca cùng bài
                  let badgeBg = 'bg-[#E1D4FA] text-[#5B21B6]'
                  let cardBg = 'bg-[#EFE9FE]'

                  if (shift.id === 'afternoon') {
                    badgeBg = 'bg-[#FFE1C2] text-[#C2410C]'
                    cardBg = 'bg-[#FFF3E4]'
                  } else if (shift.id === 'evening') {
                    badgeBg = 'bg-[#C6F7D2] text-[#15803D]'
                    cardBg = 'bg-[#EBFBF0]'
                  }

                  return (
                    <button
                      type="button"
                      key={session.id}
                      onClick={() => setSelectedSession(session)}
                      className={`h-24 sm:h-28 rounded-2xl p-1.5 sm:p-2 flex flex-col items-center justify-start text-center ${cardBg} hover:scale-[1.02] hover:shadow-md transition-all cursor-pointer group`}
                    >
                      <div className={`text-[9px] sm:text-[10px] font-semibold px-2 py-0.5 rounded-md ${badgeBg}`}>
                        {session.tagLabel}
                      </div>
                      <div className="mt-2 sm:mt-2.5">
                        <p className="text-[12px] sm:text-[13px] font-bold text-slate-800 leading-tight">
                          Hàm số
                        </p>
                        <p className="text-[12px] sm:text-[13px] font-bold text-slate-800 leading-tight mt-0.5">
                          bậc hai
                        </p>
                      </div>
                    </button>
                  )
                })}
              </React.Fragment>
            ))}
          </div>
        </div>
      </div>

      {/* KHỐI PHẢI */}
      <div className="w-full lg:w-[240px] xl:w-[260px] shrink-0 flex flex-col gap-3.5">
        {/* Thẻ Buổi học tiếp theo */}
        <div className="w-full bg-white rounded-[26px] p-4 sm:p-5 border border-slate-100 shadow-[0_4px_24px_rgba(0,0,0,0.02)] relative overflow-hidden">
          <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-bl from-[#7C74EA]/25 via-[#9E97F5]/15 to-transparent rounded-bl-[44px] pointer-events-none" />

          <div className="flex items-center gap-2 relative z-10">
            <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-xl bg-[#EEF0FD] flex items-center justify-center text-[#4F46E5]">
              <CalendarDays className="w-4 h-4" strokeWidth={2.2} />
            </div>
            <h3 className="font-bold text-slate-900 text-[14px]">
              Buổi học tiếp theo
            </h3>
          </div>

          <div className="mt-3.5 relative z-10">
            <span className="inline-block px-3 py-1 rounded-full bg-[#EDEAFE] text-[#4F46E5] font-semibold text-xs tracking-tight">
              {UPCOMING_SESSION.subject} {UPCOMING_SESSION.grade}
            </span>
          </div>

          <div className="mt-3.5 flex items-center justify-between text-slate-700 hover:text-slate-900 transition-colors cursor-pointer group relative z-10">
            <div className="flex items-center gap-2 text-xs sm:text-[12.5px] font-medium">
              <Calendar className="w-4 h-4 text-slate-400 group-hover:text-[#4F46E5] transition-colors shrink-0" />
              <span>
                {UPCOMING_SESSION.dateDisplay} · {UPCOMING_SESSION.timeRange}
              </span>
            </div>
            <ChevronRight className="w-4 h-4 text-slate-400 group-hover:translate-x-0.5 transition-transform shrink-0" />
          </div>

          <div className="mt-2 flex items-center gap-2 text-slate-500 text-xs sm:text-[12.5px] font-medium relative z-10">
            <MapPin className="w-4 h-4 text-slate-400 shrink-0" />
            <span>{UPCOMING_SESSION.room}</span>
          </div>
        </div>

        {/* Nút Đổi lịch học mở Modal */}
        <button
          type="button"
          onClick={() => setIsChangeModalOpen(true)}
          className="w-full h-[52px] sm:h-[56px] bg-gradient-to-r from-[#25208F] via-[#332EB8] to-[#4F46E5] text-white font-semibold text-[14.5px] px-4 sm:px-5 rounded-2xl shadow-lg shadow-indigo-600/20 hover:brightness-105 active:scale-[0.99] transition-all flex items-center justify-between cursor-pointer"
        >
          <div className="flex items-center gap-2.5">
            <ArrowLeftRight className="w-4.5 h-4.5" />
            <span>Đổi lịch học</span>
          </div>
          <ChevronRight className="w-4.5 h-4.5" />
        </button>
      </div>

      {/* MODAL 1: CHI TIẾT BUỔI HỌC KHI CLICK VÀO Ô LỊCH */}
      {selectedSession && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl border border-slate-100 animate-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <span className="text-xs font-bold uppercase tracking-wider text-[#5553E6]">
                Chi tiết buổi học
              </span>
              <button
                type="button"
                onClick={() => setSelectedSession(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="mt-4 space-y-3">
              <h3 className="text-xl font-bold text-slate-900">
                {selectedSession.topic}
              </h3>

              <div className="bg-[#F8FAFD] rounded-2xl p-3.5 space-y-2 text-xs sm:text-[13px] text-slate-700">
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-slate-400" />
                  <span>
                    Thứ: <strong>{selectedSession.dayOfWeek}</strong> ({selectedSession.dateDisplay})
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4 text-slate-400" />
                  <span>Khung giờ: <strong>{selectedSession.timeRange}</strong></span>
                </div>
                <div className="flex items-center gap-2">
                  <MapPin className="w-4 h-4 text-slate-400" />
                  <span>Phòng học: <strong>{selectedSession.room}</strong></span>
                </div>
              </div>

              {selectedSession.tagType === 'same_lesson' ? (
                <div className="pt-2">
                  <div className="p-3 bg-purple-50 rounded-xl border border-purple-100 flex items-start gap-2.5 text-xs text-purple-900 mb-4">
                    <Info className="w-4 h-4 text-purple-600 shrink-0 mt-0.5" />
                    <p>
                      Ca này dạy cùng chuyên đề với lịch của bạn. Bạn có thể đổi sang ca này cho tuần 9.
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleConfirmSwap(selectedSession)}
                    className="w-full bg-[#5553E6] hover:bg-[#4745D4] text-white font-semibold py-3 rounded-xl shadow-md transition-colors flex items-center justify-center gap-2"
                  >
                    <Check className="w-4 h-4" />
                    <span>Xác nhận đổi sang ca này</span>
                  </button>
                </div>
              ) : (
                <div className="pt-2">
                  <p className="text-xs text-slate-500 italic text-center">
                    Đây là buổi học chính thức theo lịch cố định của bạn.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* MODAL 2: CHỌN HÌNH THỨC ĐỔI LỊCH (ĐỔI TẠM THỜI HOẶC ĐỔI CỐ ĐỊNH) */}
      {isChangeModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl border border-slate-100 animate-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <ArrowLeftRight className="w-5 h-5 text-[#5553E6]" />
                <h3 className="font-bold text-slate-900 text-lg">Đổi lịch học</h3>
              </div>
              <button
                type="button"
                onClick={() => {
                  setIsChangeModalOpen(false)
                  setChangeType(null)
                }}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <p className="text-xs sm:text-[13px] text-slate-500 mt-3 mb-5">
              Chọn hình thức đổi lịch phù hợp với nhu cầu của bạn:
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
              {/* Lựa chọn 1: Đổi tạm thời */}
              <div
                onClick={() => setChangeType('temporary')}
                className={`p-4 rounded-2xl border-2 transition-all cursor-pointer flex flex-col justify-between ${
                  changeType === 'temporary'
                    ? 'border-[#5553E6] bg-[#EEF0FD]'
                    : 'border-slate-200/80 hover:border-slate-300 bg-white'
                }`}
              >
                <div>
                  <div className="w-8 h-8 rounded-lg bg-indigo-100 text-[#5553E6] flex items-center justify-center mb-3">
                    <Sparkles className="w-4 h-4" />
                  </div>
                  <h4 className="font-bold text-slate-900 text-sm">Đổi tạm thời</h4>
                  <p className="text-[12px] text-slate-500 mt-1 leading-snug">
                    Áp dụng cho <strong>1 buổi</strong> trong tuần này. Các tuần sau vẫn học theo lịch gốc.
                  </p>
                </div>
                <span className="text-[11px] font-semibold text-[#5553E6] mt-4 block">
                  Chọn ca trên lưới →
                </span>
              </div>

              {/* Lựa chọn 2: Đổi cố định */}
              <div
                onClick={() => setChangeType('permanent')}
                className={`p-4 rounded-2xl border-2 transition-all cursor-pointer flex flex-col justify-between ${
                  changeType === 'permanent'
                    ? 'border-[#5553E6] bg-[#EEF0FD]'
                    : 'border-slate-200/80 hover:border-slate-300 bg-white'
                }`}
              >
                <div>
                  <div className="w-8 h-8 rounded-lg bg-purple-100 text-purple-700 flex items-center justify-center mb-3">
                    <CalendarRange className="w-4 h-4" />
                  </div>
                  <h4 className="font-bold text-slate-900 text-sm">Đổi cố định</h4>
                  <p className="text-[12px] text-slate-500 mt-1 leading-snug">
                    Chuyển hẳn sang lớp/ca mới từ tuần sau. Lịch sử đã học được bảo lưu.
                  </p>
                </div>
                <span className="text-[11px] font-semibold text-[#5553E6] mt-4 block">
                  Đăng ký chuyển ca →
                </span>
              </div>
            </div>

            <div className="mt-6 flex justify-end gap-2.5">
              <button
                type="button"
                onClick={() => {
                  setIsChangeModalOpen(false)
                  setChangeType(null)
                }}
                className="px-4 py-2.5 rounded-xl text-slate-600 hover:bg-slate-100 text-xs sm:text-sm font-medium"
              >
                Đóng
              </button>
              {changeType && (
                <button
                  type="button"
                  onClick={() => {
                    setIsChangeModalOpen(false)
                    if (changeType === 'temporary') {
                      alert('Vui lòng chọn 1 ca có nhãn "Cùng bài" trên bảng lịch để hoàn tất đổi tạm thời.')
                    } else {
                      alert('Yêu cầu đổi lịch cố định đã được ghi nhận và gửi đến cô duyệt.')
                    }
                  }}
                  className="px-5 py-2.5 rounded-xl bg-[#5553E6] text-white hover:bg-[#4745D4] text-xs sm:text-sm font-semibold shadow-md"
                >
                  Tiếp tục
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
