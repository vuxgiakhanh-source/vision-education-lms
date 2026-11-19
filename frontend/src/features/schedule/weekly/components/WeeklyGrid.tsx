'use client'

import { useState, useEffect, Fragment } from 'react'
import { CalendarDays, ChevronLeft, ChevronRight } from 'lucide-react'
import { formatLocalDate, addCalendarDays } from '../../../../lib/date'
import { weeklyScheduleService } from '../services/weeklyScheduleService'
import type { WeeklyScheduleResponse } from '../types/weeklyScheduleTypes'

const WEEK_DAYS = ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN']
const SHIFT_ICON_CLASS = 'mb-0.5 size-7 shrink-0 lg:size-8'
const SHIFT_ROWS = [
    {
        id: 'morning',
        label: 'Ca 1 · Sáng',
        timeRange: '07:30 – 10:30',
        bgClass: 'bg-[#EAF2FF]',
        icon: (
            <svg viewBox="0 0 32 32" className={SHIFT_ICON_CLASS} fill="none" aria-hidden="true">
                <path d="M16 6V8.5M9.5 8.8L11.2 10.5M22.5 8.8L20.8 10.5M5.8 15H8.3M23.7 15H26.2" stroke="#3B82F6" strokeWidth="1.8" strokeLinecap="round" />
                <path d="M10.5 19C10.5 15.962 12.962 13.5 16 13.5C19.038 13.5 21.5 15.962 21.5 19H10.5Z" fill="#3B82F6" />
                <path d="M6.5 20.5H25.5" stroke="#2563EB" strokeWidth="1.8" strokeLinecap="round" />
                <path d="M10 24.5H22" stroke="#60A5FA" strokeWidth="1.8" strokeLinecap="round" />
            </svg>
        ),
    },
    {
        id: 'afternoon',
        label: 'Ca 2 · Chiều',
        timeRange: '14:00 – 17:00',
        bgClass: 'bg-[#FFF3E6]',
        icon: (
            <svg viewBox="0 0 32 32" className={SHIFT_ICON_CLASS} fill="none" aria-hidden="true">
                <circle cx="16" cy="16" r="5.5" fill="#F59E0B" />
                <path d="M16 5.5V8M16 24V26.5M5.5 16H8M24 16H26.5M8.6 8.6L10.4 10.4M21.6 21.6L23.4 23.4M23.4 8.6L21.6 10.4M10.4 21.6L8.6 23.4" stroke="#F59E0B" strokeWidth="1.8" strokeLinecap="round" />
            </svg>
        ),
    },
    {
        id: 'evening',
        label: 'Ca 3 · Tối',
        timeRange: '18:00 – 21:00',
        bgClass: 'bg-[#ECECFE]',
        icon: (
            <svg viewBox="0 0 32 32" className={SHIFT_ICON_CLASS} fill="none" aria-hidden="true">
                <path d="M22.8 20.3C21.5 20.9 20 21.2 18.5 21.2C13.1 21.2 8.8 16.9 8.8 11.5C8.8 9.8 9.2 8.2 10 6.8C7.1 8.3 5.2 11.3 5.2 14.7C5.2 19.7 9.3 23.8 14.3 23.8C18 23.8 21.2 21.6 22.6 18.4C22.7 19 22.8 19.7 22.8 20.3Z" fill="#E0E2FE" stroke="#5553E6" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
        ),
    },
]
const WEEK_NAV_BUTTON_CLASS = 'flex size-8 shrink-0 cursor-pointer items-center justify-center rounded-full border border-[#EAEFF5] bg-white text-slate-600 shadow-sm transition-colors hover:bg-slate-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-primary'

export function formatWeekLabel(weekStart: string): string {
    const weekEnd = addCalendarDays(weekStart, 6)
    const [startYear, startMonth, startDay] = weekStart.split('-')
    const [endYear, endMonth, endDay] = weekEnd.split('-')
    if (endYear === startYear && startMonth < endMonth) {
        return `${startDay}/${startMonth} - ${endDay}/${endMonth}/${endYear}`
    }
    else if (endYear > startYear) {
        return `${startDay}/${startMonth}/${startYear} - ${endDay}/${endMonth}/${endYear}`
    }
    return `${startDay} - ${endDay}/${endMonth}/${endYear}`
}
export function formatDayMonth(weekStart: string): string {
    const [, month, day] = weekStart.split('-')
    return `${day}/${month}`
}



