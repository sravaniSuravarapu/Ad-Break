import { describe, expect, it } from 'vitest'
import { formatApiError } from './errors'

describe('formatApiError', () => {
  it('shows the API reason and remaining seconds', () => {
    expect(
      formatApiError({
        detail: { reason: 'Booked seconds would exceed break capacity.', rule: 'BR-03', remaining_seconds: 20 },
      }),
    ).toBe('Booked seconds would exceed break capacity. Remaining seconds: 20.')
  })

  it('shows a plain reason when seconds are absent', () => {
    expect(formatApiError({ detail: { reason: 'Only an active campaign can be booked.', rule: 'BR-08', remaining_seconds: null } })).toBe(
      'Only an active campaign can be booked.',
    )
  })
})
