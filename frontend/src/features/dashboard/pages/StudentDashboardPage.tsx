import React from 'react'
import { DashboardLayout } from '../components/DashboardLayout'
import { WelcomeBanner } from '../components/WelcomeBanner'
import { KpiStatCards } from '../components/KpiStatCards'
import { TaskListCard } from '../components/TaskListCard'
import { MiniCalendarCard } from '../components/MiniCalendarCard'
import { RecentDocumentsCard } from '../components/RecentDocumentsCard'
import {
  mockUserProfile,
  mockKpiStats,
  mockTasks,
  mockDocuments,
  mockCalendarDays,
} from '../mock/dashboard.mock'

export const StudentDashboardPage: React.FC = () => {
  return (
    <DashboardLayout user={mockUserProfile}>
      <div
        className="student-dashboard flex-1 flex flex-col w-full"
        style={{ rowGap: 'var(--gap-main)' }}
      >
        {/* Banner chào mừng */}
        <div className="dashboard-banner min-w-0 wide:shrink-0">
          <WelcomeBanner
            userName={mockUserProfile.name}
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
            <div className="dashboard-stats min-w-0"><KpiStatCards stats={mockKpiStats} /></div>
            <div className="dashboard-tasks min-w-0"><TaskListCard tasks={mockTasks} /></div>
          </div>

          {/* Lịch và tài liệu */}
          <div
            className="dashboard-resources grid grid-cols-1 md:grid-cols-2 xl:grid-cols-1 items-start min-w-0"
            style={{ gap: 'var(--gap-right-col)' }}
          >
            <div className="min-w-0">
              <MiniCalendarCard days={mockCalendarDays} currentMonthYear="Tháng 9, 2024" />
            </div>
            <div className="min-w-0">
              <RecentDocumentsCard documents={mockDocuments} />
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
