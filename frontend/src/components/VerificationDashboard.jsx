import { RequiredDocuments } from './RequiredDocuments'
import { DocumentUpload } from './DocumentUpload'
import { UploadedDocuments } from './UploadedDocuments'
import { ExtractedFields } from './ExtractedFields'
import { EligibilityResults } from './EligibilityResults'
import { DiscrepancySection } from './DiscrepancySection'
import { ReadinessStatus } from './ReadinessStatus'
import { FinalReadiness } from './FinalReadiness'
import { formatStatusLabel, getStatusBadgeClass } from '../utils/formatters'

export function VerificationDashboard({
  session,
  onUploadFiles,
  uploading,
  uploadProgress,
  lastUploadResult,
  uploadError,
  onResolveDiscrepancy,
  resolvingId,
  onNewSession,
}) {
  if (!session) return null

  const { student_name, session_id, rule_config, documents, extracted_fields, discrepancies, readiness } = session
  const badgeClass = getStatusBadgeClass(readiness?.overall_status)
  const statusLabel = formatStatusLabel(readiness?.overall_status)

  return (
    <div className="verification-page">
      {/* Session Hero Banner */}
      <div className="dashboard-hero-banner">
        <div className="dashboard-hero-meta">
          <p className="tagline">VERIFICATION DASHBOARD</p>
          <h1>Verification for {student_name || 'Applicant'}</h1>
          <p className="dashboard-subtitle">
            Target Scheme: <strong>{rule_config?.name}</strong>
          </p>
        </div>

        <div className="dashboard-hero-right">
          <div className="session-id-pill">
            <span className="pill-label">Session:</span>
            <span className="pill-val">{session_id}</span>
          </div>

          <div className={`readiness-status-badge ${badgeClass}`}>
            <span className="status-dot"></span>
            <strong>{statusLabel}</strong>
          </div>
        </div>
      </div>

      {/* Human-in-the-Loop Assistive Banner */}
      <div className="assistant-guiding-banner">
        <div className="assistant-icon">🤝</div>
        <div className="assistant-content">
          <strong>AI-Assisted Verification Partner</strong>
          <p>
            Sahayak checks your documents for consistency, flags spelling variations and missing records, and invites your confirmation. It assists you without making silent assumptions.
          </p>
        </div>
      </div>

      {/* Step 1: Scheme Criteria Bar */}
      {rule_config && (
        <div className="criteria-bar">
          <div className="criteria-item">
            <span className="criteria-label">Required Documents:</span>
            <strong>{rule_config.required_documents.length} Mandatory</strong>
          </div>
          {rule_config.income_ceiling && (
            <div className="criteria-item">
              <span className="criteria-label">Income Ceiling:</span>
              <strong>₹{(rule_config.income_ceiling).toLocaleString('en-IN')} / year</strong>
            </div>
          )}
          {rule_config.min_academic_percentage && (
            <div className="criteria-item">
              <span className="criteria-label">Minimum Marks:</span>
              <strong>{rule_config.min_academic_percentage}%</strong>
            </div>
          )}
          <div className="criteria-item">
            <span className="criteria-label">Fuzzy Matching:</span>
            <strong>
              {Math.round(rule_config.matching_thresholds.human_review_threshold * 100)}% Review / {Math.round(rule_config.matching_thresholds.auto_approve_threshold * 100)}% Auto
            </strong>
          </div>
        </div>
      )}

      {/* Step 2: Required Documents Checklist */}
      <RequiredDocuments
        ruleConfig={rule_config}
        uploadedDocuments={documents || []}
      />

      {/* Step 3: Document Upload Dropzone */}
      <DocumentUpload
        onUploadFiles={onUploadFiles}
        uploading={uploading}
        uploadProgress={uploadProgress}
        lastUploadResult={lastUploadResult}
        error={uploadError}
      />

      {/* Step 4: Uploaded Documents Table */}
      <UploadedDocuments documents={documents || []} />

      {/* Step 5: Extracted Fields Grid */}
      <ExtractedFields
        extractedFields={extracted_fields || []}
        documents={documents || []}
      />

      {/* Step 6: Live Scholarship Eligibility Evaluation */}
      <EligibilityResults
        ruleConfig={rule_config}
        extractedFields={extracted_fields || []}
        documents={documents || []}
      />

      {/* Step 7: Discrepancies & Human Review Section */}
      <DiscrepancySection
        discrepancies={discrepancies || []}
        onResolveDiscrepancy={onResolveDiscrepancy}
        resolvingId={resolvingId}
        matchingThresholds={rule_config?.matching_thresholds}
      />

      {/* Step 8: Readiness Scorecard & Counters */}
      <ReadinessStatus readiness={readiness} />

      {/* Step 9: Final Application Readiness Guidance & Action Items */}
      <FinalReadiness session={session} />

      {/* Bottom Actions */}
      <div className="dashboard-footer-actions">
        <button
          type="button"
          className="text-button"
          onClick={onNewSession}
        >
          ← Start New Verification Session
        </button>
      </div>
    </div>
  )
}
