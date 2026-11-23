'use client'

import { useEffect, useRef, useState } from 'react'
import { addCalendarDays, formatCenterDate } from '../../../../lib/date'
import { getTeacherSession } from '../../sessions/services/teacherSessionService'
import { TeacherSessionAdjustmentDialog } from '../../sessions/components/TeacherSessionAdjustmentDialog'
import { toScheduledTeacherSession } from '../services/teacherScheduleSession'
import type { TeacherSession } from '../types/teacherScheduleTypes'
import { TeacherUpcomingSessionCard } from '../upcoming/components/TeacherUpcomingSessionCard'
import { getTeacherUpcomingSession } from '../upcoming/teacherUpcomingSessionService'
import { TeacherWeeklyGrid } from '../weekly/components/TeacherWeeklyGrid'
import { getTeacherWeeklySchedule, type TeacherWeeklySchedule } from '../weekly/services/teacherWeeklyScheduleService'
import styles from '../components/TeacherSchedule.module.css'

function mondayOf(date: string): string {
    const weekday = new Date(`${date}T00:00:00Z`).getUTCDay()
    return addCalendarDays(date, -((weekday + 6) % 7))
}

export function TeacherSchedulePage() {
    const today = formatCenterDate(new Date())
    const [weekStart, setWeekStart] = useState(() => mondayOf(today))
    const [week, setWeek] = useState<TeacherWeeklySchedule>()
    const [weekError, setWeekError] = useState(false)
    const [nextSession, setNextSession] = useState<TeacherSession | null>()
    const [upcomingError, setUpcomingError] = useState(false)
    const [selectedId, setSelectedId] = useState<number | null>(null)
    const [detail, setDetail] = useState<TeacherSession>()
    const [detailError, setDetailError] = useState(false)
    const [scheduleRevision, setScheduleRevision] = useState(0)
    const [savedNotice, setSavedNotice] = useState('')
    const scheduleMain = useRef<HTMLElement>(null)

    useEffect(() => {
        const controller = new AbortController()
        getTeacherWeeklySchedule(weekStart, controller.signal)
            .then(data => {
                if (!controller.signal.aborted) setWeek(data)
            })
            .catch(() => {
                if (!controller.signal.aborted) setWeekError(true)
            })
        return () => controller.abort()
    }, [weekStart, scheduleRevision])

    useEffect(() => {
        const controller = new AbortController()
        getTeacherUpcomingSession(controller.signal)
            .then(data => {
                if (!controller.signal.aborted) setNextSession(data)
            })
            .catch(() => {
                if (!controller.signal.aborted) setUpcomingError(true)
            })
        return () => controller.abort()
    }, [scheduleRevision])

    useEffect(() => {
        if (selectedId === null) return
        const controller = new AbortController()
        getTeacherSession(selectedId, controller.signal)
            .then(data => {
                if (!controller.signal.aborted) setDetail(toScheduledTeacherSession(data))
            })
            .catch(() => {
                if (!controller.signal.aborted) {
                    setDetailError(true)
                    setSelectedId(null)
                }
            })
        return () => controller.abort()
    }, [selectedId])

    useEffect(() => {
        if (scheduleRevision > 0) scheduleMain.current?.focus()
    }, [scheduleRevision])

    function selectSession(id: number | null) {
        setDetail(undefined)
        setDetailError(false)
        setSelectedId(id)
    }

    function changeWeek(date: string) {
        setSavedNotice('')
        setWeek(undefined)
        setWeekError(false)
        selectSession(null)
        setWeekStart(date)
    }

    function reloadSchedule(message = '') {
        selectSession(null)
        setSavedNotice(message)
        setWeek(undefined)
        setWeekError(false)
        setNextSession(undefined)
        setUpcomingError(false)
        setScheduleRevision(revision => revision + 1)
    }

    const displayedWeek = week?.weekStart === weekStart ? week : undefined
    const sessions = displayedWeek?.sessions ?? []
    const selected = detail?.id === selectedId ? detail : undefined
    const notice = weekError ? 'Không tải được lịch của tuần đã chọn.'
        : detailError ? 'Không mở được buổi dạy. Vui lòng thử lại.'
        : selectedId !== null && !selected ? 'Đang tải chi tiết buổi dạy…'
        : savedNotice ? savedNotice
        : !displayedWeek ? 'Đang tải lịch dạy…'
        : sessions.length === 0 ? 'Tuần này chưa có lịch dạy.'
        : undefined

    return (
        <main ref={scheduleMain} tabIndex={-1} aria-labelledby="teacher-schedule-title" className={styles.page}>
            <TeacherWeeklyGrid
                weekStart={weekStart}
                highlightedDate={today}
                sessions={sessions}
                notice={notice}
                onWeekChange={changeWeek}
                onSelectSession={session => {
                    if (session.id !== selectedId) selectSession(session.id)
                }}
            />
            <TeacherUpcomingSessionCard session={nextSession} loadError={upcomingError} />
            {selected && (
                <TeacherSessionAdjustmentDialog
                    session={selected}
                    sessions={sessions}
                    onClose={() => selectSession(null)}
                    onSaved={reloadSchedule}
                    onReload={reloadSchedule}
                />
            )}
        </main>
    )
}
