import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import "./AuthPages.css";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [fieldErrors, setFieldErrors] = useState<{ email?: string; password?: string }>({});
  const [submitting, setSubmitting] = useState(false);

  function validate(): boolean {
    const errors: { email?: string; password?: string } = {};

    if (!email.trim()) {
      errors.email = "E-Mail ist erforderlich";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
      errors.email = "Bitte eine gültige E-Mail-Adresse eingeben";
    }

    if (!password) {
      errors.password = "Passwort ist erforderlich";
    }

    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");

    if (!validate()) return;

    setSubmitting(true);
    try {
      await login(email.trim(), password);
      navigate("/wardrobe", { replace: true });
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Anmeldung fehlgeschlagen");
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="auth-heading">Anmelden</h1>

        <form className="auth-form" onSubmit={handleSubmit} noValidate>
          <div className="auth-field">
            <label className="auth-label" htmlFor="login-email">E-Mail</label>
            <input
              id="login-email"
              className={`auth-input${fieldErrors.email ? " auth-input--error" : ""}`}
              type="email"
              autoComplete="email"
              placeholder="ihre@email.de"
              value={email}
              aria-invalid={fieldErrors.email ? true : undefined}
              aria-describedby={fieldErrors.email ? "login-email-err" : undefined}
              onChange={(e) => { setEmail(e.target.value); setFieldErrors((p) => ({ ...p, email: undefined })); }}
            />
            {fieldErrors.email && <span id="login-email-err" className="auth-field-error" role="alert">{fieldErrors.email}</span>}
          </div>

          <div className="auth-field">
            <label className="auth-label" htmlFor="login-password">Passwort</label>
            <input
              id="login-password"
              className={`auth-input${fieldErrors.password ? " auth-input--error" : ""}`}
              type="password"
              autoComplete="current-password"
              placeholder="Ihr Passwort"
              value={password}
              aria-invalid={fieldErrors.password ? true : undefined}
              aria-describedby={fieldErrors.password ? "login-password-err" : undefined}
              onChange={(e) => { setPassword(e.target.value); setFieldErrors((p) => ({ ...p, password: undefined })); }}
            />
            {fieldErrors.password && <span id="login-password-err" className="auth-field-error" role="alert">{fieldErrors.password}</span>}
          </div>

          {error && <div className="auth-error-banner" role="alert">{error}</div>}

          <button className="auth-submit" type="submit" disabled={submitting}>
            {submitting ? "Anmelden..." : "Anmelden"}
          </button>
        </form>

        <p className="auth-switch">
          Noch kein Konto?{" "}
          <Link to="/register">Registrieren</Link>
        </p>
      </div>
    </div>
  );
}
