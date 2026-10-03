import { formatDateTime, formatDocumentType } from '../utils/formatters'

export function UploadedDocuments({ documents }) {
  return (
    <section className="dashboard-card">
      <div className="section-card-header">
        <div>
          <h3>Uploaded Documents ({documents.length})</h3>
          <p className="section-card-subtitle">
            Files analyzed and verified by the Sahayak engine
          </p>
        </div>
      </div>

      {documents.length === 0 ? (
        <div className="empty-state-box">
          <p>No documents uploaded yet.</p>
          <small>Select and upload your files above to start verification.</small>
        </div>
      ) : (
        <div className="uploaded-docs-table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Document File</th>
                <th>Detected Type</th>
                <th>Upload Time</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {documents.map((doc) => (
                <tr key={doc.doc_id}>
                  <td>
                    <div className="doc-file-cell">
                      <span className="file-icon-small">📄</span>
                      <div>
                        <strong>{doc.file_name}</strong>
                        <span className="doc-id-subtext">{doc.doc_id}</span>
                      </div>
                    </div>
                  </td>
                  <td>
                    <span className="detected-type-badge">
                      {formatDocumentType(doc.detected_type)}
                    </span>
                  </td>
                  <td className="timestamp-cell">
                    {formatDateTime(doc.uploaded_at)}
                  </td>
                  <td>
                    <span className="status-tag tag-green">
                      Analyzed & Verified
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}
