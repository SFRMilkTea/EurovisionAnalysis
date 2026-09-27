export type NotificationType = 'success' | 'warning' | 'error'

const labels: Record<NotificationType, string> = {
  success: 'Готово',
  warning: 'Внимание',
  error: 'Ошибка',
}

const icons: Record<NotificationType, string> = {
  success: '✓',
  warning: '!',
  error: '×',
}

export function Notification({ type, message, onClose }: { type: NotificationType; message: string; onClose: () => void }) {
  if (!message) return null
  return <div className={`notification notification-${type}`} role={type === 'error' ? 'alert' : 'status'} aria-live={type === 'error' ? 'assertive' : 'polite'}>
    <span className="notification-icon" aria-hidden="true">{icons[type]}</span>
    <span className="notification-content"><strong>{labels[type]}</strong><span>{message}</span></span>
    <button type="button" className="notification-close" aria-label="Закрыть уведомление" onClick={onClose}>×</button>
  </div>
}
