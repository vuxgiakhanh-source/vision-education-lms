import React, { useState } from 'react'
import { Calendar, MoreHorizontal, ArrowRight, Check } from 'lucide-react'
import type { TaskItem } from '../types/dashboard.types'

interface TaskListCardProps {
  initialTasks: TaskItem[]
}

export const TaskListCard: React.FC<TaskListCardProps> = ({ initialTasks }) => {
  const [tasks, setTasks] = useState<TaskItem[]>(initialTasks)

  const toggleTask = (id: string) => {
    setTasks((prev) =>
      prev.map((task) =>
        task.id === id ? { ...task, isCompleted: !task.isCompleted } : task
      )
    )
  }

  const getTagClasses = (statusType: TaskItem['statusType']) => {
    switch (statusType) {
      case 'urgent':
        return 'bg-[#FEF2F2] text-[#EF4444]'
      case 'due':
        return 'bg-[#FFF7ED] text-[#EA580C]'
      case 'pending':
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
      case 'pending':
      default:
        return 'bg-slate-200'
    }
  }

  return (
    <div className="flex-1 flex flex-col space-y-3.5 select-none min-w-0">
      {/* Tiêu đề Việc cần làm */}
      <div className="flex items-center justify-between px-1">
        <h2 className="text-[18px] sm:text-[19px] xl:text-[20px] font-bold text-[#1E293B] tracking-tight">
          Việc cần làm
        </h2>
        <button
          type="button"
          className="text-[13px] font-bold text-[#4F46E5] hover:text-[#4338CA] flex items-center gap-1 transition-colors cursor-pointer"
        >
          <span>Xem tất cả</span>
          <ArrowRight className="w-3.5 h-3.5" strokeWidth={2.4} />
        </button>
      </div>

      {/* Thẻ trắng chứa danh sách nhiệm vụ: 4 hàng chia bằng divider mảnh */}
      <div
        className="bg-white rounded-[24px] shadow-[0_4px_20px_rgba(0,0,0,0.03)] border border-[#EDF1F8] divide-y divide-[#F1F5F9] flex flex-col justify-around overflow-hidden"
        style={{ minHeight: 'var(--task-h)' }}
      >
        {tasks.map((task) => (
          <div
            key={task.id}
            className={`flex-1 flex items-center justify-between gap-2.5 sm:gap-3 px-3.5 sm:px-6 xl:px-7 hover:bg-slate-50/60 transition-colors ${
              task.isCompleted ? 'opacity-50' : ''
            }`}
            style={{ paddingTop: 'var(--task-row-py)', paddingBottom: 'var(--task-row-py)' }}
          >
            {/* Cột trái: Vạch màu chỉ thị + Checkbox + Tiêu đề & Môn học */}
            <div className="flex items-center gap-2.5 sm:gap-3.5 min-w-0 flex-1 pr-1 sm:pr-2">
              {/* Vạch màu chỉ thị trạng thái thanh lịch ở mép trái */}
              <div
                className={`w-1 h-7 rounded-full shrink-0 ${getIndicatorColor(task.statusType)}`}
              />

              <button
                type="button"
                onClick={() => toggleTask(task.id)}
                aria-label={`Đánh dấu hoàn thành ${task.title}`}
                className={`w-5 h-5 sm:w-5.5 sm:h-5.5 rounded-lg border-2 flex items-center justify-center shrink-0 transition-all cursor-pointer ${
                  task.isCompleted
                    ? 'bg-[#4F46E5] border-[#4F46E5] text-white shadow-xs'
                    : 'border-[#CBD5E1] hover:border-[#4F46E5] bg-white'
                }`}
              >
                {task.isCompleted && <Check className="w-3.5 h-3.5 text-white" strokeWidth={3.2} />}
              </button>

              <div className="min-w-0 flex-1">
                <h3
                  className={`text-[13px] sm:text-[14px] font-bold text-[#1E293B] truncate leading-tight ${
                    task.isCompleted ? 'line-through text-slate-400' : ''
                  }`}
                >
                  {task.title}
                </h3>
                <p className="text-[11.5px] sm:text-[12.5px] text-slate-500 truncate mt-0.5 font-medium">
                  {task.subjectTopic}
                </p>
              </div>
            </div>

            {/* Cột phải: Ngày đến hạn + Status Badge + Actions */}
            <div className="flex items-center gap-1.5 sm:gap-4 shrink-0">
              {/* Ngày đến hạn */}
              <div className="hidden sm:flex items-center gap-1.5 text-[12.5px] font-medium text-slate-600 w-28 sm:w-32 justify-start whitespace-nowrap shrink-0">
                <Calendar className="w-4 h-4 text-slate-400" strokeWidth={2} />
                <span>{task.dueDate}</span>
              </div>

              {/* Status Badge */}
              <div className="flex justify-center shrink-0">
                <span
                  className={`px-2.5 sm:px-3 py-0.5 sm:py-1 rounded-full text-[10px] sm:text-[11px] font-bold tracking-wide whitespace-nowrap ${getTagClasses(
                    task.statusType
                  )}`}
                >
                  {task.statusLabel}
                </span>
              </div>

              {/* Menu ... với vùng nhấn thoải mái */}
              <button
                type="button"
                aria-label="Thao tác"
                className="w-7 h-7 sm:w-8 sm:h-8 rounded-lg flex items-center justify-center text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors cursor-pointer shrink-0"
              >
                <MoreHorizontal className="w-4 h-4 sm:w-4.5 sm:h-4.5" strokeWidth={2} />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
