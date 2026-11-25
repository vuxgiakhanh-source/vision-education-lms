'use client'

import { useState, useEffect } from 'react'
import { StudentDashboardLayout } from '../../../../components/layout/student/StudentDashboardLayout'
import { StudentWelcomeBanner } from '../components/StudentWelcomeBanner'
import { StudentKpiStatCards } from '../components/StudentKpiStatCards'
import { StudentTaskListCard } from '../components/StudentTaskListCard'
import { StudentMiniCalendarCard } from '../components/StudentMiniCalendarCard'
import { StudentRecentDocumentsCard } from '../components/StudentRecentDocumentsCard'
import {
  mockKpiStats,
  mockTasks,
  mockDocuments,
  mockCalendarDays,
} from '../mock/dashboard.mock'
import { useAuthProfile } from '../../../auth/guards/AuthGuard'
import { meService } from '../../../auth/me/services/meService'
import { getShortName } from '../../../../lib/getShortName'
import type { MeResponse } from '../../../auth/me/types/meTypes'

export function StudentDashboardPreview() {
  const [previewProfile, setPreviewProfile] = useState<MeResponse | null>(null)
  useEffect(() => {
    if (!localStorage.getItem('access_token')) return

    async function loadUser() {
      try {
        const profile = await meService.getMe()
        setPreviewProfile(profile)
      } catch (error) {
        console.error('Không tải được hồ sơ: ', error)
      }
    }

    loadUser()
  }, [])
  const name = previewProfile ? getShortName(previewProfile.full_name) : 'Đang tải...'
  return <StudentDashboardLayout user={{ name }}><StudentDashboardPage userName={name} /></StudentDashboardLayout>
}

export function StudentDashboardPage({ userName }: { userName?: string }) {
  const profile = useAuthProfile()
  const displayName = userName ?? (profile ? getShortName(profile.full_name) : 'Đang tải...')
  return (
      <div
        className="student-dashboard flex-1 flex flex-col w-full"
        style={{ rowGap: 'var(--gap-main)' }}
      >
        {/* Banner chào mừng */}
        <div className="dashboard-banner min-w-0 wide:shrink-0">
          <StudentWelcomeBanner
            userName={displayName}
            taskCount={mockTasks.length}
          />
        </div>

        {/* Màn rất rộng đưa thống kê lên cạnh banner; lịch và tài liệu xếp dọc. */}
        <div className="grid grid-cols-1 xl:grid-cols-[minmax(0,2.05fr)_minmax(335px,1fr)] wide:grid-cols-[minmax(0,1fr)_380px] ultrawide:contents gap-5 xl:gap-6 wide:gap-7 ultrawide:gap-6 items-start w-full min-w-0">
          {/* Thống kê và việc cần làm */}
          <div
            className="flex flex-col min-w-0 ultrawide:contents"
            style={{ gap: 'var(--gap-left-col)' }}
          >
            <div className="dashboard-stats min-w-0"><StudentKpiStatCards stats={mockKpiStats} /></div>
            <div className="dashboard-tasks min-w-0"><StudentTaskListCard tasks={mockTasks} /></div>
          </div>

          {/* Lịch và tài liệu */}
          <div
            className="dashboard-resources grid grid-cols-1 md:grid-cols-2 xl:grid-cols-1 items-start min-w-0"
            style={{ gap: 'var(--gap-right-col)' }}
          >
            <div className="min-w-0">
              <StudentMiniCalendarCard days={mockCalendarDays} currentMonthYear="Tháng 9, 2024" />
            </div>
            <div className="min-w-0">
              <StudentRecentDocumentsCard documents={mockDocuments} />
            </div>
          </div>
        </div>
      </div>
  )
}
