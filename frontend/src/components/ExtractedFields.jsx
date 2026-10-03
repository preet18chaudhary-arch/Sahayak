import {
  formatDocumentType,
  formatFieldName,
  formatFieldValue,
} from '../utils/formatters'

export function ExtractedFields({ extractedFields, documents }) {
  // Map document ids to document info for quick lookup
  const docMap = (documents || []).reduce((acc, doc) => {
    acc[doc.doc_id] = doc
    return acc
  }, {})

  return (
    <section className="dashboard-card">
      <div className="section-card-header">
        <div>
          <h3>Extracted Information ({extractedFields.length})</h3>
          <p className="section-card-subtitle">
            Structured data points read from your uploaded documents
          </p>
        </div>
      </div>

      {extractedFields.length === 0 ? (
        <div className="empty-state-box">
          <p>No information extracted yet.</p>
          <small>Extracted name, DOB, marks, and income fields will appear here once files are processed.</small>
        </div>
      ) : (
        <div className="extracted-fields-grid">
          {extractedFields.map((field, idx) => {
            const sourceDoc = docMap[field.source_doc_id]
            const confidencePct = Math.round((field.confidence || 1.0) * 100)

            return (
              <div className="field-card" key={`${field.field_name}-${idx}`}>
                <div className="field-card-top">
                  <span className="field-name-label">
                    {formatFieldName(field.field_name)}
                  </span>
                  <span className="confidence-pill" title="Extraction Confidence">
                    {confidencePct}% Confidence
                  </span>
                </div>

                <div className="field-value-display">
                  {formatFieldValue(field.field_name, field.value)}
                </div>

                {sourceDoc && (
                  <div className="field-source-footer">
                    <span className="source-label">Source Document:</span>
                    <span className="source-doc-name">
                      {formatDocumentType(sourceDoc.detected_type)} ({sourceDoc.file_name})
                    </span>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </section>
  )
}
