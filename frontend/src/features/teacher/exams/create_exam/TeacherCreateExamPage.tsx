'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useEffect, useRef, useState, type FormEvent } from 'react'
import {
    ArrowLeftRight,
    CalendarPlus,
    CloudUpload,
    Eye,
    FileText,
    FolderOpen,
    Layers,
    MonitorCheck,
    Pencil,
    Settings,
    Upload,
} from 'lucide-react'
import { useAuthProfile } from '../../../auth/guards/AuthGuard'
import { listExamBankChoices, type ExamBankChoice } from '../../documents/exam_bank/examBankService'
import { TeacherExamAudience } from './TeacherExamAudience'
import { TeacherExamSchedule } from './TeacherExamSchedule'
import { useExamDraft } from './useExamDraft'
import './TeacherCreateExamPage.css'

type Props = { examId: number | null; draftKey: string | null; start: boolean }

const saveMessage = {
    idle: '',
    loading: '',
    gone: '',
    loadFailed: '',
    pending: 'Đang chờ lưu…',
    saving: 'Đang lưu…',
    saved: 'Đã lưu bản nháp.',
    local: 'Đã lưu trên thiết bị này. Bản nháp chưa đồng bộ lên hệ thống.',
    error: 'Chưa lưu được. Hãy thử lưu lại trước khi rời trang.',
    conflict: 'Bản nháp đã được cập nhật ở nơi khác.',
    invalid: 'Kiểm tra lại thông tin chưa hợp lệ.',
    deleting: 'Đang xóa bản nháp…',
    deleteFailed: 'Chưa xóa được bản nháp. Hãy thử lại.',
}

const sourceOptions = [
    { value: 'upload', label: 'Tải file đề thi', Icon: Upload },
    { value: 'library', label: 'Chọn từ Kho đề & câu hỏi', Icon: Layers },
    { value: 'manual', label: 'Tạo đề mới', Icon: Pencil },
] as const

export function TeacherCreateExamPage(props: Props) {
    const profile = useAuthProfile()
    if (!profile) return null
    return (
        <TeacherExamDraftEditor
            key={`${props.examId ?? ''}:${props.draftKey ?? ''}`}
            {...props}
            teacherId={profile.id}
        />
    )
}

function TeacherExamDraftEditor({ teacherId, examId, draftKey, start }: Props & { teacherId: number }) {
    const router = useRouter()
    const draft = useExamDraft(teacherId, examId, draftKey, start)
    const { status, flush } = draft

    return (
        <main className="teacher-reference-main">
            <div id="teacher-exams-view">
                <div className="exam-wizard" id="exam-wizard">
                    <header className="teacher-page-heading detail-id">
                        <nav className="detail-path" aria-label="Vị trí trong Phòng thi ảo">
                            <ol>
                                <li>
                                    <Link
                                        className="teacher-page-title"
                                        href="/teacher-exams"
                                        onClick={() => {
                                            void flush()
                                        }}
                                    >
                                        <span className="teacher-page-icon">
                                            <MonitorCheck aria-hidden="true" />
                                        </span>
                                        Phòng thi ảo
                                    </Link>
                                </li>
                                <li aria-current="page">
                                    <span className="detail-separator" aria-hidden="true" />
                                    <h1 id="exam-event-dialog-title" tabIndex={-1}>
                                        Tạo kỳ thi
                                    </h1>
                                </li>
                            </ol>
                        </nav>
                    </header>
                    {status === 'loading' ? (
                        <p role="status">Đang mở bản nháp…</p>
                    ) : status === 'gone' || status === 'loadFailed' ? (
                        <p role="alert">
                            {status === 'gone'
                                ? 'Kỳ thi nháp này không còn trong danh sách.'
                                : 'Chưa mở được kỳ thi nháp. Hãy tải lại trang.'}
                        </p>
                    ) : (
                        <TeacherExamWizard
                            draft={draft}
                            onDiscard={async () => {
                                if (window.confirm('Xóa bản nháp này?') && (await draft.discard()))
                                    router.replace('/teacher-exams')
                            }}
                        />
                    )}
                </div>
            </div>
        </main>
    )
}

