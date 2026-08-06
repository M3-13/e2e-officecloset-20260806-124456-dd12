import { useState, useEffect, useCallback } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { get, post, put } from "../services/api";
import "./OutfitCreatorPage.css";

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

export default function OutfitCreatorPage() {
  const { id } = useParams<{ id: string }>();
  const isEdit = Boolean(id);
  const navigate = useNavigate();

  const [wardrobeItems, setWardrobeItems] = useState<ItemOut[]>([]);
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [outfitName, setOutfitName] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function loadData() {
      try {
        const items = await get<ItemOut[]>("/wardrobe/items");
        if (cancelled) return;
        setWardrobeItems(items);

        if (isEdit && id) {
          const outfit = await get<OutfitOut>(`/outfits/${id}`);
          if (cancelled) return;
          setOutfitName(outfit.name);
          setSelectedIds(new Set(outfit.items.map((it) => it.id)));
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Fehler beim Laden der Daten");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    loadData();
    return () => {
      cancelled = true;
    };
  }, [id, isEdit]);

  const toggleItem = useCallback((itemId: number) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(itemId)) {
        next.delete(itemId);
      } else {
        next.add(itemId);
      }
      return next;
    });
  }, []);

  async function handleSave() {
    if (!outfitName.trim() || selectedIds.size === 0) return;
    setSaving(true);
    setError(null);
    try {
      const body = { name: outfitName.trim(), item_ids: Array.from(selectedIds) };
      if (isEdit && id) {
        await put<OutfitOut>(`/outfits/${id}`, body);
      } else {
        await post<OutfitOut>("/outfits", body);
      }
      navigate("/outfits");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Fehler beim Speichern");
    } finally {
      setSaving(false);
    }
  }

  const selectedItems = wardrobeItems.filter((i) => selectedIds.has(i.id));

  if (loading) {
    return (
      <div className="page">
        <h1>{isEdit ? "Outfit bearbeiten" : "Neues Outfit"}</h1>
        <div className="oc-spinner" />
      </div>
    );
  }

  return (
    <div className="page">
      <h1>{isEdit ? "Outfit bearbeiten" : "Neues Outfit"}</h1>

      <div className="oc-layout">
        <section className="oc-left">
          <h2 className="oc-section-title">Garderobe</h2>
          {wardrobeItems.length === 0 ? (
            <div className="oc-empty">
              <p className="oc-empty-title">Keine Kleidungsstücke vorhanden</p>
              <p className="oc-empty-text">
                Lege zuerst Kleidungsstücke in deiner Garderobe an, bevor du ein Outfit erstellst.
              </p>
            </div>
          ) : (
            <div className="oc-item-grid">
              {wardrobeItems.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  className={`oc-item-card${selectedIds.has(item.id) ? " oc-item-card--selected" : ""}`}
                  onClick={() => toggleItem(item.id)}
                  aria-pressed={selectedIds.has(item.id)}
                >
                  <div className="oc-item-card-image">
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
                    <div className={`oc-item-card-placeholder${item.image_url ? " oc-hidden" : ""}`}>
                      <span>{item.category}</span>
                    </div>
                  </div>
                  <div className="oc-item-card-info">
                    <span className="oc-item-card-name">{item.name}</span>
                    <span className="oc-item-card-meta">
                      {item.category}
                      {item.color ? ` \u00b7 ${item.color}` : ""}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </section>

        <section className="oc-right">
          <div className="oc-form-group">
            <label htmlFor="oc-outfit-name" className="oc-label">
              Outfit-Name
            </label>
            <input
              id="oc-outfit-name"
              type="text"
              className="oc-input"
              value={outfitName}
              onChange={(e) => setOutfitName(e.target.value)}
              placeholder="z.B. Sommer-Abendlook"
              maxLength={100}
            />
          </div>

          <h2 className="oc-section-title">Ausgewählte Items ({selectedItems.length})</h2>
          {selectedItems.length === 0 ? (
            <div className="oc-preview-empty">
              Klicke links auf Kleidungsstücke, um sie zum Outfit hinzuzufügen.
            </div>
          ) : (
            <div className="oc-preview-list">
              {selectedItems.map((item) => (
                <div key={item.id} className="oc-preview-item">
                  <div className="oc-preview-item-image">
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
                    <div className={`oc-preview-item-placeholder${item.image_url ? " oc-hidden" : ""}`}>
                      {item.category}
                    </div>
                  </div>
                  <div className="oc-preview-item-body">
                    <span className="oc-preview-item-name">{item.name}</span>
                    <span className="oc-preview-item-meta">
                      {item.category}
                      {item.color ? ` \u00b7 ${item.color}` : ""}
                    </span>
                  </div>
                  <button
                    type="button"
                    className="oc-preview-item-remove"
                    onClick={() => toggleItem(item.id)}
                    title={`${item.name} entfernen`}
                    aria-label={`${item.name} entfernen`}
                  >
                    &times;
                  </button>
                </div>
              ))}
            </div>
          )}

          {error && (
            <p className="oc-error" role="alert">
              {error}
            </p>
          )}

          <button
            type="button"
            className="oc-btn-save"
            onClick={handleSave}
            disabled={saving || !outfitName.trim() || selectedIds.size === 0}
          >
            {saving ? "Speichere..." : "Outfit speichern"}
          </button>
        </section>
      </div>
    </div>
  );
}
