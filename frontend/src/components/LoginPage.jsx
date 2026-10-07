export function LoginPage({ onLogin }) {
  const handleSubmit = (event) => {
    event.preventDefault()

    const form = new FormData(event.currentTarget)
    const name = form.get('name')?.trim()

    if (!name) {
      return
    }

    onLogin(name)
  }

  return (
    <main className="login-page">
      <div className="login-container">

        <div className="login-card">

          <div className="login-brand">
            <div className="login-logo">S</div>

            <div>
              <div className="login-brand-name">Sahayak</div>
              <div className="login-brand-subtitle">
                Verification Engine
              </div>
            </div>
          </div>

          <div className="login-heading">
            <h1>Welcome back</h1>
            <p>
              Sign in to continue with document verification.
            </p>
          </div>

          <form onSubmit={handleSubmit}>

            <div className="login-field">
              <label htmlFor="name">Your Name</label>

              <input
                id="name"
                name="name"
                type="text"
                placeholder="Enter your name"
                autoComplete="name"
                required
              />
            </div>

            <div className="login-field">
              <label htmlFor="email">Email Address</label>

              <input
                id="email"
                name="email"
                type="email"
                placeholder="Enter your email"
                autoComplete="email"
                required
              />
            </div>

            <div className="login-field">
              <label htmlFor="password">Password</label>

              <input
                id="password"
                name="password"
                type="password"
                placeholder="Enter your password"
                autoComplete="current-password"
                required
              />
            </div>

            <button type="submit" className="login-button">
              Sign In
            </button>

          </form>

          <div className="login-note">
            Demo login for Sahayak verification system
          </div>

        </div>

      </div>
    </main>
  )
}