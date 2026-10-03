import { useRef, useState } from 'react'
import { formatDocumentType } from '../utils/formatters'

export function DocumentUpload({
  onUploadFiles,
  uploading,
  uploadProgress,
  lastUploadResult,
  error,
}) {
  const [selectedFiles, setSelectedFiles] = useState([])
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef(null)

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const newFiles = Array.from(e.target.files)
      setSelectedFiles((prev) => {
        const existingNames = new Set(prev.map((f) => f.name))
        const filteredNew = newFiles.filter((f) => !existingNames.has(f.name))
        return [...prev, ...filteredNew]
      })
    }
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFiles = Array.from(e.dataTransfer.files)
      setSelectedFiles((prev) => {
        const existingNames = new Set(prev.map((f) => f.name))
        const filteredNew = droppedFiles.filter((f) => !existingNames.has(f.name))
        return [...prev, ...filteredNew]
      })
    }
  }

  const handleRemoveFile = (fileName) => {
    setSelectedFiles((prev) => prev.filter((f) => f.name !== fileName))
  }

  const handleTriggerUpload = async () => {
    if (selectedFiles.length === 0 || uploading) return
    const filesToUpload = [...selectedFiles]
    const success = await onUploadFiles(filesToUpload)
    if (success) {
      setSelectedFiles([])
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  return (
    <section className="dashboard-card upload-section-card">
      <div className="section-card-header">
        <div>
          <h3>Upload Scholarship Documents</h3>
          <p className="section-card-subtitle">
            Upload Aadhaar, 12th Marksheet, and Income Certificate. You can select multiple files.
          </p>
        </div>
      </div>

      <div
        className={`dropzone-container ${isDragging ? 'dragging' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !uploading && fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".png,.jpg,.jpeg,.pdf,.webp"
          style={{ display: 'none' }}
          onChange={handleFileChange}
          disabled={uploading}
        />

        <div className="dropzone-icon">📁</div>
        <p className="dropzone-headline">
          {uploading ? 'Processing documents...' : 'Click to browse or drag & drop files here'}
        </p>
        <span className="dropzone-hint">
          Supports PNG, JPG, JPEG, and PDF (Max 15MB each)
        </span>
      </div>

      {selectedFiles.length > 0 && (
        <div className="selected-queue">
          <div className="selected-queue-header">
            <strong>Ready to Upload ({selectedFiles.length})</strong>
            <button
              type="button"
              className="text-button text-danger"
              onClick={() => setSelectedFiles([])}
              disabled={uploading}
            >
              Clear All
            </button>
          </div>

          <div className="selected-file-list">
            {selectedFiles.map((file) => (
              <div className="selected-file-item" key={file.name}>
                <div className="file-info">
                  <span className="file-icon">📄</span>
                  <div>
                    <span className="file-name">{file.name}</span>
                    <small className="file-size">
                      {(file.size / 1024).toFixed(1)} KB
                    </small>
                  </div>
                </div>

                {!uploading && (
                  <button
                    type="button"
                    className="remove-file-button"
                    onClick={(e) => {
                      e.stopPropagation()
                      handleRemoveFile(file.name)
                    }}
                    title="Remove file"
                  >
                    ✕
                  </button>
                )}
              </div>
            ))}
          </div>

          <div className="upload-action-row">
            <button
              className="primary-button upload-submit-btn"
              type="button"
              onClick={handleTriggerUpload}
              disabled={uploading}
            >
              {uploading
                ? `Uploading ${uploadProgress.current} of ${uploadProgress.total}...`
                : `Upload & Verify ${selectedFiles.length} Document${selectedFiles.length > 1 ? 's' : ''}`}
            </button>
          </div>
        </div>
      )}

      {uploading && (
        <div className="upload-progress-box">
          <div className="spinner"></div>
          <div className="progress-text">
            <strong>
              Uploading & Verifying {uploadProgress.current} of {uploadProgress.total}
            </strong>
            <span>Currently processing: <em>{uploadProgress.currentFileName}</em></span>
          </div>
          <div className="progress-bar-track">
            <div
              className="progress-bar-fill"
              style={{
                width: `${(uploadProgress.current / Math.max(uploadProgress.total, 1)) * 100}%`,
              }}
            ></div>
          </div>
        </div>
      )}

      {lastUploadResult && !uploading && (
        <div className="upload-success-banner">
          <span className="banner-check">✓</span>
          <div>
            <strong>Document Processed: {lastUploadResult.file_name}</strong>
            <p>
              Classified as: <strong>{formatDocumentType(lastUploadResult.detected_type)}</strong>
            </p>
          </div>
        </div>
      )}

      {error && <div className="error-banner">{error}</div>}
    </section>
  )
}
