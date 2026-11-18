'use client'

import { useState, useEffect } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { formatLocalDate } from '../../../../lib/date'
import { weeklyScheduleService } from '../services/weeklyScheduleService'
import type { WeeklyScheduleResponse } from '../types/weeklyScheduleTypes'

export function WeeklyGrid() {
    const [selectedDate, setSelectedDate] = useState(() => formatLocalDate(new Date()))
    const [weeklySchedule, setWeeklySchedule] = useState<WeeklyScheduleResponse | null>(null)
    useEffect(
        () => {
            async function loadWeek() {
                try {
                    const data = await weeklyScheduleService.getWeeklySchedule(selectedDate)
                    setWeeklySchedule(data)
                    console.log('Dữ liệu tuần lấy về:', data.week_start)
                } catch (error) {
                    console.error('Lỗi lấy lịch:', error)
                }
            }
            loadWeek()
        },
        [selectedDate]
    )
    return (
        <section>
            <header>
                <h1> Lịch học </h1>
                <div>
                    <button type="button" aria-label="Tuần trước">
                        <ChevronLeft />
                    </button>
                    <span> {weeklySchedule?.week_start} </span>
                    <button type="button" aria-label="Tuần sau">
                        <ChevronRight />
                    </button>
                </div>
            </header>
        </section>
    )

}