import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { get, del } from "../services/api";
import "./OutfitsPage.css";

interface ItemOut {
  id: number;
  name: string;
  category: string;
  color: string | null;
  notes: string | null;
  image_url: string | null;
  created_at: string;
}

interface OutfitOut {
  id: number;
  name: string;
  items: ItemOut[];
  created_at: string;
}

function getApiBase(): string {
  return import.meta.env.VITE_API_URL || "http://localhost:8000/api";
}

function makeImageUrl(imageUrl: string | null): string {
  if (!imageUrl) return "";
  const clean = imageUrl.replace(/^\/api/, "");
  return `${getApiBase()}${clean}`;
}

export default function OutfitsPage() {
  const navigate = useNavigate();
  const [outfits, setOutfits] = useState<OutfitOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<OutfitOut | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [toast, setToast] = useState<{ message: string; type: "success" | "error" } | null>(null);

  const showToast = useCallback(
    (message: string, type: "success" | "error") => {
      setToast({ message, type });
      setTimeout(() => setToast(null), 4000);
    },
    [],
  );

  const loadOutfits = useCallback(async () => {
    try {
      const data = await get<OutfitOut[]>("/outfits");
      setOutfits(data);
      setFetchError(null);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Fehler beim Laden der Outfits";
      setFetchError(msg);
      showToast(msg, "error");
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  useEffect(() => {
    loadOutfits();
  }, [loadOutfits]);

  async function handleDelete() {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await del(`/outfits/${deleteTarget.id}`);
      setOutfits((prev) => prev.filter((o) => o.id !== deleteTarget.id));
      setDeleteTarget(null);
      showToast("Outfit gel\u00f6scht", "success");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Fehler beim L\u00f6schen";
      showToast(msg, "error");
    } finally {
      setDeleting(false);
    }
  }

  function formatDate(iso: string): string {
    const d = new Date(iso);
    return d.toLocaleDateString("de-DE", { day: "2-digit", month: "2-digit", year: "numeric" });
  }

  if (loading) {
    return (
      <div className="page">
        <h1>Outfits</h1>
        <div className="of-spinner" />
      </div>
    );
  }

  const outfitsContent =
    outfits.length === 0 ? (
      <div className="of-empty">
        <p className="of-empty-text">Noch keine Outfits – kombiniere deinen ersten Look!</p>
        <button type="button" className="of-btn-primary" onClick={() => navigate("/outfits/new")}>
          Zum Outfit-Creator
        </button>
      </div>
    ) : (
      <div className="of-grid">
        {outfits.map((outfit) => (
          <div key={outfit.id} className="of-card">
            <div className="of-card-images">
              {outfit.items.length === 0 ? (
                <div className="of-card-images-empty">Keine Items</div>
              ) : (
                <>
                  {outfit.items.slice(0, 6).map((item) => (
                    <div key={item.id} className="of-card-thumb">
                      {item.image_url ? (
                        <img
                          src={makeImageUrl(item.image_url)}
                          alt={item.name}
                          loading="lazy"
                          onError={(e) => {
                            const img = e.target as HTMLImageElement;
                            img.style.display = "none";
                            const ph = img.nextElementSibling;
                            if (ph) ph.classList.remove("oc-hidden");
                          }}
                        />
                      ) : null}
                      <div className={`of-card-thumb-ph${item.image_url ? " oc-hidden" : ""}`}>
                        {item.category.charAt(0).toUpperCase()}
                      </div>
                    </div>
                  ))}
                  {outfit.items.length > 6 && (
                    <div className="of-card-thumb-more">+{outfit.items.length - 6}</div>
                  )}
                </>
              )}
            </div>
            <div className="of-card-body">
              <h3 className="of-card-name">{outfit.name}</h3>
              <span className="of-card-meta">
                {outfit.items.length} {outfit.items.length === 1 ? "Item" : "Items"} &middot;{" "}
                {formatDate(outfit.created_at)}
              </span>
            </div>
            <div className="of-card-actions">
              <button
                type="button"
                className="of-btn-secondary"
                onClick={() => navigate(`/outfits/${outfit.id}/edit`)}
              >
                Bearbeiten
              </button>
              <button
                type="button"
                className="of-btn-danger"
                onClick={() => setDeleteTarget(outfit)}
              >
                L&ouml;schen
              </button>
            </div>
          </div>
        ))}
      </div>
    );

  return (
    <div className="page">
      <div className="of-header">
        <h1>Outfits</h1>
        <button type="button" className="of-btn-primary" onClick={() => navigate("/outfits/new")}>
          Neues Outfit
        </button>
      </div>

      {fetchError && (
        <div className="of-inline-error" role="alert">
          {fetchError}
        </div>
      )}

      {outfitsContent}

      {deleteTarget && (
        <div
          className="of-modal-overlay"
          onClick={() => {
            if (!deleting) setDeleteTarget(null);
          }}
        >
          <div className="of-modal" onClick={(e) => e.stopPropagation()}>
            <h2 className="of-modal-title">Outfit l&ouml;schen</h2>
            <p className="of-modal-text">
              M&ouml;chtest du das Outfit &quot;{deleteTarget.name}&quot; wirklich l&ouml;schen? Diese
              Aktion kann nicht r&uuml;ckg&auml;ngig gemacht werden.
            </p>
            <div className="of-modal-actions">
              <button
                type="button"
                className="of-btn-secondary"
                onClick={() => setDeleteTarget(null)}
                disabled={deleting}
              >
                Abbrechen
              </button>
              <button
                type="button"
                className="of-btn-danger"
                onClick={handleDelete}
                disabled={deleting}
              >
                {deleting ? "L&ouml;sche..." : "L&ouml;schen"}
              </button>
            </div>
          </div>
        </div>
      )}

      {toast && (
        <div className={`of-toast of-toast--${toast.type}`} role="alert">
          <span className="of-toast-title">{toast.type === "success" ? "Erfolg" : "Fehler"}</span>
          <span className="of-toast-text">{toast.message}</span>
        </div>
      )}
    </div>
  );
}
