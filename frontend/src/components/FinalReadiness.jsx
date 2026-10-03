import { formatDocumentType, formatStatusLabel, getStatusBadgeClass } from '../utils/formatters'

export function FinalReadiness({ session }) {
  if (!session || !session.readiness) {
    return null
  }

  const { readiness, rule_config, discrepancies = [], extracted_fields = [] } = session
  const { overall_status, status_message, required_documents_missing = [] } = readiness
  const badgeClass = getStatusBadgeClass(overall_status)
  const statusLabel = formatStatusLabel(overall_status)

  // Unresolved discrepancies
  const unresolvedMismatches = discrepancies.filter((d) => !d.resolved)

  // Eligibility evaluation checks
  const incomeField = extracted_fields.find((f) => f.field_name === 'income')
  const percentageField = extracted_fields.find((f) => f.field_name === 'percentage')

  const incomeExceeded =
    rule_config?.income_ceiling &&
    incomeField &&
    !isNaN(Number(incomeField.value)) &&
    Number(incomeField.value) > rule_config.income_ceiling

  const marksBelow =
    rule_config?.min_academic_percentage &&
    percentageField &&
    !isNaN(Number(percentageField.value)) &&
    Number(percentageField.value) < rule_config.min_academic_percentage

  const isReady = overall_status === 'READY_FOR_SUBMISSION'
  const isActionRequired = overall_status === 'ACTION_REQUIRED'
  const isInReview = overall_status === 'IN_REVIEW'
  const isIncomplete = overall_status === 'INCOMPLETE'

  return (
    <section className="dashboard-card final-readiness-card" id="readiness-summary">
      <div className={`final-readiness-container ${badgeClass}`}>
        <div className="final-icon-wrapper">
          {isReady && '✅'}
          {isActionRequired && '🛑'}
          {isInReview && '⚠️'}
          {isIncomplete && '📋'}
        </div>

        <div className="final-content">
          <div className="final-header-row">
            <h4>Application Readiness: {statusLabel}</h4>
            <span className={`status-pill ${badgeClass}`}>{statusLabel}</span>
          </div>

          <p className="final-message-text">{status_message}</p>

          {/* Action Required / Incomplete / In-Review Action List */}
          {!isReady && (
            <div className="action-items-container">
              <strong className="action-items-title">
                {isActionRequired ? 'Required Action Items to Proceed:' : 'Steps to Complete Verification:'}
              </strong>

              <div className="action-items-list">
                {/* 1. Missing Documents */}
                {required_documents_missing.length > 0 && (
                  <div className="action-item-card action-item-missing">
                    <span className="action-item-icon">📄</span>
                    <div className="action-item-body">
                      <strong>Upload Missing Required Documents ({required_documents_missing.length})</strong>
                      <p>
                        Please upload: <em>{required_documents_missing.map((d) => formatDocumentType(d)).join(', ')}</em>
                      </p>
                    </div>
                  </div>
                )}

                {/* 2. Unresolved Discrepancies */}
                {unresolvedMismatches.length > 0 && (
                  <div className="action-item-card action-item-review">
                    <span className="action-item-icon">⚠️</span>
                    <div className="action-item-body">
                      <strong>Review & Confirm Discrepancies ({unresolvedMismatches.length})</strong>
                      <p>
                        Name or Date of Birth variations were detected. Scroll to the <strong>Detected Discrepancies</strong> section above to review and provide your confirmation note.
                      </p>
                    </div>
                  </div>
                )}

                {/* 3. Income Violation */}
                {incomeExceeded && (
                  <div className="action-item-card action-item-danger">
                    <span className="action-item-icon">💰</span>
                    <div className="action-item-body">
                      <strong>Family Income Exceeds Scholarship Cap</strong>
                      <p>
                        Extracted income of ₹{Number(incomeField.value).toLocaleString('en-IN')} exceeds the scheme maximum of ₹{rule_config.income_ceiling.toLocaleString('en-IN')}. Verify if an updated income certificate applies.
                      </p>
                    </div>
                  </div>
                )}

                {/* 4. Marks Cutoff Violation */}
                {marksBelow && (
                  <div className="action-item-card action-item-danger">
                    <span className="action-item-icon">🎓</span>
                    <div className="action-item-body">
                      <strong>Marks Below Eligibility Cutoff</strong>
                      <p>
                        Extracted aggregate of {percentageField.value}% is below the required cutoff of {rule_config.min_academic_percentage}%.
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Success guidance if all clear */}
          {isReady && (
            <div className="final-guidance guidance-success">
              <strong>All Checks Passed:</strong>
              <p>
                All {rule_config?.required_documents?.length || 3} mandatory documents are present, identity fields are consistent across documents, and eligibility thresholds are satisfied.
                Your application package is consistent and ready for formal submission!
              </p>
            </div>
          )}

          {/* Human-in-the-Loop Advisory Notice */}
          <div className="human-loop-disclaimer">
            <span className="disclaimer-icon">🛡️</span>
            <div className="disclaimer-text">
              <strong>Human-in-the-Loop Assurance:</strong>
              <p>
                Sahayak functions as an assistive pre-submission verification tool to help students catch mistakes, spelling variations, and missing documents before submission. Sahayak does not officially grant scholarships or alter student records without human review. Final award decisions rest solely with the scholarship authority.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
