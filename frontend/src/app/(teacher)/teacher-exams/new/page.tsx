import { TeacherCreateExamPage } from '../../../../features/teacher/exams/create_exam/TeacherCreateExamPage'

export default async function CreateExamPage({ searchParams }: {
    searchParams: Promise<{ id?: string | string[]; draft?: string | string[]; start?: string | string[] }>
}) {
    const { id, draft, start } = await searchParams
    const parsedId = typeof id === 'string' && /^\d+$/.test(id) ? Number(id) : 0
    const examId = parsedId > 0 && parsedId <= 2_147_483_647 ? parsedId : null
    return <TeacherCreateExamPage examId={examId} draftKey={typeof draft === 'string' ? draft : null} start={start === '1'} />
}
