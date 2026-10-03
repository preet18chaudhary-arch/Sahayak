import { useState } from 'react'
import { formatDocumentType, formatFieldName } from '../utils/formatters'

export function DiscrepancySection({ discrepancies, onResolveDiscrepancy, resolvingId, matchingThresholds }) {
  const [notes, setNotes] = useState({})
  const [errorMsg, setErrorMsg] = useState({})

  if (!discrepancies || discrepancies.length === 0) {
    return null
  }

  const reviewThreshold = matchingThresholds?.human_review_threshold ?? 0.80

  const handleNoteChange = (id, val) => {
    setNotes((prev) => ({ ...prev, [id]: val }))
    if (errorMsg[id]) {
      setErrorMsg((prev) => ({ ...prev, [id]: null }))
    }
  }

  const handleQuickChipClick = (id, text) => {
    setNotes((prev) => ({ ...prev, [id]: text }))
  }

  const handleResolveClick = async (discrepancyId) => {
    const note = (notes[discrepancyId] || '').trim()
    if (!note) {
      setErrorMsg((prev) => ({
        ...prev,
        [discrepancyId]: 'Please provide a resolution note or confirmation reason.',
      }))
      return
    }

    const success = await onResolveDiscrepancy(discrepancyId, note)
    if (success) {
      setNotes((prev) => {
        const updated = { ...prev }
        delete updated[discrepancyId]
        return updated
      })
    }
  }

  const unresolvedCount = discrepancies.filter((d) => !d.resolved).length

  return (
    <section className="dashboard-card discrepancy-section-card" id="discrepancies">
      <div className="section-card-header">
        <div>
          <h3 className="section-title-warning">
            Detected Discrepancies & Consistency Issues ({discrepancies.length})
          </h3>
          <p className="section-card-subtitle">
            {unresolvedCount > 0
              ? `${unresolvedCount} item(s) require human review or correction before submission.`
              : 'All flagged discrepancies have been reviewed and resolved.'}
          </p>
        </div>
        <span className={`status-pill ${unresolvedCount > 0 ? 'pill-warning' : 'pill-success'}`}>
          {unresolvedCount > 0 ? `${unresolvedCount} Needs Attention` : 'All Resolved'}
        </span>
      </div>

      <div className="discrepancies-list">
        {discrepancies.map((item) => {
          const isResolving = resolvingId === item.id
          const similarityScore = item.similarity_score || 0
          const similarityPct = Math.round(similarityScore * 100)

          // Distinguish Minor Spelling Variation vs Hard Mismatch
          const isMinorVariation = similarityScore >= reviewThreshold && similarityScore < 0.98

          return (
            <div
              key={item.id}
              className={`discrepancy-card ${item.resolved ? 'resolved' : isMinorVariation ? 'minor-variation' : 'hard-mismatch'}`}
            >
              <div className="discrepancy-header-row">
                <div className="discrepancy-title">
                  <span className="discrepancy-icon">
                    {item.resolved ? '✓' : isMinorVariation ? '⚠️' : '🚨'}
                  </span>
                  <div>
                    <strong>{formatFieldName(item.field_name)} Discrepancy</strong>
                    <span className="discrepancy-sub-type">
                      {item.resolved
                        ? 'Resolved via Human Review'
                        : isMinorVariation
                        ? 'Minor Spelling Variation (Review Required)'
                        : 'Hard Mismatch (Action Required)'}
                    </span>
                  </div>
                </div>

                <div className="discrepancy-badges">
                  {/* Similarity Badge */}
                  <span
                    className={`similarity-badge ${isMinorVariation ? 'sim-yellow' : 'sim-red'}`}
                    title="Computed Similarity Match Score"
                  >
                    {similarityPct}% Similarity
                  </span>

                  {/* Classification Pill */}
                  <span
                    className={`discrepancy-type-pill ${
                      item.resolved
                        ? 'type-resolved'
                        : isMinorVariation
                        ? 'type-minor'
                        : 'type-hard'
                    }`}
                  >
                    {item.resolved
                      ? 'Resolved'
                      : isMinorVariation
                      ? 'Minor Typo'
                      : 'Critical Mismatch'}
                  </span>
                </div>
              </div>

              {/* Side by side comparison */}
              <div className="comparison-grid">
                <div className="comparison-card">
                  <span className="comparison-doc-label">
                    Document A: {formatDocumentType(item.doc_a_type)}
                  </span>
                  <span className="comparison-value">{item.value_a}</span>
                </div>

                <div className="comparison-vs">vs</div>

                <div className="comparison-card">
                  <span className="comparison-doc-label">
                    Document B: {formatDocumentType(item.doc_b_type)}
                  </span>
                  <span className={`comparison-value ${isMinorVariation ? 'highlight-minor' : 'highlight-value'}`}>
                    {item.value_b}
                  </span>
                </div>
              </div>

              {/* Explanation Callout */}
              <div className="explanation-callout">
                <div className="callout-icon">💡</div>
                <div className="callout-text">
                  <strong>Verification Engine Explanation:</strong>
                  <p>{item.explanation}</p>
                </div>
              </div>

              {/* Resolution Form or Confirmation Note */}
              {item.resolved ? (
                <div className="resolution-confirmed-box">
                  <span className="check-icon">✓</span>
                  <div>
                    <strong>Confirmed by Human Reviewer:</strong>
                    <p>{item.resolution_note || 'Verified as valid variant.'}</p>
                  </div>
                </div>
              ) : (
                <div className="resolution-action-box">
                  <label htmlFor={`res-note-${item.id}`}>
                    Human-in-the-Loop Resolution & Confirmation:
                  </label>
                  <p className="resolution-help-text">
                    {isMinorVariation
                      ? 'If this is a minor spelling variant representing the same student, confirm with a note below.'
                      : 'If this value is incorrect, replace the conflicting document or provide official verification notes.'}
                  </p>

                  <div className="quick-chips-row">
                    <span className="chips-label">Quick Suggestions:</span>
                    <button
                      type="button"
                      className="chip-btn"
                      onClick={() =>
                        handleQuickChipClick(
                          item.id,
                          'Minor spelling variation, confirmed referring to the same student'
                        )
                      }
                    >
                      Minor Typo Confirmed
                    </button>
                    <button
                      type="button"
                      className="chip-btn"
                      onClick={() =>
                        handleQuickChipClick(
                          item.id,
                          'Aadhaar card spelling is canonical for this application'
                        )
                      }
                    >
                      Aadhaar Canonical
                    </button>
                    <button
                      type="button"
                      className="chip-btn"
                      onClick={() =>
                        handleQuickChipClick(
                          item.id,
                          'Supported by official gazette / school certificate'
                        )
                      }
                    >
                      Official Proof Verified
                    </button>
                  </div>

                  <div className="resolution-input-row">
                    <input
                      id={`res-note-${item.id}`}
                      type="text"
                      placeholder="Enter resolution note (e.g. Verified typo with student; Aadhaar is canonical)..."
                      value={notes[item.id] || ''}
                      onChange={(e) => handleNoteChange(item.id, e.target.value)}
                      disabled={isResolving}
                    />

                    <button
                      className="primary-button resolve-btn"
                      type="button"
                      onClick={() => handleResolveClick(item.id)}
                      disabled={isResolving}
                    >
                      {isResolving ? 'Resolving...' : 'Confirm & Resolve'}
                    </button>
                  </div>

                  {errorMsg[item.id] && (
                    <p className="error-message">{errorMsg[item.id]}</p>
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </section>
  )
}
