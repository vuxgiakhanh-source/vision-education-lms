import {
    createExamDraft,
    deleteExamDraft,
    draftErrorStatus,
    emptyExamDraft,
    type ExamDraftFields,
} from './draftService'

export type PendingExamDraft = {
    key: string
    examId: number | null
    version: number | null
    fields: ExamDraftFields
    base?: ExamDraftFields
    writer?: string
}

function prefix(teacherId: number) {
    return `vision:exam-draft:v1:${teacherId}:`
}

function storageName(teacherId: number, draft: Pick<PendingExamDraft, 'key' | 'writer'>) {
    return prefix(teacherId) + draft.key + (draft.writer ? ':' + draft.writer : '')
}

export function readPendingDrafts(teacherId: number): PendingExamDraft[] {
    const entries: PendingExamDraft[] = []
    try {
        for (const name of Object.keys(localStorage)) {
            if (!name.startsWith(prefix(teacherId))) continue
            const json = localStorage.getItem(name)
            if (!json) continue
            try {
                const entry = JSON.parse(json) as PendingExamDraft | null
                if (entry?.fields && storageName(teacherId, entry) === name) entries.push(entry)
            } catch {
                // Một bản ghi lỗi không ảnh hưởng tới các bản nháp khác.
            }
        }
    } catch {
        // Trình duyệt có thể chặn bộ nhớ; API vẫn tự lưu khi kết nối còn hoạt động.
    }
    return entries
}

export function writePendingDraft(teacherId: number, draft: PendingExamDraft): boolean {
    try {
        localStorage.setItem(storageName(teacherId, draft), JSON.stringify(draft))
        return true
    } catch {
        return false
    }
}

export function clearPendingDraft(teacherId: number, draft: PendingExamDraft): void {
    try {
        const name = storageName(teacherId, draft)
        if (localStorage.getItem(name) === JSON.stringify(draft)) localStorage.removeItem(name)
    } catch {
        // Các trình duyệt có thể giới hạn quyền truy cập localStorage.
    }
}

export function clearDraftEdits(teacherId: number, key: string): void {
    for (const draft of readPendingDrafts(teacherId)) {
        if (draft.key === key) clearPendingDraft(teacherId, draft)
    }
}

function deletionPrefix(teacherId: number) {
    return `vision:exam-draft-deleted:v1:${teacherId}:`
}

const syncingDeletions = new Set<number>()

function creationRequestName(teacherId: number, key: string) {
    return `vision:exam-draft-creating:v1:${teacherId}:${key}`
}

export function markDraftCreationRequested(teacherId: number, key: string): void {
    try {
        localStorage.setItem(creationRequestName(teacherId, key), '1')
    } catch {
        // The active editor still tracks its request if storage is unavailable.
    }
}

export function wasDraftCreationRequested(teacherId: number, key: string): boolean {
    try {
        return localStorage.getItem(creationRequestName(teacherId, key)) === '1'
    } catch {
        return true
    }
}

export function isLocalDraftDeleted(teacherId: number, key: string): boolean {
    try {
        return localStorage.getItem(deletionPrefix(teacherId) + key) !== null
    } catch {
        return false
    }
}

export function markLocalDraftDeleted(
    teacherId: number,
    key: string,
    needsServerCleanup: boolean,
): boolean {
    try {
        localStorage.setItem(deletionPrefix(teacherId) + key, needsServerCleanup ? 'pending' : 'deleted')
        return true
    } catch {
        return false
    }
}

export async function syncDraftDeletions(teacherId: number): Promise<void> {
    if (!navigator.onLine || syncingDeletions.has(teacherId)) return
    syncingDeletions.add(teacherId)
    const prefix = deletionPrefix(teacherId)
    try {
        const token = localStorage.getItem('access_token')
        for (const name of Object.keys(localStorage)) {
            if (!name.startsWith(prefix) || localStorage.getItem(name) !== 'pending') continue
            if (!token || token !== localStorage.getItem('access_token')) return
            const key = name.slice(prefix.length)
            try {
                // An unanswered create might still be committed. Reuse its key, then keep the
                // server's deletion marker so a later repeat cannot recreate this draft.
                const id = await createExamDraft(emptyExamDraft, key)
                if (token !== localStorage.getItem('access_token')) return
                await deleteExamDraft(id)
            } catch (error) {
                const status = draftErrorStatus(error)
                if (status !== 404 && status !== 410) continue
            }
            markLocalDraftDeleted(teacherId, key, false)
            localStorage.removeItem(creationRequestName(teacherId, key))
        }
    } catch {
        // Pending deletions can be retried on the next visit or network reconnect.
    } finally {
        syncingDeletions.delete(teacherId)
    }
}
