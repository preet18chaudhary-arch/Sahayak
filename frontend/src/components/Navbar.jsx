export function Navbar({ onReset, session }) {
  return (
    <header className="navbar">
      <div className="logo-group" onClick={onReset} style={{ cursor: onReset ? 'pointer' : 'default' }}>
        <div className="logo">Sahayak</div>
        <span className="logo-badge">Verification Engine</span>
      </div>

      <nav>
        {session ? (
          <div className="session-navbar-info">
            <span className="session-badge">
              <span className="status-dot online"></span>
              Session: <strong>{session.session_id}</strong>
            </span>
            <button className="text-button" onClick={onReset}>
              + New Session
            </button>
          </div>
        ) : (
          <>
            <a href="#home">Home</a>
            <a href="#how-it-works">How It Works</a>
            <a href="#about">About</a>
          </>
        )}
      </nav>
    </header>
  )
}
