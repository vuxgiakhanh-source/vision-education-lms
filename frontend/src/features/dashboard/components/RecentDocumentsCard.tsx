import React from 'react'
import { ArrowUpRight, ArrowRight, FileText, Presentation, FileCode } from 'lucide-react'
import type { DocumentItem } from '../types/dashboard.types'

interface RecentDocumentsCardProps {
  documents: DocumentItem[]
  onOpenDocument?: (document: DocumentItem) => void
}

export const RecentDocumentsCard: React.FC<RecentDocumentsCardProps> = ({
  documents,
  onOpenDocument,
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
    <section
      className="bg-white rounded-[20px] shadow-[0_3px_16px_rgba(30,41,59,0.02)] border border-[#EAEFF5] flex flex-col min-w-0"
      style={{ padding: 'var(--doc-pad)' }}
    >
      <div className="flex items-center justify-between gap-2 pb-3">
        <h3 className="text-[14px] wide:text-[16px] font-bold text-[#1E293B]">Tài liệu mới</h3>
        <button type="button" className="text-[10px] wide:text-[12px] font-semibold text-[#5553E6] hover:text-[#4338CA] flex items-center gap-1 whitespace-nowrap cursor-pointer">
          <span>Xem tất cả</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      <div className="divide-y divide-[#F1F5F9]">
        {documents.map((doc) => (
          <button
            key={doc.id}
            type="button"
            onClick={() => onOpenDocument?.(doc)}
            className="w-full flex items-center gap-3 py-3 text-left hover:bg-slate-50/70 transition-colors group focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#5553E6] rounded cursor-pointer"
            aria-label={`Mở tài liệu: ${doc.title}`}
          >
            {getDocIcon(doc.format)}
            <div className="min-w-0 flex-1">
              <h4 className="text-[12.5px] wide:text-[14px] ultrawide:text-[15px] font-semibold text-[#1E293B] leading-relaxed break-words group-hover:text-[#5553E6] transition-colors">
                {doc.title}
              </h4>
              <p className="text-[10.5px] wide:text-[12px] ultrawide:text-[13px] text-slate-500 leading-relaxed mt-1">
                {doc.format} · {doc.size} · {doc.date}
              </p>
            </div>
            <ArrowUpRight className="w-3.5 h-3.5 text-slate-400 shrink-0" />
          </button>
        ))}
      </div>
    </section>
  )
}
