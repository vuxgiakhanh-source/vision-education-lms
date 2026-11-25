'use client'

import { useRouter } from 'next/navigation'
import { useEffect, useRef, useState } from 'react'
import { ArrowRight, CalendarPlus, Layers, MonitorCheck } from 'lucide-react'
import { useAuthProfile } from '../../../auth/guards/AuthGuard'
import { listExamBankChoices, type ExamBankChoice } from '../../documents/exam_bank/examBankService'
import { listExamDrafts, newExamFields, type ExamDraft } from '../drafts/draftService'
import { TeacherExamDraftPanel } from '../drafts/TeacherExamDraftPanel'
import {
    isLocalDraftDeleted,
    readPendingDrafts,
    syncDraftDeletions,
    writePendingDraft,
    type PendingExamDraft,
} from '../drafts/pendingDrafts'
import { TeacherExamTable } from './TeacherExamTable'

export function TeacherExamOverview({ preview, query }: { preview: boolean; query: string }) {
    const router = useRouter()
    const profile = useAuthProfile()
    const teacherId = profile?.id
    const [exams, setExams] = useState<ExamDraft[] | 'loading' | 'failed'>('loading')
    const [pending, setPending] = useState<PendingExamDraft[]>([])
    const [papers, setPapers] = useState<ExamBankChoice[] | 'loading' | 'failed'>('loading')
    const bankDialog = useRef<HTMLDialogElement>(null)

    useEffect(() => {
        if (!teacherId) return
        const controller = new AbortController()
        const readPending = () =>
            setPending(
                readPendingDrafts(teacherId).filter((item) => !isLocalDraftDeleted(teacherId, item.key)),
            )
        const syncDeleted = () => {
            void syncDraftDeletions(teacherId)
        }
        void Promise.resolve().then(() => {
            if (!controller.signal.aborted) readPending()
        })
        listExamDrafts(controller.signal)
            .then(setExams)
            .catch(() => {
                if (!controller.signal.aborted) setExams('failed')
            })
        window.addEventListener('storage', readPending)
        window.addEventListener('online', syncDeleted)
        syncDeleted()
        return () => {
            controller.abort()
            window.removeEventListener('storage', readPending)
            window.removeEventListener('online', syncDeleted)
        }
    }, [teacherId])

    const saved = Array.isArray(exams)
        ? exams.filter(
              (exam) =>
                  !exam.autosave_key ||
                  teacherId === undefined ||
                  !isLocalDraftDeleted(teacherId, exam.autosave_key),
          )
        : []
    const linked = (item: PendingExamDraft, exam: ExamDraft) =>
        item.examId === exam.exam_id || item.key === exam.autosave_key
    const localOnly = new Map(
        pending
            .filter((item) => !saved.some((exam) => linked(item, exam)))
            .map((item) => [item.key, item]),
    )
    const cards = [
        ...Array.from(localOnly.values(), (item) => ({
            href: `/teacher-exams/new?${item.examId !== null ? `id=${item.examId}` : `draft=${encodeURIComponent(item.key)}`}`,
            title: item.fields.title,
            pending: true,
        })),
        ...saved.map((exam) => {
            const local = pending.find((item) => linked(item, exam))
            const param =
                local?.examId === null ? `draft=${encodeURIComponent(local.key)}` : `id=${exam.exam_id}`
            return {
                href: `/teacher-exams/new?${param}`,
                title: (local?.fields ?? exam).title,
                pending: Boolean(local),
            }
        }),
    ]

    function startDraft() {
        if (teacherId === undefined) return
        const key = crypto.randomUUID()
        const fields = newExamFields()
        writePendingDraft(teacherId, { key, examId: null, version: null, fields, base: fields })
        router.push(`/teacher-exams/new?draft=${key}&start=1`)
    }

    function openBank() {
        bankDialog.current?.showModal()
        setPapers('loading')
        listExamBankChoices()
            .then(setPapers)
            .catch(() => setPapers('failed'))
    }

    return (
        <main id="exam-overview" className="room-overview teacher-reference-main">
            <header className="room-banner">
                <span className="room-banner-icon">
                    <MonitorCheck size={20} aria-hidden="true" />
                </span>
                <div>
                    <h1>Phòng thi ảo</h1>
                    <p>Tổ chức thi trực tuyến, quản lý kỳ thi và theo dõi kết quả.</p>
                </div>
            </header>
            <div className="room-actions">
                <button
                    type="button"
                    className="room-action"
                    onClick={openBank}
                    aria-labelledby="room-bank-action-title"
                    aria-describedby="room-bank-action-description"
                >
                    <span className="room-action-icon">
                        <Layers aria-hidden="true" />
                    </span>
                    <span className="room-action-copy">
                        <strong id="room-bank-action-title">Kho đề &amp; câu hỏi</strong>
                        <small id="room-bank-action-description">
                            Quản lý đề thi, ngân hàng câu hỏi và đề từ tệp.
                        </small>
                    </span>
                    <span className="room-action-arrow">
                        <ArrowRight size={18} aria-hidden="true" />
                    </span>
                </button>
                <button
                    type="button"
                    className="room-action"
                    data-tone="green"
                    onClick={startDraft}
                    aria-labelledby="room-create-action-title"
                    aria-describedby="room-create-action-description"
                >
                    <span className="room-action-icon">
                        <CalendarPlus aria-hidden="true" />
                    </span>
                    <span className="room-action-copy">
                        <strong id="room-create-action-title">Tạo kỳ thi</strong>
                        <small id="room-create-action-description">
                            Chọn đề, lớp tham gia và thiết lập thời gian thi.
                        </small>
                    </span>
                    <span className="room-action-arrow">
                        <ArrowRight size={18} aria-hidden="true" />
                    </span>
                </button>
            </div>
            <div className="room-overview-body">
                <TeacherExamTable key={query} preview={preview} initialQuery={query} />
                <TeacherExamDraftPanel cards={cards} status={Array.isArray(exams) ? 'ready' : exams} />
            </div>
            <dialog ref={bankDialog} className="room-dialog" aria-labelledby="room-bank-title">
                <h2 id="room-bank-title">Kho đề &amp; câu hỏi</h2>
                {papers === 'loading' ? (
                    <p className="mt-4" role="status">
                        Đang tải đề…
                    </p>
                ) : papers === 'failed' ? (
                    <p className="mt-4" role="status">
                        Chưa tải được Kho đề.
                    </p>
                ) : papers.length ? (
                    <ul className="mt-4 divide-y divide-slate-200">
                        {papers.map((paper) => (
                            <li className="py-3" key={paper.paper_id}>
                                {paper.title}
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p className="mt-4">Chưa có đề trong kho.</p>
                )}
                <form method="dialog" className="mt-5">
                    <button className="room-outline">Đóng</button>
                </form>
            </dialog>
        </main>
    )
}
