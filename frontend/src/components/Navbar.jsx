export function Navbar({
  onReset,
  session,
  loggedInUser,
  onLogout,
}) {
  return (
    <header className="navbar">
      <div
        className="logo-group"
        onClick={onReset}
        style={{
          cursor: onReset ? 'pointer' : 'default',
        }}
      >
        <div className="logo">Sahayak</div>

        <span className="logo-badge">
          Verification Engine
        </span>
      </div>

      {loggedInUser && onLogout && (
        <nav>
          {session ? (
            <div className="session-navbar-info">
              <span className="session-badge">
                <span className="status-dot online"></span>
                Session: <strong>{session.session_id}</strong>
              </span>

              <button
                className="text-button"
                onClick={onReset}
              >
                + New Session
              </button>

              <button
                className="logout-button"
                onClick={onLogout}
              >
                Logout
              </button>
            </div>
          ) : (
            <div className="logged-in-navbar">
              <span className="welcome-user">
                Welcome, <strong>{loggedInUser}</strong>
              </span>

              <button
                className="logout-button"
                onClick={onLogout}
              >
                Logout
              </button>
            </div>
          )}
        </nav>
      )}
    </header>
  )
}
