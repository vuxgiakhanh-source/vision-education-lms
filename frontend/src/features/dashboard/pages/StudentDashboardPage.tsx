import React from 'react'
import { DashboardLayout } from '../components/DashboardLayout'
import { WelcomeBanner } from '../components/WelcomeBanner'
import { KpiStatCards } from '../components/KpiStatCards'
import { TaskListCard } from '../components/TaskListCard'
import { NotificationCard } from '../components/NotificationCard'
import { UpcomingClassesCard } from '../components/UpcomingClassesCard'
import { ResourceListCard } from '../components/ResourceListCard'
import {
  mockUserProfile,
  mockKpiStats,
  mockDashboardTasks,
  mockDashboardNotifications,
  mockUpcomingClasses,
  mockResources,
} from '../mock/dashboard.mock'

export const StudentDashboardPage: React.FC = () => {
  return (
    <DashboardLayout user={mockUserProfile}>
      <div className="space-y-4 pt-1">
        {/* 1. Welcome Greeting */}
        <WelcomeBanner
          userName={mockUserProfile.name}
          taskCount={mockDashboardTasks.length}
        />

        {/* 2. Top KPI Cards */}
        <KpiStatCards stats={mockKpiStats} />

        {/* 3. Main 4 Bento Cards (2 Columns x 2 Rows) */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
          {/* Top Left: Việc cần làm */}
          <TaskListCard initialTasks={mockDashboardTasks} />

          {/* Top Right: Thông báo mới */}
          <NotificationCard notifications={mockDashboardNotifications} />

          {/* Bottom Left: Buổi học sắp tới */}
          <UpcomingClassesCard classes={mockUpcomingClasses} />

          {/* Bottom Right: Tài liệu mới */}
          <ResourceListCard resources={mockResources} />
        </div>
      </div>
    </DashboardLayout>
  )
}
