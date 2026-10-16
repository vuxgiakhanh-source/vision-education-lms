import React from 'react'
import { Calendar, ArrowRight, ArrowUpRight } from 'lucide-react'
import type { TaskItem } from '../types/dashboard.types'

interface TaskListCardProps {
  tasks: TaskItem[]
  onOpenTask?: (task: TaskItem) => void
}

export const TaskListCard: React.FC<TaskListCardProps> = ({ tasks, onOpenTask }) => {
  const getTagClasses = (statusType: TaskItem['statusType']) => {
    switch (statusType) {
      case 'urgent':
        return 'bg-[#FEF2F2] text-[#EF4444]'
      case 'due':
        return 'bg-[#FFF7ED] text-[#EA580C]'
      default:
        return 'bg-[#F1F5F9] text-[#64748B]'
    }
  }

  const getIndicatorColor = (statusType: TaskItem['statusType']) => {
    switch (statusType) {
      case 'urgent':
        return 'bg-[#F87171]'
      case 'due':
        return 'bg-[#FB923C]'
      default:
        return 'bg-slate-200'
    }
  }

  return (
    <section className="flex flex-col gap-3.5 ultrawide:gap-5 min-w-0">
      <div className="flex items-center justify-between px-1 ultrawide:min-h-8">
        <h2 className="text-[18px] wide:text-[22px] ultrawide:text-[24px] font-bold text-[#1E293B] tracking-tight">
          Việc cần làm
        </h2>
        <button type="button" className="text-[11px] wide:text-[13px] font-semibold text-[#5553E6] hover:text-[#4338CA] flex items-center gap-1.5 cursor-pointer">
          <span>Xem tất cả</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      <div className="bg-white rounded-[20px] shadow-[0_3px_16px_rgba(30,41,59,0.02)] border border-[#EAEFF5] divide-y divide-[#F1F5F9] overflow-hidden">
        {tasks.map((task) => (
          <div
            key={task.id}
            className={`grid grid-cols-[minmax(0,1fr)_auto] sm:grid-cols-[minmax(0,1fr)_116px_104px_72px] wide:grid-cols-[minmax(0,1fr)_136px_112px_96px] items-center gap-x-3 gap-y-3 min-h-[72px] px-4 sm:px-5 py-3.5 wide:min-h-[84px] wide:px-6 wide:py-[18px] wide:gap-x-[18px] ultrawide:min-h-28 ultrawide:px-7 ultrawide:py-6 hover:bg-slate-50/60 transition-colors ${task.isCompleted ? 'opacity-50' : ''}`}
          >
            <div className="col-span-2 sm:col-span-1 flex items-center gap-3.5 min-w-0">
              <span className={`w-[3px] h-7 rounded-full shrink-0 ${getIndicatorColor(task.statusType)}`} />
              <div className="min-w-0">
                <h3 className={`text-[13px] sm:text-[14px] wide:text-[16px] ultrawide:text-[18px] wide:leading-normal font-semibold text-[#1E293B] leading-relaxed break-words ${task.isCompleted ? 'line-through' : ''}`}>
                  {task.title}
                </h3>
                <p className="text-[12px] wide:text-[13px] ultrawide:text-[14px] text-slate-500 mt-1 leading-relaxed break-words">{task.subjectTopic}</p>
              </div>
            </div>

            <div className="flex items-center gap-1.5 text-[11.5px] wide:text-[13px] ultrawide:text-[14px] text-slate-500 whitespace-nowrap">
              <Calendar className="w-3.5 h-3.5 text-slate-400 shrink-0" />
              <span>{task.dueDate}</span>
            </div>
            <div className="flex justify-end sm:justify-center">
              <span className={`px-2.5 py-1 rounded-full text-[10px] wide:text-[11px] font-semibold whitespace-nowrap ${getTagClasses(task.statusType)}`}>
                {task.statusLabel}
              </span>
            </div>
            <button
              type="button"
              onClick={() => onOpenTask?.(task)}
              aria-label={`${task.actionLabel || 'Xem bài'}: ${task.title}`}
              className="col-span-2 sm:col-span-1 flex items-center justify-end gap-1 min-h-9 text-[11px] wide:text-[12px] ultrawide:text-[13px] font-semibold text-[#635DC4] hover:text-[#4338CA] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#5553E6] rounded cursor-pointer whitespace-nowrap"
            >
              {task.actionLabel || 'Xem bài'}
              <ArrowUpRight className="w-3 h-3" />
            </button>
          </div>
        ))}
      </div>
    </section>
  )
}
