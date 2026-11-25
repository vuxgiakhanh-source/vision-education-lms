import { useCallback, useEffect, useRef, useState } from 'react'
import {
    createExamDraft,
    deleteExamDraft,
    draftErrorStatus,
    draftValidationMessage,
    emptyExamDraft,
    getExamDraft,
    getExamDraftByKey,
    newExamFields,
    toDraftFields,
    updateExamDraft,
    type ExamDraft,
    type ExamDraftFields,
} from '../drafts/draftService'
import { mergeDraftEdits, sameDraftFields } from '../drafts/mergeDraftEdits'
import {
    clearDraftEdits,
    clearPendingDraft,
    isLocalDraftDeleted,
    markDraftCreationRequested,
    markLocalDraftDeleted,
    readPendingDrafts,
    syncDraftDeletions,
    wasDraftCreationRequested,
    writePendingDraft,
    type PendingExamDraft,
} from '../drafts/pendingDrafts'

const saveDelayMs = 450

type SaveStatus =
    | 'loading'
    | 'idle'
    | 'pending'
    | 'saving'
    | 'saved'
    | 'local'
    | 'error'
    | 'invalid'
    | 'conflict'
    | 'gone'
    | 'loadFailed'
    | 'deleting'
    | 'deleteFailed'

type Conflict = { draft: PendingExamDraft; server: ExamDraft; fields: string[] }

async function saveEntry(draft: PendingExamDraft, known: ExamDraft | null, onId: (id: number) => void) {
    let latest = known
    const id = latest?.exam_id ?? draft.examId ?? (await createExamDraft(draft.fields, draft.key))
    onId(id)
    if (!latest && draft.version !== null) {
        try {
            return { saved: await updateExamDraft(id, draft.version, draft.fields) }
        } catch (error) {
            if (draftErrorStatus(error) !== 409) throw error
        }
    }

    while (true) {
        latest ??= await getExamDraft(id)
        const remote = toDraftFields(latest)
        const base = draft.base ?? (draft.version === latest.version ? remote : undefined)
        const { fields, conflicts } = mergeDraftEdits(base, draft.fields, remote)
        if (conflicts.length) return { conflict: { draft, server: latest, fields: conflicts } }
        if (sameDraftFields(fields, remote)) return { saved: latest }
        try {
            return { saved: await updateExamDraft(id, latest.version, fields) }
        } catch (error) {
            if (draftErrorStatus(error) !== 409) throw error
            latest = null
        }
    }
}

function sameEntry(a: PendingExamDraft, b: PendingExamDraft) {
    return a.key === b.key && a.writer === b.writer
}

