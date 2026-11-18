import type { ReactNode } from 'react'
import { AuthGuard } from '../../features/auth/guards/AuthGuard'

export default function StudentLayout({ children }: { children: ReactNode }) {
  return <AuthGuard>{children}</AuthGuard>
}
