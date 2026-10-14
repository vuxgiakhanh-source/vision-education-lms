import React from 'react'
import { BarChart2, FileText, Flame, ArrowUp } from 'lucide-react'
import type { KpiStats } from '../types/dashboard.types'

interface KpiStatCardsProps {
  stats: KpiStats
}

export const KpiStatCards: React.FC<KpiStatCardsProps> = ({ stats }) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5 sm:gap-4 select-none">
      {/* 1. Điểm trung bình - Icon Xanh Tím pastel */}
      <div
        className="bg-white rounded-[24px] px-4 py-3.5 xl:px-5 xl:py-4 shadow-[0_4px_20px_rgba(0,0,0,0.03)] border border-[#EDF1F8] flex items-center gap-3.5 xl:gap-4 hover:shadow-[0_8px_30px_rgba(0,0,0,0.05)] transition-all min-w-0"
        style={{ height: 'var(--kpi-h)', paddingTop: 'var(--kpi-pad-y)', paddingBottom: 'var(--kpi-pad-y)' }}
      >
        <div
          className="rounded-2xl bg-[#EEF2FF] text-[#4F46E5] flex items-center justify-center shrink-0 shadow-2xs"
          style={{ width: 'var(--kpi-icon-size)', height: 'var(--kpi-icon-size)' }}
        >
          <BarChart2 className="w-5.5 h-5.5 xl:w-[26px] xl:h-[26px]" strokeWidth={2.2} />
        </div>
        <div className="min-w-0 flex-1">
          <span className="text-[12.5px] xl:text-[13px] font-semibold text-slate-500 block leading-none mb-1.5 xl:mb-2 truncate">
            Điểm trung bình
          </span>
          <div className="flex items-center gap-2 flex-nowrap">
            <span
              className="font-black text-[#1E293B] tracking-tight leading-none whitespace-nowrap"
              style={{ fontSize: 'var(--kpi-val-size)' }}
            >
              {stats.averageScore.current}/{stats.averageScore.max}
            </span>
            <span className="inline-flex items-center gap-0.5 h-5 px-2 rounded-full text-[10.5px] xl:text-[11px] font-bold bg-[#ECFDF5] text-[#10B981] whitespace-nowrap shrink-0">
              <ArrowUp className="w-2.5 h-2.5" strokeWidth={3} />
              +{stats.averageScore.diff}
            </span>
          </div>
          <span className="text-[12px] xl:text-[12.5px] text-slate-500 font-medium block leading-none mt-1.5 xl:mt-2 truncate">
            {stats.averageScore.diffLabel || 'Cao hơn tuần trước'}
          </span>
        </div>
      </div>

      {/* 2. Chuỗi học tập - Icon Cam Đỏ (Lửa nhiệt huyết / Streak) */}
      <div
        className="bg-white rounded-[24px] px-4 py-3.5 xl:px-5 xl:py-4 shadow-[0_4px_20px_rgba(0,0,0,0.03)] border border-[#EDF1F8] flex items-center gap-3.5 xl:gap-4 hover:shadow-[0_8px_30px_rgba(0,0,0,0.05)] transition-all min-w-0"
        style={{ height: 'var(--kpi-h)', paddingTop: 'var(--kpi-pad-y)', paddingBottom: 'var(--kpi-pad-y)' }}
      >
        <div
          className="rounded-2xl bg-[#FFF4EB] text-[#F97316] flex items-center justify-center shrink-0 shadow-2xs"
          style={{ width: 'var(--kpi-icon-size)', height: 'var(--kpi-icon-size)' }}
        >
          <Flame className="w-5.5 h-5.5 xl:w-[26px] xl:h-[26px]" strokeWidth={2.2} />
        </div>
        <div className="min-w-0 flex-1">
          <span className="text-[12.5px] xl:text-[13px] font-semibold text-slate-500 block leading-none mb-1.5 xl:mb-2 truncate">
            Chuỗi học tập
          </span>
          <div className="flex items-center gap-2">
            <span
              className="font-black text-[#1E293B] tracking-tight leading-none whitespace-nowrap"
              style={{ fontSize: 'var(--kpi-val-size)' }}
            >
              {stats.streak.days} ngày
            </span>
          </div>
          <span className="text-[12px] xl:text-[12.5px] text-slate-500 font-medium block leading-none mt-1.5 xl:mt-2 truncate">
            {stats.streak.note || 'Giữ vững phong độ!'}
          </span>
        </div>
      </div>

      {/* 3. Bài tập cần nộp - Icon Xanh Lá Mint pastel */}
      <div
        className="bg-white rounded-[24px] px-4 py-3.5 xl:px-5 xl:py-4 shadow-[0_4px_20px_rgba(0,0,0,0.03)] border border-[#EDF1F8] flex items-center gap-3.5 xl:gap-4 hover:shadow-[0_8px_30px_rgba(0,0,0,0.05)] transition-all min-w-0"
        style={{ height: 'var(--kpi-h)', paddingTop: 'var(--kpi-pad-y)', paddingBottom: 'var(--kpi-pad-y)' }}
      >
        <div
          className="rounded-2xl bg-[#E6FBF5] text-[#10B981] flex items-center justify-center shrink-0 shadow-2xs"
          style={{ width: 'var(--kpi-icon-size)', height: 'var(--kpi-icon-size)' }}
        >
          <FileText className="w-5.5 h-5.5 xl:w-[26px] xl:h-[26px]" strokeWidth={2.2} />
        </div>
        <div className="min-w-0 flex-1">
          <span className="text-[12.5px] xl:text-[13px] font-semibold text-slate-500 block leading-none mb-1.5 xl:mb-2 truncate">
            Bài tập cần nộp
          </span>
          <div className="flex items-center gap-2 flex-nowrap">
            <span
              className="font-black text-[#1E293B] tracking-tight leading-none whitespace-nowrap"
              style={{ fontSize: 'var(--kpi-val-size)' }}
            >
              {stats.pendingAssignments.count} bài
            </span>
            <span className="inline-flex items-center h-5 px-2 rounded-full text-[10px] xl:text-[10.5px] font-bold bg-[#FEF2F2] text-[#EF4444] whitespace-nowrap shrink-0">
              {stats.pendingAssignments.tag}
            </span>
          </div>
          <span className="text-[12px] xl:text-[12.5px] text-slate-500 font-medium block leading-none mt-1.5 xl:mt-2 truncate">
            {stats.pendingAssignments.nearestDeadline || 'Trong 3 ngày tới'}
          </span>
        </div>
      </div>
    </div>
  )
}
