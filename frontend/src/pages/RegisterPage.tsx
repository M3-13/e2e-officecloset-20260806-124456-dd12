import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import "./AuthPages.css";

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [fieldErrors, setFieldErrors] = useState<{
    email?: string;
    password?: string;
    confirmPassword?: string;
  }>({});
  const [submitting, setSubmitting] = useState(false);

  function validate(): boolean {
    const errors: { email?: string; password?: string; confirmPassword?: string } = {};

    if (!email.trim()) {
      errors.email = "E-Mail ist erforderlich";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) {
      errors.email = "Bitte eine gültige E-Mail-Adresse eingeben";
    }

    if (!password) {
      errors.password = "Passwort ist erforderlich";
    } else if (password.length < 8) {
      errors.password = "Passwort muss mindestens 8 Zeichen lang sein";
    }

    if (!confirmPassword) {
      errors.confirmPassword = "Bitte Passwort bestätigen";
    } else if (password !== confirmPassword) {
      errors.confirmPassword = "Passwörter stimmen nicht überein";
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
      await register(email.trim(), password);
      navigate("/wardrobe", { replace: true });
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Registrierung fehlgeschlagen");
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="auth-heading">Registrieren</h1>

        <form className="auth-form" onSubmit={handleSubmit} noValidate>
          <div className="auth-field">
            <label className="auth-label" htmlFor="register-email">E-Mail</label>
            <input
              id="register-email"
              className={`auth-input${fieldErrors.email ? " auth-input--error" : ""}`}
              type="email"
              autoComplete="email"
              placeholder="ihre@email.de"
              value={email}
              aria-invalid={fieldErrors.email ? true : undefined}
              aria-describedby={fieldErrors.email ? "register-email-err" : undefined}
              onChange={(e) => { setEmail(e.target.value); setFieldErrors((p) => ({ ...p, email: undefined })); }}
            />
            {fieldErrors.email && <span id="register-email-err" className="auth-field-error" role="alert">{fieldErrors.email}</span>}
          </div>

          <div className="auth-field">
            <label className="auth-label" htmlFor="register-password">Passwort</label>
            <input
              id="register-password"
              className={`auth-input${fieldErrors.password ? " auth-input--error" : ""}`}
              type="password"
              autoComplete="new-password"
              placeholder="Mindestens 8 Zeichen"
              value={password}
              aria-invalid={fieldErrors.password ? true : undefined}
              aria-describedby={fieldErrors.password ? "register-password-err" : undefined}
              onChange={(e) => { setPassword(e.target.value); setFieldErrors((p) => ({ ...p, password: undefined })); }}
            />
            {fieldErrors.password && <span id="register-password-err" className="auth-field-error" role="alert">{fieldErrors.password}</span>}
          </div>

          <div className="auth-field">
            <label className="auth-label" htmlFor="register-confirm-password">Passwort bestätigen</label>
            <input
              id="register-confirm-password"
              className={`auth-input${fieldErrors.confirmPassword ? " auth-input--error" : ""}`}
              type="password"
              autoComplete="new-password"
              placeholder="Passwort wiederholen"
              value={confirmPassword}
              aria-invalid={fieldErrors.confirmPassword ? true : undefined}
              aria-describedby={fieldErrors.confirmPassword ? "register-confirm-password-err" : undefined}
              onChange={(e) => { setConfirmPassword(e.target.value); setFieldErrors((p) => ({ ...p, confirmPassword: undefined })); }}
            />
            {fieldErrors.confirmPassword && <span id="register-confirm-password-err" className="auth-field-error" role="alert">{fieldErrors.confirmPassword}</span>}
          </div>

          {error && <div className="auth-error-banner" role="alert">{error}</div>}

          <button className="auth-submit" type="submit" disabled={submitting}>
            {submitting ? "Registrieren..." : "Registrieren"}
          </button>
        </form>

        <p className="auth-switch">
          Bereits registriert?{" "}
          <Link to="/login">Anmelden</Link>
        </p>
      </div>
    </div>
  );
}
