const API_BASE_URL = 'http://127.0.0.1:8001'

/**
 * Helper to handle fetch responses and extract error details
 */
async function handleResponse(response, defaultErrorMessage) {
  if (!response.ok) {
    let errorDetail = defaultErrorMessage
    try {
      const errorJson = await response.json()
      if (errorJson && errorJson.detail) {
        errorDetail = errorJson.detail
      }
    } catch {
      // response wasn't JSON
    }
    throw new Error(errorDetail)
  }
  return response.json()
}

export async function checkBackendHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/health`)
    return res.ok
  } catch {
    return false
  }
}

export async function getScholarships() {
  const response = await fetch(`${API_BASE_URL}/api/scholarships`)
  return handleResponse(response, 'Failed to fetch scholarship schemes.')
}

export async function createSession(studentName, scholarshipId = 'merit-cum-means') {
  const response = await fetch(`${API_BASE_URL}/api/sessions/create`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      student_name: studentName.trim(),
      scholarship_id: scholarshipId,
    }),
  })
  return handleResponse(response, 'Could not create verification session.')
}

export async function getSession(sessionId) {
  const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}`)
  return handleResponse(response, `Could not retrieve session ${sessionId}.`)
}

export async function uploadSingleDocument(sessionId, file) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(
    `${API_BASE_URL}/api/sessions/${sessionId}/documents/upload`,
    {
      method: 'POST',
      body: formData,
    }
  )
  return handleResponse(response, `Upload failed for ${file.name}.`)
}

export async function resolveDiscrepancy(sessionId, discrepancyId, resolutionNote) {
  const response = await fetch(
    `${API_BASE_URL}/api/sessions/${sessionId}/discrepancies/${discrepancyId}/resolve`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        resolution_note: resolutionNote.trim(),
      }),
    }
  )
  return handleResponse(response, 'Could not resolve discrepancy.')
}
