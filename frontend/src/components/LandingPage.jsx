export function LandingPage({
  studentName,
  setStudentName,
  scholarships,
  selectedScholarshipId,
  setSelectedScholarshipId,
  onStartVerification,
  loading,
  error,
}) {
  const currentScholarship = scholarships.find(
    (s) => s.scholarship_id === selectedScholarshipId
  ) || scholarships[0]

  return (
    <main>
      <section className="hero-section" id="home">
        <div className="hero-content">
          <p className="tagline">DOCUMENT VERIFICATION ASSISTANT</p>

          <h1>
            Submit your application
            <span> with confidence.</span>
          </h1>

          <p className="hero-description">
            Sahayak automatically cross-checks your multi-document records, identifies
            spelling variations and eligibility discrepancies, and gives you a clear
            readiness report before you submit.
          </p>

          <div className="start-card">
            <div className="form-group">
              <label htmlFor="student-name">Student Full Name</label>
              <input
                id="student-name"
                type="text"
                value={studentName}
                onChange={(e) => setStudentName(e.target.value)}
                placeholder="e.g. Hana Sharma"
                disabled={loading}
              />
            </div>

            {scholarships.length > 0 && (
              <div className="form-group">
                <label htmlFor="scholarship-select">Select Scholarship Scheme</label>
                <select
                  id="scholarship-select"
                  value={selectedScholarshipId}
                  onChange={(e) => setSelectedScholarshipId(e.target.value)}
                  disabled={loading}
                >
                  {scholarships.map((scheme) => (
                    <option key={scheme.scholarship_id} value={scheme.scholarship_id}>
                      {scheme.name}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {currentScholarship && (
              <div className="scheme-preview-box">
                <div className="scheme-meta-row">
                  <span className="scheme-chip">
                    {currentScholarship.required_documents.length} Required Docs
                  </span>
                  {currentScholarship.income_ceiling && (
                    <span className="scheme-chip">
                      Max Income: ₹{(currentScholarship.income_ceiling / 100000).toFixed(1)} LPA
                    </span>
                  )}
                  {currentScholarship.min_academic_percentage && (
                    <span className="scheme-chip">
                      Min Marks: {currentScholarship.min_academic_percentage}%
                    </span>
                  )}
                </div>
                <p className="scheme-desc">{currentScholarship.description}</p>
              </div>
            )}

            {error && <p className="error-message">{error}</p>}

            <button
              className="primary-button full-width"
              type="button"
              onClick={onStartVerification}
              disabled={loading}
            >
              {loading ? 'Initializing Session...' : 'Start Verification →'}
            </button>
          </div>
        </div>

        <div className="hero-card">
          <div className="card-header">
            <span className="status-dot"></span>
            <strong>Verification Preview</strong>
          </div>

          <div className="document-item">
            <div>
              <strong>Aadhaar Card</strong>
              <small>Identity & DOB verification</small>
            </div>
            <span className="check">✓</span>
          </div>

          <div className="document-item">
            <div>
              <strong>12th Marksheet</strong>
              <small>Academic performance & name check</small>
            </div>
            <span className="check">✓</span>
          </div>

          <div className="document-item">
            <div>
              <strong>Income Certificate</strong>
              <small>Financial eligibility verification</small>
            </div>
            <span className="check">✓</span>
          </div>

          <div className="ready-message">
            <strong>Human-in-the-Loop Architecture</strong>
            <span>
              Sahayak detects mismatches and spelling nuances, explains their potential impact,
              and allows you to confirm corrections before final submission.
            </span>
          </div>
        </div>
      </section>

      <section className="features" id="how-it-works">
        <div className="section-heading">
          <p className="tagline">HOW SAHAYAK HELPS</p>
          <h2>One verification flow. Zero submission surprises.</h2>
        </div>

        <div className="feature-grid">
          <article className="feature-card">
            <div className="feature-number">01</div>
            <h3>Multi-Document Upload</h3>
            <p>
              Upload all required application documents together (Aadhaar, Marksheets,
              Income Certificates). Sahayak detects each document type automatically.
            </p>
          </article>

          <article className="feature-card">
            <div className="feature-number">02</div>
            <h3>Cross-Document Verification</h3>
            <p>
              Extracted fields are cross-matched across documents with intelligent fuzzy matching
              to detect name spellings, DOB mismatches, and income limit violations.
            </p>
          </article>

          <article className="feature-card">
            <div className="feature-number">03</div>
            <h3>Resolve Before Submission</h3>
            <p>
              Review clear explanations for flagged discrepancies. Resolve them with audit-logged
              human confirmations and get an instant application readiness assessment.
            </p>
          </article>
        </div>
      </section>
    </main>
  )
}