export function WeeklyGrid() {
    const [selectedDate, setSelectedDate] = useState(() => formatLocalDate(new Date()))
    const [weeklySchedule, setWeeklySchedule] = useState<WeeklyScheduleResponse | null>(null)
    const [loadError, setLoadError] = useState<string | null>(null)
    useEffect(
        () => {
            let ignore = false
            async function loadWeek() {
                try {
                    const data = await weeklyScheduleService.getWeeklySchedule(selectedDate)
                    if (ignore) return
                    setLoadError(null)
                    setWeeklySchedule(data)
                    console.log('Dữ liệu tuần lấy về:', data.week_start)
                } catch (error) {
                    console.error('Lỗi lấy lịch:', error)
                    if (ignore) return
                    setLoadError('Không tải được lịch của tuần đã chọn')
                }
            }
            loadWeek()
            return () => { ignore = true }
        },
        [selectedDate]
    )
    return (
        <section className="mx-3.5 my-4 flex min-w-0 flex-col rounded-[22px] border border-[#EAEFF5] bg-white p-4 shadow-[0_4px_20px_rgba(20,25,45,0.03)] sm:mx-6 sm:rounded-[24px] sm:p-5 md:min-h-[calc(100dvh_-_92px)]">
            <header className="flex shrink-0 flex-wrap items-center justify-between gap-3 pb-4">
                <div className="flex items-center gap-2.5">
                    <div className="flex size-8 shrink-0 items-center justify-center rounded-xl bg-brand-light text-brand-primary">
                        <CalendarDays aria-hidden="true" className="size-[18px]" strokeWidth={2.2} />
                    </div>
                    <h1 className="text-[19px] font-bold tracking-tight text-[#1E293B] sm:text-[21px]">Lịch học</h1>
                </div>
                <div className="flex items-center gap-1.5 sm:gap-2">
                    <button
                        type="button"
                        aria-label="Tuần trước"
                        className={WEEK_NAV_BUTTON_CLASS}
                        onClick={() => setSelectedDate(currentDate => addCalendarDays(currentDate, -7))}
                    >
                        <ChevronLeft className="size-4" strokeWidth={2.2} />
                    </button>
                    <span className="rounded-full border border-[#EAEFF5] bg-white px-3 py-1.5 text-[12px] font-semibold whitespace-nowrap text-[#1E293B] shadow-sm sm:px-4 sm:text-[13px]"> {weeklySchedule ? formatWeekLabel(weeklySchedule.week_start) : ''} </span>
                    <button
                        type="button"
                        aria-label="Tuần sau"
                        className={WEEK_NAV_BUTTON_CLASS}
                        onClick={() => setSelectedDate(currentDate => addCalendarDays(currentDate, +7))}
                    >
                        <ChevronRight className="size-4" strokeWidth={2.2} />
                    </button>
                </div>
            </header>
            {loadError ? <p role="alert" className="mb-3 rounded-xl bg-red-50 px-3 py-2 text-sm text-red-700">{loadError}</p> : null}
            <div className="grid flex-1 grid-cols-[96px_repeat(7,minmax(4rem,1fr))] grid-rows-[48px_repeat(3,minmax(108px,1fr))] gap-1.5 overflow-x-auto lg:grid-cols-[112px_repeat(7,minmax(0,1fr))]">
                <div className="rounded-2xl bg-[#F3F5FA]"></div>
                {WEEK_DAYS.map((day, index) => (
                    <div key={day} className="flex flex-col items-center justify-center rounded-2xl bg-[#F3F5FA] text-[#1E293B]">
                        <span className="text-[13.5px] leading-tight font-bold lg:text-sm">{day}</span>
                        <span className="mt-0.5 text-[11px] leading-tight font-medium text-slate-500 lg:text-[11.5px]">
                            {weeklySchedule
                                ? formatDayMonth(addCalendarDays(weeklySchedule.week_start, index))
                                : ''}
                        </span>
                    </div>
                ))}
                {SHIFT_ROWS.map(shift => (
                    <Fragment key={shift.id}>
                        <div className={`flex flex-col items-center justify-center gap-1 rounded-2xl p-2 text-center lg:p-3 ${shift.bgClass}`}>
                            {shift.icon}
                            <span className="text-xs leading-snug font-bold whitespace-nowrap text-[#1E293B] lg:text-[13px]">{shift.label}</span>
                            <span className="text-[10.5px] leading-tight font-medium whitespace-nowrap text-slate-600 lg:text-[11.5px]">{shift.timeRange}</span>
                        </div>
                        {WEEK_DAYS.map(day => (
                            <div key={day} className="rounded-2xl bg-[#F5F6FB]" />
                        ))}
                    </Fragment>
                ))}
            </div>
        </section>
    )
}
