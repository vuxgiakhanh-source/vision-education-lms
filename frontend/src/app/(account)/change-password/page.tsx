import { ChangePasswordPage } from '../../../features/auth/change_password/pages/ChangePasswordPage'
import { AuthGuard } from '../../../features/auth/guards/AuthGuard'

export default function ChangePasswordRoute() {
  return <AuthGuard><ChangePasswordPage /></AuthGuard>
}
