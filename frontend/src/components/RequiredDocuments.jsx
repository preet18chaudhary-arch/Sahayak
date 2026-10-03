import { formatDocumentType } from '../utils/formatters'

export function RequiredDocuments({ ruleConfig, uploadedDocuments }) {
  if (!ruleConfig || !ruleConfig.required_documents) {
    return null
  }

  const requiredList = ruleConfig.required_documents

  return (
    <section className="dashboard-card">
      <div className="section-card-header">
        <div>
          <h3>Required Documents Checklist</h3>
          <p className="section-card-subtitle">
            Mandatory documents required for {ruleConfig.name}
          </p>
        </div>
        <span className="count-pill">
          {uploadedDocuments.length} / {requiredList.length} Uploaded
        </span>
      </div>

      <div className="required-docs-grid">
        {requiredList.map((docType) => {
          const matchingUploads = uploadedDocuments.filter(
            (doc) => doc.detected_type === docType
          )
          const isUploaded = matchingUploads.length > 0

          return (
            <div
              key={docType}
              className={`doc-checklist-item ${isUploaded ? 'uploaded' : 'missing'}`}
            >
              <div className="doc-checklist-status-icon">
                {isUploaded ? '✓' : '!'}
              </div>

              <div className="doc-checklist-content">
                <div className="doc-checklist-title-row">
                  <strong>{formatDocumentType(docType)}</strong>
                  <span className={`status-tag ${isUploaded ? 'tag-green' : 'tag-orange'}`}>
                    {isUploaded ? 'Uploaded & Verified' : 'Missing'}
                  </span>
                </div>

                <div className="doc-checklist-meta">
                  <span className="meta-requirement">Required Document</span>
                  {isUploaded && (
                    <span className="meta-filename">
                      Matched from: <em>{matchingUploads[0].file_name}</em>
                    </span>
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </section>
  )
}
