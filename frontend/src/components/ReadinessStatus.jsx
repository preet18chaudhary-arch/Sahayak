import { formatDocumentType, formatStatusLabel, getStatusBadgeClass } from '../utils/formatters'

export function ReadinessStatus({ readiness }) {
  if (!readiness) {
    return null
  }

  const {
    overall_status,
    status_message,
    documents_checked,
    fields_extracted,
    fields_consistent,
    potential_mismatches,
    required_documents_missing = [],
  } = readiness

  const badgeClass = getStatusBadgeClass(overall_status)
  const statusLabel = formatStatusLabel(overall_status)

  return (
    <section className="dashboard-card readiness-card">
      <div className="section-card-header">
        <div>
          <h3>Verification & Readiness Summary</h3>
          <p className="section-card-subtitle">
            Live evaluation calculated by the Sahayak verification engine
          </p>
        </div>

        <span className={`status-pill ${badgeClass}`}>
          {statusLabel}
        </span>
      </div>

      {/* Metrics Row */}
      <div className="metrics-grid">
        <div className="metric-box">
          <span className="metric-number">{documents_checked}</span>
          <span className="metric-label">Documents Checked</span>
        </div>

        <div className="metric-box">
          <span className="metric-number">{fields_extracted}</span>
          <span className="metric-label">Fields Extracted</span>
        </div>

        <div className="metric-box">
          <span className="metric-number highlight-consistent">{fields_consistent}</span>
          <span className="metric-label">Fields Consistent</span>
        </div>

        <div className="metric-box">
          <span className={`metric-number ${potential_mismatches > 0 ? 'highlight-mismatch' : ''}`}>
            {potential_mismatches}
          </span>
          <span className="metric-label">Potential Mismatches</span>
        </div>

        <div className="metric-box">
          <span className={`metric-number ${required_documents_missing.length > 0 ? 'highlight-missing' : ''}`}>
            {required_documents_missing.length}
          </span>
          <span className="metric-label">Required Docs Missing</span>
        </div>
      </div>

      {/* Status Message Banner */}
      <div className={`readiness-message-banner ${badgeClass}`}>
        <div className="banner-icon">
          {overall_status === 'READY_FOR_SUBMISSION' && '🎉'}
          {overall_status === 'ACTION_REQUIRED' && '🛑'}
          {overall_status === 'IN_REVIEW' && '⏳'}
          {overall_status === 'INCOMPLETE' && '📋'}
        </div>

        <div className="banner-content">
          <strong>Status: {statusLabel}</strong>
          <p>{status_message}</p>

          {required_documents_missing.length > 0 && (
            <div className="missing-docs-tags">
              <span>Still missing:</span>
              {required_documents_missing.map((docType) => (
                <span className="missing-tag" key={docType}>
                  {formatDocumentType(docType)}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </section>
  )
}
