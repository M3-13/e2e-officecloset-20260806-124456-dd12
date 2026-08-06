import { NavLink } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import "./Navbar.css";

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <NavLink to="/" className="navbar-brand">
          Hollywood Closet
        </NavLink>

        <div className="navbar-links">
          <NavLink to="/wardrobe" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
            Garderobe
          </NavLink>
          <NavLink to="/outfits" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
            Outfits
          </NavLink>
          <NavLink to="/outfits/new" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
            Outfit-Creator
          </NavLink>
        </div>

        <div className="navbar-actions">
          {isAuthenticated ? (
            <>
              <span className="navbar-username">{user?.email}</span>
              <button className="btn-logout" onClick={logout}>
                Logout
              </button>
            </>
          ) : (
            <>
              <NavLink to="/login" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
                Login
              </NavLink>
              <NavLink to="/register" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
                Registrieren
              </NavLink>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
