import React, { useState } from 'react'
import {
  Check,
  CalendarCheck2,
  MoreVertical,
  ArrowRight,
} from 'lucide-react'
import type { DashboardTask } from '../types/dashboard.types'

interface TaskListCardProps {
  initialTasks: DashboardTask[]
}

export const TaskListCard: React.FC<TaskListCardProps> = ({ initialTasks }) => {
  const [tasks, setTasks] = useState<DashboardTask[]>(initialTasks)

  const toggleTask = (id: string) => {
    setTasks((prev) =>
      prev.map((t) => (t.id === id ? { ...t, isCompleted: !t.isCompleted } : t))
    )
  }

  const getTagClasses = (tagColor: 'blue' | 'cyan' | 'pink') => {
    switch (tagColor) {
      case 'cyan':
        return 'bg-[#E0F7FA] text-[#00ACC1]'
      case 'pink':
        return 'bg-[#FCE4EC] text-[#D81B60]'
      case 'blue':
      default:
        return 'bg-[#EEF2FF] text-[#4F46E5]'
    }
  }

  return (
    <div className="bg-white rounded-[26px] p-5 shadow-[0_4px_24px_rgba(0,0,0,0.02)] flex flex-col justify-between select-none">
      {/* Header */}
      <div className="flex items-center justify-between pb-3">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-lg bg-[#4F46E5] text-white flex items-center justify-center shrink-0">
            <Check className="w-4 h-4" strokeWidth={3} />
          </div>
          <h2 className="text-[15px] font-bold text-slate-900">Việc cần làm</h2>
          <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-[#EEF2FF] text-[#4F46E5]">
            {tasks.length}
          </span>
        </div>
        <button
          type="button"
          className="text-xs font-semibold text-[#4F46E5] hover:text-[#4338CA] flex items-center gap-1 transition-colors"
        >
          <span>Xem tất cả</span>
          <ArrowRight className="w-3.5 h-3.5" strokeWidth={2.2} />
        </button>
      </div>

      {/* Task List Items */}
      <div className="space-y-2 pt-1">
        {tasks.map((task) => (
          <div
            key={task.id}
            className={`flex items-center justify-between py-2 px-1 rounded-2xl hover:bg-slate-50/60 transition-all ${
              task.isCompleted ? 'opacity-50' : ''
            }`}
          >
            {/* Left: Purple outlined checkbox + Title & Subtitle */}
            <div className="flex items-center gap-3 min-w-0 pr-1">
              <button
                type="button"
                onClick={() => toggleTask(task.id)}
                aria-label={`Hoàn thành ${task.title}`}
                className={`w-5 h-5 rounded-[6px] border-2 flex items-center justify-center shrink-0 transition-all ${
                  task.isCompleted
                    ? 'bg-[#5B5CE5] border-[#5B5CE5] text-white'
                    : 'border-[#5B5CE5] bg-white hover:bg-indigo-50/50'
                }`}
              >
                {task.isCompleted && <Check className="w-3.5 h-3.5" strokeWidth={3} />}
              </button>

              <div className="min-w-0">
                <p
                  className={`text-[12px] font-bold text-slate-900 whitespace-nowrap ${
                    task.isCompleted ? 'line-through text-slate-400' : ''
                  }`}
                >
                  {task.title}
                </p>
                <p className="text-[10.5px] text-slate-400 whitespace-nowrap mt-0.5">
                  {task.subjectTopic}
                </p>
              </div>
            </div>

            {/* Right: Tag, Deadline, Countdown, Menu */}
            <div className="flex items-center gap-2 shrink-0">
              {/* Category Tag */}
              <span
                className={`text-[10.5px] font-semibold px-2 py-0.5 rounded-full ${getTagClasses(
                  task.categoryTagColor
                )}`}
              >
                {task.categoryTag}
              </span>

              {/* Deadline */}
              <div className="hidden sm:flex items-center gap-1 text-[10.5px] text-slate-500">
                <CalendarCheck2 className="w-3.5 h-3.5 text-slate-400" strokeWidth={2} />
                <span>Hạn: {task.deadline}</span>
              </div>

              {/* Countdown badge */}
              <span
                className={`text-[10.5px] font-semibold px-2 py-0.5 rounded-full ${
                  task.isUrgent
                    ? 'bg-[#FEE2E2] text-[#EF4444]'
                    : 'bg-[#EEF2FF] text-[#4F46E5]'
                }`}
              >
                Còn {task.remainingDays} ngày
              </span>

              {/* Action Menu */}
              <button
                type="button"
                aria-label="Thao tác"
                className="text-slate-300 hover:text-slate-600 p-0.5"
              >
                <MoreVertical className="w-4 h-4" strokeWidth={2} />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
