import { formatDocumentType } from '../utils/formatters'

export function EligibilityResults({ ruleConfig, extractedFields, documents }) {
  if (!ruleConfig) return null

  // 1. Income rule check
  const incomeField = extractedFields.find((f) => f.field_name === 'income')
  const hasIncomeDoc = documents.some((d) => d.detected_type === 'income_certificate')
  let incomeStatus = 'PENDING'
  let incomeExtractedDisplay = 'Not yet uploaded'

  if (ruleConfig.income_ceiling !== null && ruleConfig.income_ceiling !== undefined) {
    if (incomeField) {
      const incVal = Number(incomeField.value)
      if (!isNaN(incVal)) {
        incomeStatus = incVal <= ruleConfig.income_ceiling ? 'PASSED' : 'FAILED'
        incomeExtractedDisplay = `₹${incVal.toLocaleString('en-IN')} / year`
      } else {
        incomeExtractedDisplay = incomeField.value
      }
    } else if (hasIncomeDoc) {
      incomeExtractedDisplay = 'Income document uploaded, reading value...'
    }
  }

  // 2. Academic percentage rule check
  const percentageField = extractedFields.find((f) => f.field_name === 'percentage')
  const hasMarksheetDoc = documents.some(
    (d) => d.detected_type === 'marksheet_12th' || d.detected_type === 'marksheet_10th'
  )
  let marksStatus = 'PENDING'
  let marksExtractedDisplay = 'Not yet uploaded'

  if (ruleConfig.min_academic_percentage !== null && ruleConfig.min_academic_percentage !== undefined) {
    if (percentageField) {
      const pctVal = Number(percentageField.value)
      if (!isNaN(pctVal)) {
        marksStatus = pctVal >= ruleConfig.min_academic_percentage ? 'PASSED' : 'FAILED'
        marksExtractedDisplay = `${pctVal}%`
      } else {
        marksExtractedDisplay = percentageField.value
      }
    } else if (hasMarksheetDoc) {
      marksExtractedDisplay = 'Marksheet uploaded, reading value...'
    }
  }

  // 3. Document Completeness rule check
  const requiredDocs = ruleConfig.required_documents || []
  const uploadedDetectedTypes = new Set(documents.map((d) => d.detected_type))
  const missingDocs = requiredDocs.filter((req) => !uploadedDetectedTypes.has(req))
  const docsStatus = missingDocs.length === 0 && requiredDocs.length > 0 ? 'PASSED' : 'PENDING'

  return (
    <section className="dashboard-card eligibility-card">
      <div className="section-card-header">
        <div>
          <h3>Scholarship Eligibility Evaluation</h3>
          <p className="section-card-subtitle">
            Automated check against the official rules for <strong>{ruleConfig.name}</strong>
          </p>
        </div>
        <span className="count-pill">Live Policy Check</span>
      </div>

      <div className="eligibility-table-wrapper">
        <table className="data-table eligibility-table">
          <thead>
            <tr>
              <th>Criteria / Rule</th>
              <th>Required Policy</th>
              <th>Your Extracted Value</th>
              <th>Evaluation Result</th>
            </tr>
          </thead>
          <tbody>
            {/* Rule 1: Income Ceiling */}
            {ruleConfig.income_ceiling !== null && ruleConfig.income_ceiling !== undefined ? (
              <tr>
                <td>
                  <div className="rule-title-cell">
                    <span className="rule-icon">💰</span>
                    <div>
                      <strong>Family Income Limit</strong>
                      <small>Must be equal or below ceiling</small>
                    </div>
                  </div>
                </td>
                <td>
                  <strong>₹{ruleConfig.income_ceiling.toLocaleString('en-IN')} / year</strong>
                </td>
                <td>
                  <span className={incomeStatus === 'FAILED' ? 'val-failed' : 'val-ok'}>
                    {incomeExtractedDisplay}
                  </span>
                </td>
                <td>
                  {incomeStatus === 'PASSED' && (
                    <span className="eval-tag eval-pass">
                      <span className="eval-icon">✓</span> PASSED (Eligible)
                    </span>
                  )}
                  {incomeStatus === 'FAILED' && (
                    <span className="eval-tag eval-fail">
                      <span className="eval-icon">✕</span> FAILED (Exceeds Limit)
                    </span>
                  )}
                  {incomeStatus === 'PENDING' && (
                    <span className="eval-tag eval-pending">
                      <span className="eval-icon">⏳</span> Pending Income Cert
                    </span>
                  )}
                </td>
              </tr>
            ) : (
              <tr>
                <td>
                  <div className="rule-title-cell">
                    <span className="rule-icon">💰</span>
                    <div>
                      <strong>Family Income Limit</strong>
                      <small>Financial criteria</small>
                    </div>
                  </div>
                </td>
                <td>
                  <span className="neutral-text">No income ceiling (Merit-based)</span>
                </td>
                <td>
                  <span className="neutral-text">{incomeExtractedDisplay}</span>
                </td>
                <td>
                  <span className="eval-tag eval-pass">
                    <span className="eval-icon">✓</span> Not Required
                  </span>
                </td>
              </tr>
            )}

            {/* Rule 2: Minimum Academic Percentage */}
            {ruleConfig.min_academic_percentage !== null && ruleConfig.min_academic_percentage !== undefined ? (
              <tr>
                <td>
                  <div className="rule-title-cell">
                    <span className="rule-icon">🎓</span>
                    <div>
                      <strong>Minimum Academic Marks</strong>
                      <small>Qualifying aggregate percentage</small>
                    </div>
                  </div>
                </td>
                <td>
                  <strong>Minimum {ruleConfig.min_academic_percentage}%</strong>
                </td>
                <td>
                  <span className={marksStatus === 'FAILED' ? 'val-failed' : 'val-ok'}>
                    {marksExtractedDisplay}
                  </span>
                </td>
                <td>
                  {marksStatus === 'PASSED' && (
                    <span className="eval-tag eval-pass">
                      <span className="eval-icon">✓</span> PASSED (Meets Cutoff)
                    </span>
                  )}
                  {marksStatus === 'FAILED' && (
                    <span className="eval-tag eval-fail">
                      <span className="eval-icon">✕</span> FAILED (Below Cutoff)
                    </span>
                  )}
                  {marksStatus === 'PENDING' && (
                    <span className="eval-tag eval-pending">
                      <span className="eval-icon">⏳</span> Pending Marksheet
                    </span>
                  )}
                </td>
              </tr>
            ) : null}

            {/* Rule 3: Document Completeness */}
            <tr>
              <td>
                <div className="rule-title-cell">
                  <span className="rule-icon">📑</span>
                  <div>
                    <strong>Mandatory Document Portfolio</strong>
                    <small>All required schemes documents present</small>
                  </div>
                </div>
              </td>
              <td>
                <strong>{requiredDocs.length} Mandatory Documents</strong>
              </td>
              <td>
                <span>
                  {documents.length} of {requiredDocs.length} uploaded
                </span>
              </td>
              <td>
                {docsStatus === 'PASSED' ? (
                  <span className="eval-tag eval-pass">
                    <span className="eval-icon">✓</span> ALL PRESENT
                  </span>
                ) : (
                  <span className="eval-tag eval-pending">
                    <span className="eval-icon">!</span> {missingDocs.length} Missing ({missingDocs.map((d) => formatDocumentType(d)).join(', ')})
                  </span>
                )}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  )
}