export function useExamDraft(
    teacherId: number,
    examId: number | null,
    draftKey: string | null,
    start: boolean,
) {
    const [fields, setFields] = useState(emptyExamDraft)
    const [status, setStatus] = useState<SaveStatus>('loading')
    const [hasDraft, setHasDraft] = useState(false)
    const [message, setMessage] = useState('')
    const currentFields = useRef(emptyExamDraft)
    const identity = useRef({ key: draftKey, examId })
    const server = useRef<ExamDraft | null>(null)
    const own = useRef<PendingExamDraft | null>(null)
    const recovered = useRef<PendingExamDraft[]>([])
    const writer = useRef('')
    const conflict = useRef<Conflict | null>(null)
    const rejected = useRef<PendingExamDraft | null>(null)
    const inFlight = useRef<Promise<void> | null>(null)
    const timer = useRef<ReturnType<typeof setTimeout> | null>(null)
    const active = useRef(false)
    const deleting = useRef(false)
    const creationRequested = useRef(false)
    const sessionToken = useRef<string | null>(null)

    const display = useCallback((next: ExamDraftFields) => {
        currentFields.current = next
        if (active.current) setFields(next)
    }, [])

    const cancelTimer = useCallback(() => {
        if (timer.current !== null) clearTimeout(timer.current)
        timer.current = null
    }, [])

    const addStoredEdits = useCallback(() => {
        for (const entry of readPendingDrafts(teacherId)) {
            const matches =
                entry.key === identity.current.key ||
                (identity.current.examId !== null && entry.examId === identity.current.examId)
            if (
                matches &&
                entry.writer !== writer.current &&
                !recovered.current.some((item) => sameEntry(item, entry))
            ) {
                recovered.current.push(entry)
            }
        }
    }, [teacherId])

    const flush = useCallback((): Promise<void> => {
        if (inFlight.current) return inFlight.current
        if (deleting.current || sessionToken.current !== localStorage.getItem('access_token'))
            return Promise.resolve()
        cancelTimer()

        const save = async () => {
            let draft = recovered.current[0] ?? own.current
            while (draft && !deleting.current) {
                if (isLocalDraftDeleted(teacherId, draft.key)) {
                    if (active.current) setStatus('gone')
                    return
                }
                if (
                    conflict.current ||
                    rejected.current ||
                    sessionToken.current !== localStorage.getItem('access_token')
                )
                    return
                const snapshot = draft
                const hasDurableCopy = () =>
                    readPendingDrafts(teacherId).some(
                        (entry) =>
                            sameEntry(entry, snapshot) && sameDraftFields(entry.fields, snapshot.fields),
                    )
                if (!navigator.onLine) {
                    if (active.current) setStatus(hasDurableCopy() ? 'local' : 'error')
                    return
                }
                if (!server.current && draft.examId === null) {
                    creationRequested.current = true
                    markDraftCreationRequested(teacherId, draft.key)
                }
                if (active.current) setStatus('saving')
                try {
                    const result = await saveEntry(draft, server.current, (id) => {
                        identity.current.examId = id
                        if (!deleting.current && own.current && own.current.examId === null) {
                            own.current.examId = id
                            writePendingDraft(teacherId, own.current)
                        }
                    })
                    if (deleting.current || isLocalDraftDeleted(teacherId, draft.key)) return
                    if (result.conflict) {
                        conflict.current = result.conflict
                        if (active.current) {
                            setMessage(
                                'Có thay đổi ở tab khác trong: ' +
                                    result.conflict.fields.join(', ') +
                                    '.',
                            )
                            setStatus('conflict')
                        }
                        return
                    }

                    const saved = result.saved
                    server.current = saved
                    const remote = toDraftFields(saved)
                    recovered.current = recovered.current.filter((item) => item !== draft)
                    if (own.current === draft) {
                        own.current = null
                    } else if (own.current && sameEntry(own.current, draft)) {
                        const fields = mergeDraftEdits(
                            draft.fields,
                            own.current.fields,
                            remote,
                            'local',
                        ).fields
                        own.current = { ...own.current, fields, base: remote, version: saved.version }
                        writePendingDraft(teacherId, own.current)
                    }
                    clearPendingDraft(teacherId, draft)
                    const remaining = [...recovered.current, ...(own.current ? [own.current] : [])]
                    display(
                        remaining.reduce(
                            (view, entry) =>
                                mergeDraftEdits(entry.base, entry.fields, view, 'local').fields,
                            remote,
                        ),
                    )
                    if (active.current && remaining.length === 0) setStatus('saved')
                } catch (error) {
                    if (deleting.current || isLocalDraftDeleted(teacherId, draft.key)) return
                    const code = draftErrorStatus(error)
                    if (code === 410) {
                        own.current = null
                        recovered.current = []
                        clearDraftEdits(teacherId, draft.key)
                        if (active.current) setStatus('gone')
                    } else if (code === 422 || code === 404) {
                        // If an edit arrived while the request was in flight, validate that newer edit instead.
                        if (own.current && own.current !== draft && sameEntry(own.current, draft)) {
                            draft = own.current
                            continue
                        }
                        rejected.current = draft
                        if (active.current) {
                            setMessage(
                                code === 422
                                    ? draftValidationMessage(error)
                                    : 'Đề đã chọn hoặc bản nháp không còn khả dụng. Kiểm tra lại thông tin.',
                            )
                            setStatus('invalid')
                        }
                    } else if (active.current) {
                        const durable = readPendingDrafts(teacherId).some(
                            (entry) =>
                                sameEntry(entry, draft) && sameDraftFields(entry.fields, draft.fields),
                        )
                        setStatus(durable ? 'local' : 'error')
                    }
                    return
                }
                draft = recovered.current[0] ?? own.current
            }
        }

        if (!recovered.current.length && !own.current) return Promise.resolve()
        const job = save().finally(() => {
            inFlight.current = null
        })
        inFlight.current = job
        return job
    }, [cancelTimer, display, teacherId])

    useEffect(() => {
        active.current = true
        sessionToken.current = localStorage.getItem('access_token')
        writer.current ||= crypto.randomUUID()
        const controller = new AbortController()

        async function load() {
            try {
                if (draftKey && isLocalDraftDeleted(teacherId, draftKey)) {
                    setStatus('gone')
                    return
                }
                addStoredEdits()
                const first = recovered.current[0]
                if (first) {
                    identity.current = { key: first.key, examId: examId ?? first.examId }
                    addStoredEdits()
                    display(
                        recovered.current
                            .slice(1)
                            .reduce(
                                (view, entry) =>
                                    mergeDraftEdits(entry.base, entry.fields, view, 'local').fields,
                                first.fields,
                            ),
                    )
                    setHasDraft(true)
                    void flush()
                    return
                }
                let saved: ExamDraft | null = null
                if (examId !== null) saved = await getExamDraft(examId, controller.signal)
                if (examId === null && draftKey) {
                    try {
                        saved = await getExamDraftByKey(draftKey, controller.signal)
                    } catch (error) {
                        if (!start || draftErrorStatus(error) !== 404) throw error
                        const fields = newExamFields()
                        const entry = {
                            key: draftKey,
                            examId: null,
                            fields,
                            base: fields,
                            version: null,
                            writer: writer.current,
                        }
                        own.current = entry
                        writePendingDraft(teacherId, entry)
                        display(fields)
                        setHasDraft(true)
                        void flush()
                        return
                    }
                }
                if (controller.signal.aborted) return
                if (saved) {
                    if (saved.autosave_key && isLocalDraftDeleted(teacherId, saved.autosave_key)) {
                        setStatus('gone')
                        return
                    }
                    identity.current = {
                        key: saved.autosave_key ?? `id-${saved.exam_id}`,
                        examId: saved.exam_id,
                    }
                    server.current = saved
                    addStoredEdits()
                    const remote = toDraftFields(saved)
                    display(
                        recovered.current.reduce(
                            (view, entry) =>
                                mergeDraftEdits(entry.base, entry.fields, view, 'local').fields,
                            remote,
                        ),
                    )
                    setHasDraft(true)
                    setStatus('saved')
                    void flush()
                } else {
                    display(newExamFields())
                    setStatus('idle')
                }
            } catch (error) {
                if (!controller.signal.aborted) {
                    const code = draftErrorStatus(error)
                    setStatus(code === 404 || code === 410 ? 'gone' : 'loadFailed')
                }
            }
        }

        void load()
        const saveWhenHidden = () => {
            if (document.visibilityState === 'hidden') void flush()
        }
        const saveWhenOnline = () => {
            addStoredEdits()
            void flush()
        }
        document.addEventListener('visibilitychange', saveWhenHidden)
        window.addEventListener('online', saveWhenOnline)
        return () => {
            active.current = false
            controller.abort()
            document.removeEventListener('visibilitychange', saveWhenHidden)
            window.removeEventListener('online', saveWhenOnline)
            cancelTimer()
            void flush()
        }
    }, [addStoredEdits, cancelTimer, display, draftKey, examId, flush, start, teacherId])

    function edit<Key extends keyof ExamDraftFields>(name: Key, value: ExamDraftFields[Key]) {
        if (deleting.current) return
        const next = { ...currentFields.current, [name]: value }
        const current = identity.current
        if (current.key && isLocalDraftDeleted(teacherId, current.key)) {
            setStatus('gone')
            return
        }
        if (!current.key) {
            current.key = crypto.randomUUID()
            window.history.replaceState(null, '', `/teacher-exams/new?draft=${current.key}`)
        }
        const blocked = rejected.current
        const previous = own.current ?? blocked
        const entry = {
            key: current.key,
            examId: current.examId,
            version: previous?.version ?? server.current?.version ?? null,
            base: previous?.base ?? currentFields.current,
            fields: next,
            writer: writer.current,
        }
        own.current = entry
        const stored = writePendingDraft(teacherId, entry)
        if (blocked) {
            rejected.current = null
            recovered.current = recovered.current.filter((item) => item !== blocked)
            if (stored) clearPendingDraft(teacherId, blocked)
        }
        display(next)
        setHasDraft(true)
        if (conflict.current) return
        setStatus('pending')
        cancelTimer()
        timer.current = setTimeout(() => {
            void flush()
        }, saveDelayMs)
    }

    async function resolveConflict(resolution: 'local' | 'server') {
        const blocked = conflict.current
        if (!blocked) return
        const remote = toDraftFields(blocked.server)
        const latest = own.current && sameEntry(own.current, blocked.draft) ? own.current : blocked.draft
        const fields = mergeDraftEdits(latest.base, latest.fields, remote, resolution).fields
        server.current = blocked.server
        conflict.current = null
        const entry = {
            ...latest,
            fields,
            base: remote,
            examId: blocked.server.exam_id,
            version: blocked.server.version,
            writer: writer.current,
        }
        if (latest === own.current) {
            own.current = entry
        } else {
            // Replay this resolution first, then replay any newer edits made in this editor.
            entry.writer = crypto.randomUUID()
            recovered.current = recovered.current.map((item) => (item === latest ? entry : item))
        }
        if (writePendingDraft(teacherId, entry)) clearPendingDraft(teacherId, latest)
        display(
            own.current && own.current !== entry
                ? mergeDraftEdits(own.current.base, own.current.fields, fields, 'local').fields
                : fields,
        )
        await flush()
    }

    async function discard(): Promise<boolean> {
        deleting.current = true
        cancelTimer()
        setStatus('deleting')
        const current = identity.current
        if (current.key && current.examId === null) {
            const mayBeRemote =
                creationRequested.current ||
                wasDraftCreationRequested(teacherId, current.key) ||
                recovered.current.some((entry) => entry.base === undefined)
            if (markLocalDraftDeleted(teacherId, current.key, mayBeRemote)) {
                clearDraftEdits(teacherId, current.key)
                own.current = null
                recovered.current = []
                if (mayBeRemote) void syncDraftDeletions(teacherId)
                setStatus('gone')
                return true
            }
        }
        await inFlight.current
        try {
            if (current.key) {
                const id = current.examId ?? (await createExamDraft(emptyExamDraft, current.key))
                await deleteExamDraft(id)
            }
        } catch (error) {
            const code = draftErrorStatus(error)
            if (code !== 404 && code !== 410) {
                deleting.current = false
                setStatus('deleteFailed')
                return false
            }
        }
        if (current.key) clearDraftEdits(teacherId, current.key)
        own.current = null
        recovered.current = []
        return true
    }

    function retry() {
        addStoredEdits()
        return flush()
    }

    return { fields, status, message, hasDraft, edit, flush, retry, resolveConflict, discard }
}
