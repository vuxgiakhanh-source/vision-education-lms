'use client'

import { useEffect, useRef, useState } from 'react'
import { addCalendarDays, formatLocalDate } from '../../../../lib/date'
import { StudentScheduleTransferButton } from '../components/StudentScheduleTransferButton'
import { StudentPermanentTransferFlow } from '../permanent_transfers/StudentPermanentTransferFlow'
import type { PermanentTransferResult } from '../permanent_transfers/permanentTransferService'
import { StudentPendingTransferConfirmations } from '../temporary_transfers/StudentPendingTransferConfirmations'
import { StudentUpcomingSessionCard } from '../upcoming/components/StudentUpcomingSessionCard'
import { getUpcomingSession } from '../upcoming/upcomingScheduleService'
import type { UpcomingSession } from '../upcoming/upcomingScheduleService'
import { StudentWeeklyGrid } from '../weekly/components/StudentWeeklyGrid'
import { weeklyScheduleService } from '../weekly/services/weeklyScheduleService'
import type { WeeklyPreview, WeeklySchedule } from '../weekly/types/weeklyScheduleTypes'

export function StudentSchedulePage({ preview }: { preview?: WeeklyPreview }) {
    const [scheduleRevision, setScheduleRevision] = useState(0)
    const [today, setToday] = useState(() => formatLocalDate(new Date()))
    const [selectedDate, setSelectedDate] = useState(() => preview?.weekStart ?? today)
    const [week, setWeek] = useState<WeeklySchedule | null>(null)
    const [weeklyError, setWeeklyError] = useState<string>()
    const [upcoming, setUpcoming] = useState<UpcomingSession | null>()
    const [upcomingError, setUpcomingError] = useState(false)
    const [isPermanentTransferOpen, setIsPermanentTransferOpen] = useState(false)
    const [permanentTransferNotice, setPermanentTransferNotice] = useState('')
    const scheduleContent = useRef<HTMLDivElement>(null)
    const permanentTransferOpened = useRef(false)

    useEffect(() => {
        let midnightTimer = window.setTimeout(syncToday, 0)

        function syncToday() {
            window.clearTimeout(midnightTimer)
            const now = new Date()
            setToday(formatLocalDate(now))
            const nextMidnight = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1)
            midnightTimer = window.setTimeout(syncToday, nextMidnight.getTime() - now.getTime())
        }

        function syncWhenVisible() {
            if (document.visibilityState === 'visible') syncToday()
        }

        function refreshOnFocus() {
            syncToday()
            if (!preview) setScheduleRevision(revision => revision + 1)
        }

        window.addEventListener('focus', refreshOnFocus)
        document.addEventListener('visibilitychange', syncWhenVisible)
        return () => {
            window.clearTimeout(midnightTimer)
            window.removeEventListener('focus', refreshOnFocus)
            document.removeEventListener('visibilitychange', syncWhenVisible)
        }
    }, [preview])

    useEffect(() => {
        if (preview) return
        const controller = new AbortController()
        weeklyScheduleService.getWeeklySchedule(selectedDate, controller.signal)
            .then(data => {
                if (controller.signal.aborted) return
                setWeek(data)
                setWeeklyError(undefined)
            })
            .catch(() => {
                if (!controller.signal.aborted) setWeeklyError('Không tải được lịch của tuần đã chọn')
            })
        return () => controller.abort()
    }, [preview, scheduleRevision, selectedDate])

    useEffect(() => {
        if (preview) return
        const controller = new AbortController()
        getUpcomingSession(controller.signal)
            .then(data => {
                if (controller.signal.aborted) return
                setUpcoming(data)
                setUpcomingError(false)
            })
            .catch(() => {
                if (controller.signal.aborted) return
                setUpcoming(undefined)
                setUpcomingError(true)
            })
        return () => controller.abort()
    }, [preview, scheduleRevision])

    function refreshSchedule() {
        setUpcoming(undefined)
        setUpcomingError(false)
        setScheduleRevision(revision => revision + 1)
    }

    useEffect(() => {
        if (isPermanentTransferOpen) permanentTransferOpened.current = true
        else if (permanentTransferOpened.current) scheduleContent.current?.focus()
    }, [isPermanentTransferOpen])

    function completePermanentTransfer(result: PermanentTransferResult) {
        const scheduleNotice = result.first_session ? '' : ' Lớp mới chưa có lịch học.'
        setPermanentTransferNotice(`Đã chuyển sang lớp ${result.new_class.class_name}.${scheduleNotice}`)
        setWeek(null)
        setIsPermanentTransferOpen(false)
        refreshSchedule()
    }

    const displayedWeek = preview && selectedDate !== preview.weekStart
        ? { weekStart: selectedDate, sessions: [] }
        : preview ?? week

    return (
        <>
            {isPermanentTransferOpen ? (
                <StudentPermanentTransferFlow
                    upcoming={upcoming}
                    upcomingError={upcomingError}
                    onExit={() => setIsPermanentTransferOpen(false)}
                    onRefreshSchedule={refreshSchedule}
                    onSuccess={completePermanentTransfer}
                />
            ) : (
                <div ref={scheduleContent} tabIndex={-1} className="flex min-w-0 flex-1 flex-col gap-3 focus:outline-none">
                    <p role="status" className={permanentTransferNotice ? 'rounded-xl bg-emerald-50 px-4 py-3 text-sm font-medium text-emerald-900' : 'sr-only'}>
                        {permanentTransferNotice}
                    </p>
                    {!preview && (
                        <StudentPendingTransferConfirmations
                            scheduleRevision={scheduleRevision}
                            onConfirmed={refreshSchedule}
                        />
                    )}
                    <div className="grid w-full min-w-0 grid-cols-[minmax(0,1fr)] gap-4 sm:gap-5 xl:flex-1 xl:grid-cols-[minmax(0,1fr)_280px]">
                        <StudentWeeklyGrid
                            week={displayedWeek}
                            today={today}
                            onWeekChange={days => setSelectedDate(date => addCalendarDays(date, days))}
                            subtitle={preview ? `Dữ liệu mẫu · Khối ${preview.grade}` : undefined}
                            loadError={weeklyError}
                        />
                        <aside className="grid min-w-0 items-start gap-3 self-start md:grid-cols-2 xl:grid-cols-1">
                            <StudentUpcomingSessionCard session={preview ? null : upcoming} loadError={upcomingError} />
                            <StudentScheduleTransferButton
                                onRefreshSchedule={preview ? undefined : refreshSchedule}
                                onOpenPermanentTransfer={preview ? undefined : () => {
                                    setPermanentTransferNotice('')
                                    setIsPermanentTransferOpen(true)
                                }}
                            />
                        </aside>
                    </div>
                </div>
            )}
        </>
    )
}
