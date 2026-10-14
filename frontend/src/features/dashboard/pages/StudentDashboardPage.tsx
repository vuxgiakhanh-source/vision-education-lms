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
        className="flex-1 flex flex-col w-full"
        style={{ gap: 'var(--gap-main)' }}
      >
        {/* 1. Hero Banner - Chiều cao chuẩn tỷ lệ tham chiếu */}
        <WelcomeBanner
          userName={mockUserProfile.name}
          taskCount={mockTasks.length}
        />

        {/* 2. Khung lưới 2 Cột chuẩn phân bổ: 1 cột trên tablet/mobile, 2 cột trên desktop (xl+) */}
        <div className="grid grid-cols-1 xl:grid-cols-12 gap-5 xl:gap-[24px] items-start w-full min-w-0">
          {/* CỘT TRÁI (~67% - col-span-8 trên xl+) */}
          <div
            className="xl:col-span-8 flex flex-col min-w-0"
            style={{ gap: 'var(--gap-left-col)', marginTop: 'var(--left-col-mt)' }}
          >
            <KpiStatCards stats={mockKpiStats} />
            <TaskListCard initialTasks={mockTasks} />
          </div>

          {/* CỘT PHẢI (~33% - col-span-4 trên xl+) */}
          <div
            className="xl:col-span-4 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-1 min-w-0"
            style={{ gap: 'var(--gap-right-col)' }}
          >
            <MiniCalendarCard days={mockCalendarDays} currentMonthYear="Tháng 9, 2024" />
            <RecentDocumentsCard documents={mockDocuments} />
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
