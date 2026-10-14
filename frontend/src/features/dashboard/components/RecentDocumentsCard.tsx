import React from 'react'
import { MoreHorizontal, ArrowRight, FileText, Presentation, FileCode } from 'lucide-react'
import type { DocumentItem } from '../types/dashboard.types'

interface RecentDocumentsCardProps {
  documents: DocumentItem[]
}

export const RecentDocumentsCard: React.FC<RecentDocumentsCardProps> = ({
  documents,
}) => {
  const getDocIcon = (format: string) => {
    if (format === 'PDF') {
      return (
        <div
          className="rounded-xl bg-[#FEF2F2] text-[#EF4444] flex items-center justify-center shrink-0"
          style={{ width: 'var(--doc-icon-size)', height: 'var(--doc-icon-size)' }}
        >
          <FileText className="w-5 h-5" strokeWidth={2.2} />
        </div>
      )
    }
    if (format === 'PPT') {
      return (
        <div
          className="rounded-xl bg-[#FFF7ED] text-[#EA580C] flex items-center justify-center shrink-0"
          style={{ width: 'var(--doc-icon-size)', height: 'var(--doc-icon-size)' }}
        >
          <Presentation className="w-5 h-5" strokeWidth={2.2} />
        </div>
      )
    }
    return (
      <div
        className="rounded-xl bg-[#F0FDF4] text-[#16A34A] flex items-center justify-center shrink-0"
        style={{ width: 'var(--doc-icon-size)', height: 'var(--doc-icon-size)' }}
      >
        <FileCode className="w-5 h-5" strokeWidth={2.2} />
      </div>
    )
  }

  return (
    <div
      className="bg-white rounded-[24px] shadow-[0_4px_20px_rgba(0,0,0,0.03)] border border-[#EDF1F8] flex flex-col justify-between select-none overflow-hidden"
      style={{ height: 'var(--doc-h)', padding: 'var(--doc-pad)' }}
    >
      {/* Header: Tài liệu mới + Xem tất cả */}
      <div className="flex items-center justify-between pb-2 xl:pb-2.5">
        <h3 className="text-[14.5px] sm:text-[15px] xl:text-[15.5px] font-bold text-[#1E293B]">
          Tài liệu mới
        </h3>
        <button
          type="button"
          className="text-[12.5px] font-bold text-[#4F46E5] hover:text-[#4338CA] flex items-center gap-1 transition-colors cursor-pointer"
        >
          <span>Xem tất cả</span>
          <ArrowRight className="w-3.5 h-3.5" strokeWidth={2.4} />
        </button>
      </div>

      {/* Danh sách 3 tài liệu hiển thị trọn vẹn trên nền pastel mềm mại */}
      <div className="flex-1 flex flex-col justify-between py-1 divide-y divide-[#F8FAFC]">
        {documents.map((doc) => (
          <div
            key={doc.id}
            className="flex items-center justify-between gap-3 p-1 rounded-xl hover:bg-slate-50/70 transition-all group cursor-pointer"
          >
            {/* Left: Icon tài liệu trên nền pastel mềm mại + Title & Meta */}
            <div className="flex items-center gap-3 min-w-0 flex-1">
              {getDocIcon(doc.format)}

              <div className="min-w-0">
                <h4 className="text-[13.5px] sm:text-[14px] font-bold text-[#1E293B] truncate group-hover:text-[#4F46E5] transition-colors leading-tight">
                  {doc.title}
                </h4>
                <p className="text-[12px] sm:text-[12.5px] text-slate-500 truncate mt-1 font-medium">
                  {doc.format} • {doc.size} • {doc.date}
                </p>
              </div>
            </div>

            {/* Right: More menu với vùng nhấn thoải mái */}
            <button
              type="button"
              aria-label="Thao tác"
              className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors shrink-0 cursor-pointer"
            >
              <MoreHorizontal className="w-4.5 h-4.5" strokeWidth={2} />
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
