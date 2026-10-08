export function formatApiError(body: unknown): string {
  if (!body || typeof body !== 'object') return 'Request failed.'
  const detail = (body as { detail?: unknown }).detail
  if (detail && typeof detail === 'object' && !Array.isArray(detail) && 'reason' in detail) {
    const reason = String((detail as { reason: unknown }).reason)
    const remaining = (detail as { remaining_seconds?: number | null }).remaining_seconds
    if (remaining !== null && remaining !== undefined) {
      return `${reason} Remaining seconds: ${remaining}.`
    }
    return reason
  }
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (item && typeof item === 'object' && 'msg' in item) return String(item.msg)
        return 'Invalid input.'
      })
      .join(' ')
  }
  return 'Request failed.'
}

export class ApiError extends Error {
  status: number
  body: unknown

  constructor(status: number, body: unknown) {
    super(formatApiError(body))
    this.status = status
    this.body = body
  }
}