function TeacherExamWizard({
    draft,
    onDiscard,
}: {
    draft: ReturnType<typeof useExamDraft>
    onDiscard: () => Promise<void>
}) {
    const { fields, status, message, hasDraft, edit, flush, retry, resolveConflict } = draft
    const [source, setSource] = useState<(typeof sourceOptions)[number]['value']>(
        fields.paper_id ? 'library' : 'upload',
    )
    const [sourceNotice, setSourceNotice] = useState('')
    const [submitted, setSubmitted] = useState(false)
    const [papers, setPapers] = useState<ExamBankChoice[] | 'loading' | 'failed'>('loading')
    const [paperToPick, setPaperToPick] = useState<number | null>(null)
    const picker = useRef<HTMLDialogElement>(null)
    const selectedPaper = Array.isArray(papers)
        ? papers.find((paper) => paper.paper_id === fields.paper_id)
        : undefined
    const fallbackPaperTitle = fields.paper_id ? `Đề đã chọn (${fields.paper_id})` : 'Chưa chọn đề'
    const paperTitle = selectedPaper?.title ?? fallbackPaperTitle
    const description = fields.description ?? ''
    const canRetry = status === 'local' || status === 'error'

    useEffect(() => {
        const controller = new AbortController()
        listExamBankChoices(controller.signal)
            .then(setPapers)
            .catch(() => {
                if (!controller.signal.aborted) setPapers('failed')
            })
        return () => controller.abort()
    }, [])

    function openPicker() {
        setPaperToPick(fields.paper_id)
        picker.current?.showModal()
    }

    function submit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault()
        setSubmitted(true)
        if (!hasDraft) edit('title', fields.title)
        void flush()
    }

    return (
        <form
            id="exam-event-form"
            className="exam-wizard-form"
            noValidate
            onSubmit={submit}
            inert={status === 'deleting'}
        >
            <div className="exam-wizard-layout">
                <div className="exam-create-sections">
                    <section className="exam-card exam-fields" aria-labelledby="exam-event-info-title">
                        <header className="exam-card-head">
                            <h2 id="exam-event-info-title">
                                <FileText aria-hidden="true" />
                                Thông tin kỳ thi
                            </h2>
                        </header>
                        <label>
                            <span>
                                Tên kỳ thi{' '}
                                <span className="exam-required" aria-hidden="true">
                                    *
                                </span>
                            </span>
                            <input
                                name="title"
                                required
                                maxLength={100}
                                placeholder="Ví dụ: Kiểm tra chương Đạo hàm – Khối 12"
                                value={fields.title ?? ''}
                                onChange={(event) => edit('title', event.target.value)}
                            />
                        </label>
                        <div className="exam-wizard-desc">
                            <label htmlFor="exam-event-description">Mô tả (tùy chọn)</label>
                            <textarea
                                id="exam-event-description"
                                name="description"
                                rows={2}
                                maxLength={200}
                                placeholder="Nhập nội dung, phạm vi kiến thức hoặc lưu ý cho học sinh…"
                                value={description}
                                onChange={(event) => edit('description', event.target.value)}
                            />
                            <output id="exam-event-description-count" htmlFor="exam-event-description">
                                {description.length} / 200
                            </output>
                        </div>
                        <fieldset className="exam-source-fieldset">
                            <legend>
                                Nguồn đề thi{' '}
                                <span className="exam-required" aria-hidden="true">
                                    *
                                </span>
                            </legend>
                            <div className="exam-source-options">
                                {sourceOptions.map(({ value, label, Icon }) => (
                                    <label key={value}>
                                        <input
                                            type="radio"
                                            name="source"
                                            value={value}
                                            checked={source === value}
                                            onChange={() => {
                                                setSource(value)
                                                setSourceNotice('')
                                            }}
                                        />
                                        <Icon aria-hidden="true" />
                                        {label}
                                    </label>
                                ))}
                            </div>
                            <div
                                className="exam-upload-panel"
                                data-source-panel="upload"
                                hidden={source !== 'upload'}
                            >
                                <div
                                    className="exam-dropzone"
                                    id="exam-event-dropzone"
                                    onDragOver={(event) => event.preventDefault()}
                                    onDrop={(event) => {
                                        event.preventDefault()
                                        setSourceNotice('Nhập tệp đề thi thuộc Kho đề & câu hỏi.')
                                    }}
                                >
                                    <CloudUpload aria-hidden="true" />
                                    <div>
                                        <strong>Kéo thả tệp đề thi</strong>
                                        <p>PDF, JPG, PNG, DOCX, XLSX · tối đa 50 MB</p>
                                    </div>
                                    <button
                                        className="exam-button"
                                        id="exam-event-file-choose"
                                        type="button"
                                        onClick={() =>
                                            setSourceNotice('Nhập tệp đề thi thuộc Kho đề & câu hỏi.')
                                        }
                                    >
                                        <FolderOpen aria-hidden="true" />
                                        Chọn tệp
                                    </button>
                                </div>
                            </div>
                            <div data-source-panel="library" hidden={source !== 'library'}>
                                <div className="exam-wizard-paper">
                                    <div className="exam-wizard-paper-copy">
                                        <span className="exam-icon">
                                            <FileText aria-hidden="true" />
                                        </span>
                                        <div>
                                            <strong id="exam-event-paper-title">{paperTitle}</strong>
                                            <p>
                                                {fields.paper_id
                                                    ? 'Đề trong Kho đề & câu hỏi'
                                                    : 'Chọn một đề từ kho đề.'}
                                            </p>
                                        </div>
                                    </div>
                                    <div className="exam-wizard-paper-actions">
                                        <button
                                            className="exam-button"
                                            type="button"
                                            disabled={!fields.paper_id}
                                            onClick={() =>
                                                setSourceNotice(
                                                    'Màn xem trước nội dung đề chưa được nối.',
                                                )
                                            }
                                        >
                                            <Eye aria-hidden="true" />
                                            Xem trước
                                        </button>
                                        <button
                                            className="exam-button"
                                            type="button"
                                            onClick={openPicker}
                                        >
                                            <ArrowLeftRight aria-hidden="true" />
                                            Đổi đề
                                        </button>
                                    </div>
                                </div>
                            </div>
                            <div
                                className="exam-fields"
                                data-source-panel="manual"
                                hidden={source !== 'manual'}
                            >
                                <label>
                                    Tên đề mới
                                    <input
                                        name="manualPaperTitle"
                                        maxLength={100}
                                        placeholder="Dùng tên kỳ thi nếu để trống"
                                        readOnly
                                    />
                                </label>
                                <label>
                                    Số câu dự kiến
                                    <input
                                        name="manualQuestions"
                                        type="number"
                                        min={0}
                                        defaultValue={0}
                                        readOnly
                                    />
                                </label>
                                <p className="exam-wizard-selection">
                                    Tạo đề mới trong Kho đề &amp; câu hỏi.
                                </p>
                            </div>
                            {sourceNotice && (
                                <p className="exam-wizard-selection" role="status">
                                    {sourceNotice}
                                </p>
                            )}
                        </fieldset>
                    </section>
                    <TeacherExamAudience />
                </div>
                <div className="exam-create-sections">
                    <section
                        className="exam-card exam-fields exam-wizard-config"
                        aria-labelledby="exam-config-title"
                        aria-describedby="exam-config-draft-note"
                    >
                        <header className="exam-card-head">
                            <h2 id="exam-config-title">
                                <Settings aria-hidden="true" />
                                Cấu hình kỳ thi
                            </h2>
                        </header>
                        <p id="exam-config-draft-note">Cấu hình này chưa được lưu trong bản nháp.</p>
                        <div>
                            <label className="exam-switch-row">
                                Tự động nộp khi hết giờ{' '}
                                <input
                                    className="exam-switch"
                                    type="checkbox"
                                    role="switch"
                                    name="autoSubmit"
                                    disabled
                                    defaultChecked
                                />
                            </label>
                            <label className="exam-switch-row">
                                Cho phép vào trước 10 phút{' '}
                                <input
                                    className="exam-switch"
                                    type="checkbox"
                                    role="switch"
                                    name="earlyEntry"
                                    disabled
                                    defaultChecked
                                />
                            </label>
                            <label className="exam-switch-row">
                                Hiển thị kết quả sau khi kết thúc{' '}
                                <input
                                    className="exam-switch"
                                    type="checkbox"
                                    role="switch"
                                    name="showResults"
                                    disabled
                                    defaultChecked
                                />
                            </label>
                        </div>
                        <label className="exam-library-saving">
                            <input type="checkbox" name="keepInLibrary" defaultChecked disabled />
                            Lưu đề vào Kho đề &amp; câu hỏi sau khi kỳ thi kết thúc
                        </label>
                    </section>
                    <TeacherExamSchedule fields={fields} edit={edit} />
                </div>
            </div>
            <footer className="exam-wizard-footer">
                <div className="exam-save-feedback">
                    <p role="status">
                        {submitted && (status === 'saved' || status === 'idle')
                            ? 'Đã lưu bản nháp. Kỳ thi chưa được mở.'
                            : status === 'conflict' || status === 'invalid'
                              ? message || saveMessage[status]
                              : saveMessage[status]}
                    </p>
                </div>
                {canRetry && (
                    <button
                        className="exam-button"
                        type="button"
                        onClick={() => {
                            void retry()
                        }}
                    >
                        Thử lưu lại
                    </button>
                )}
                {status === 'conflict' && (
                    <>
                        <button
                            className="exam-button"
                            type="button"
                            onClick={() => {
                                void resolveConflict('server')
                            }}
                        >
                            Dùng giá trị đã lưu
                        </button>
                        <button
                            className="exam-button"
                            type="button"
                            onClick={() => {
                                void resolveConflict('local')
                            }}
                        >
                            Giữ thay đổi của tôi
                        </button>
                    </>
                )}
                {hasDraft && (
                    <button
                        className="exam-button exam-draft-delete"
                        type="button"
                        onClick={() => {
                            void onDiscard()
                        }}
                    >
                        Xóa bản nháp
                    </button>
                )}
                <Link
                    className="exam-button"
                    href="/teacher-exams"
                    onClick={() => {
                        void flush()
                    }}
                >
                    Hủy
                </Link>
                <button className="exam-button exam-primary" type="submit">
                    <CalendarPlus aria-hidden="true" />
                    Tạo kỳ thi
                </button>
            </footer>
            <dialog
                className="exam-card exam-fields exam-paper-picker"
                ref={picker}
                aria-labelledby="exam-paper-picker-title"
            >
                <header className="exam-card-head">
                    <h2 id="exam-paper-picker-title">
                        <Layers aria-hidden="true" />
                        Chọn đề từ Kho đề
                    </h2>
                </header>
                <label>
                    Đề trong kho
                    <select
                        value={paperToPick ?? ''}
                        disabled={!Array.isArray(papers)}
                        onChange={(event) =>
                            setPaperToPick(event.target.value ? Number(event.target.value) : null)
                        }
                    >
                        <option value="">
                            {papers === 'loading'
                                ? 'Đang tải Kho đề…'
                                : papers === 'failed'
                                  ? 'Chưa tải được Kho đề'
                                  : 'Chọn đề đã lưu'}
                        </option>
                        {paperToPick !== null &&
                            (!Array.isArray(papers) ||
                                !papers.some((paper) => paper.paper_id === paperToPick)) && (
                                <option value={paperToPick}>Đề đã chọn ({paperToPick})</option>
                            )}
                        {Array.isArray(papers) &&
                            papers.map((paper) => (
                                <option value={paper.paper_id} key={paper.paper_id}>
                                    {paper.title}
                                </option>
                            ))}
                    </select>
                </label>
                <div className="exam-paper-picker-actions">
                    <button
                        type="button"
                        className="exam-button"
                        onClick={() => picker.current?.close()}
                    >
                        Hủy
                    </button>
                    <button
                        type="button"
                        className="exam-button exam-primary"
                        disabled={!Array.isArray(papers)}
                        onClick={() => {
                            edit('paper_id', paperToPick)
                            setSourceNotice('')
                            picker.current?.close()
                        }}
                    >
                        Dùng đề này
                    </button>
                </div>
            </dialog>
        </form>
    )
}
