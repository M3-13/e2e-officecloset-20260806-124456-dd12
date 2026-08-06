import { useState, useEffect, useRef, useCallback, type FormEvent, type ChangeEvent } from "react";
import { get, post, put, del } from "../services/api";
import "./WardrobePage.css";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api";
const SERVER_ORIGIN = API_BASE.replace(/\/api$/, "");

interface ItemOut {
  id: number;
  name: string;
  category: string;
  color: string | null;
  notes: string | null;
  image_url: string | null;
  created_at: string;
}

interface FormDataState {
  name: string;
  category: string;
  color: string;
  notes: string;
}

const EMPTY_FORM: FormDataState = {
  name: "",
  category: "top",
  color: "",
  notes: "",
};

const CATEGORIES: { value: string; label: string }[] = [
  { value: "", label: "Alle" },
  { value: "top", label: "Oberteil" },
  { value: "bottom", label: "Hose" },
  { value: "dress", label: "Kleid" },
  { value: "shoes", label: "Schuhe" },
  { value: "accessory", label: "Accessoire" },
];

const CATEGORY_LABELS: Record<string, string> = {
  top: "Oberteil",
  bottom: "Hose",
  dress: "Kleid",
  shoes: "Schuhe",
  accessory: "Accessoire",
};

interface ToastState {
  message: string;
  type: "success" | "error";
}

async function fetchImageAsBlob(imageUrl: string): Promise<string> {
  const token = localStorage.getItem("access_token");
  const fullUrl = imageUrl.startsWith("http") ? imageUrl : `${SERVER_ORIGIN}${imageUrl}`;
  const response = await fetch(fullUrl, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!response.ok) {
    throw new Error(`Bild konnte nicht geladen werden`);
  }
  const blob = await response.blob();
  return URL.createObjectURL(blob);
}

function ItemImage({ imageUrl, alt }: { imageUrl: string | null; alt: string }) {
  const [loadedUrl, setLoadedUrl] = useState<string | null>(null);
  const [loadError, setLoadError] = useState(false);
  const blobRef = useRef<string | null>(null);

  useEffect(() => {
    if (!imageUrl) {
      return;
    }
    let cancelled = false;
    setLoadedUrl(null);
    setLoadError(false);

    fetchImageAsBlob(imageUrl)
      .then((url) => {
        if (!cancelled) {
          if (blobRef.current) {
            URL.revokeObjectURL(blobRef.current);
          }
          blobRef.current = url;
          setLoadedUrl(url);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setLoadError(true);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [imageUrl]);

  useEffect(() => {
    return () => {
      if (blobRef.current) {
        URL.revokeObjectURL(blobRef.current);
        blobRef.current = null;
      }
    };
  }, []);

  if (!imageUrl || loadError) {
    return (
      <div className="wardrobe-card-image-placeholder">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
          <circle cx="8.5" cy="8.5" r="1.5" />
          <polyline points="21 15 16 10 5 21" />
        </svg>
      </div>
    );
  }

  if (!loadedUrl) {
    return <div className="wardrobe-card-image-placeholder wardrobe-card-image-loading" />;
  }

  return (
    <img
      src={loadedUrl}
      alt={alt}
      className="wardrobe-card-image"
      loading="lazy"
    />
  );
}

function Toast({ toast, onClose }: { toast: ToastState; onClose: () => void }) {
  useEffect(() => {
    const timer = setTimeout(onClose, 4000);
    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div className={`wardrobe-toast wardrobe-toast-${toast.type}`} onClick={onClose}>
      <span className="wardrobe-toast-message">{toast.message}</span>
    </div>
  );
}

function ConfirmDialog({
  open,
  onConfirm,
  onCancel,
}: {
  open: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}) {
  if (!open) return null;

  return (
    <div className="wardrobe-modal-backdrop" onClick={onCancel}>
      <div className="wardrobe-modal-container wardrobe-confirm-dialog" onClick={(e) => e.stopPropagation()}>
        <h3 className="wardrobe-modal-title">Kleidungsstück löschen</h3>
        <p style={{ color: "var(--color-fg_muted)", marginBottom: "var(--space-3)" }}>
          Möchtest du dieses Kleidungsstück wirklich löschen? Diese Aktion kann nicht rückgängig gemacht werden.
        </p>
        <div className="wardrobe-modal-actions">
          <button className="btn-secondary" onClick={onCancel}>Abbrechen</button>
          <button className="btn-danger" onClick={onConfirm}>Löschen</button>
        </div>
      </div>
    </div>
  );
}

export default function WardrobePage() {
  const [items, setItems] = useState<ItemOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingItem, setEditingItem] = useState<ItemOut | null>(null);
  const [deleteTargetId, setDeleteTargetId] = useState<number | null>(null);
  const [formData, setFormData] = useState<FormDataState>(EMPTY_FORM);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [toast, setToast] = useState<ToastState | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const previewRevokeRef = useRef<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const fetchItems = useCallback(async (category?: string | null) => {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setLoading(true);
    setError(null);
    try {
      const params = category ? `?category=${encodeURIComponent(category)}` : "";
      const data = await get<ItemOut[]>(`/wardrobe/items${params}`);
      if (!controller.signal.aborted) {
        setItems(data);
      }
    } catch (err) {
      if (!controller.signal.aborted) {
        const msg = err instanceof Error ? err.message : "Fehler beim Laden der Garderobe";
        setError(msg);
      }
    } finally {
      if (!controller.signal.aborted) {
        setLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    fetchItems(selectedCategory);
  }, [fetchItems, selectedCategory]);

  useEffect(() => {
    return () => {
      abortRef.current?.abort();
    };
  }, []);

  function handleCategoryClick(categoryValue: string) {
    setSelectedCategory(categoryValue || null);
  }

  function openCreateForm() {
    setEditingItem(null);
    setFormData(EMPTY_FORM);
    setImageFile(null);
    setImagePreview(null);
    setShowForm(true);
  }

  function openEditForm(item: ItemOut) {
    setEditingItem(item);
    setFormData({
      name: item.name,
      category: item.category,
      color: item.color || "",
      notes: item.notes || "",
    });
    setImageFile(null);
    setImagePreview(null);
    setShowForm(true);
  }

  function closeForm() {
    setShowForm(false);
    setEditingItem(null);
    if (previewRevokeRef.current) {
      URL.revokeObjectURL(previewRevokeRef.current);
      previewRevokeRef.current = null;
    }
  }

  function handleFormChange(e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  }

  function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0] || null;
    setImageFile(file);
    if (previewRevokeRef.current) {
      URL.revokeObjectURL(previewRevokeRef.current);
      previewRevokeRef.current = null;
    }
    if (file) {
      const url = URL.createObjectURL(file);
      previewRevokeRef.current = url;
      setImagePreview(url);
    } else {
      setImagePreview(null);
    }
  }

  async function handleFormSubmit(e: FormEvent) {
    e.preventDefault();
    setSubmitting(true);

    try {
      const fd = new FormData();
      fd.append("name", formData.name);
      fd.append("category", formData.category);
      if (formData.color) fd.append("color", formData.color);
      if (formData.notes) fd.append("notes", formData.notes);
      if (imageFile) fd.append("image", imageFile);

      if (editingItem) {
        await put<ItemOut>(`/wardrobe/items/${editingItem.id}`, fd, true);
        setToast({ message: "Kleidungsstück aktualisiert", type: "success" });
      } else {
        await post<ItemOut>("/wardrobe/items", fd, true);
        setToast({ message: "Kleidungsstück angelegt", type: "success" });
      }

      closeForm();
      fetchItems(selectedCategory);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Fehler beim Speichern";
      setToast({ message: msg, type: "error" });
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete(id: number) {
    try {
      await del(`/wardrobe/items/${id}`);
      setToast({ message: "Kleidungsstück gelöscht", type: "success" });
      setDeleteTargetId(null);
      fetchItems(selectedCategory);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Fehler beim Löschen";
      setToast({ message: msg, type: "error" });
    }
  }

  function clearToast() {
    setToast(null);
  }

  function renderContent() {
    if (loading) {
      return (
        <div className="wardrobe-loading">
          <div className="wardrobe-spinner" />
          <p style={{ color: "var(--color-fg_muted)", marginTop: "var(--space-2)" }}>
            Garderobe wird geladen...
          </p>
        </div>
      );
    }

    if (error) {
      return (
        <div className="wardrobe-empty">
          <p style={{ color: "var(--color-error)", marginBottom: "var(--space-2)" }}>
            {error}
          </p>
          <button className="btn-primary" onClick={() => fetchItems(selectedCategory)}>
            Erneut versuchen
          </button>
        </div>
      );
    }

    if (items.length === 0) {
      if (selectedCategory) {
        return (
          <div className="wardrobe-empty">
            <h2 className="wardrobe-empty-title">Keine Ergebnisse</h2>
            <p className="wardrobe-empty-text">
              In dieser Kategorie gibt es noch keine Kleidungsstücke.
            </p>
            <button className="btn-secondary" onClick={() => setSelectedCategory(null)}>
              Filter zurücksetzen
            </button>
          </div>
        );
      }

      return (
        <div className="wardrobe-empty">
          <h2 className="wardrobe-empty-title">Deine Garderobe ist noch leer</h2>
          <p className="wardrobe-empty-text">Leg los und füge dein erstes Kleidungsstück hinzu!</p>
          <button className="btn-primary" onClick={openCreateForm}>
            Erstes Kleidungsstück anlegen
          </button>
        </div>
      );
    }

    return (
      <div className="wardrobe-grid">
        {items.map((item) => (
          <div key={item.id} className="wardrobe-card">
            <div className="wardrobe-card-image-wrapper">
              <ItemImage imageUrl={item.image_url} alt={item.name} />
            </div>
            <div className="wardrobe-card-body">
              <h3 className="wardrobe-card-title">{item.name}</h3>
              <p className="wardrobe-card-meta">
                {CATEGORY_LABELS[item.category] || item.category}
                {item.color ? ` • ${item.color}` : ""}
              </p>
              <div className="wardrobe-card-actions">
                <button
                  className="wardrobe-card-btn"
                  onClick={() => openEditForm(item)}
                  title="Bearbeiten"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
                  </svg>
                </button>
                <button
                  className="wardrobe-card-btn wardrobe-card-btn-danger"
                  onClick={() => setDeleteTargetId(item.id)}
                  title="Löschen"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="3 6 5 6 21 6" />
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="page wardrobe-page">
      <div className="wardrobe-header">
        <h1>Garderobe</h1>
        <button className="btn-primary" onClick={openCreateForm}>
          Neues Kleidungsstück
        </button>
      </div>

      <div className="wardrobe-filters">
        {CATEGORIES.map((cat) => {
          const isActive = (cat.value || null) === selectedCategory;
          return (
            <button
              key={cat.value}
              className={`wardrobe-filter-chip${isActive ? " active" : ""}`}
              onClick={() => handleCategoryClick(cat.value)}
            >
              {cat.label}
            </button>
          );
        })}
      </div>

      {renderContent()}

      {showForm && (
        <div className="wardrobe-modal-backdrop" onClick={closeForm}>
          <div className="wardrobe-modal-container" onClick={(e) => e.stopPropagation()}>
            <button className="wardrobe-modal-close" onClick={closeForm}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>

            <h3 className="wardrobe-modal-title">
              {editingItem ? "Kleidungsstück bearbeiten" : "Neues Kleidungsstück"}
            </h3>

            <form onSubmit={handleFormSubmit} className="wardrobe-form">
              <div className="wardrobe-form-group">
                <label className="wardrobe-form-label" htmlFor="wardrobe-name">Name</label>
                <input
                  id="wardrobe-name"
                  className="wardrobe-input"
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleFormChange}
                  required
                  placeholder="z.B. Schwarze Lederjacke"
                />
              </div>

              <div className="wardrobe-form-group">
                <label className="wardrobe-form-label" htmlFor="wardrobe-category">Kategorie</label>
                <select
                  id="wardrobe-category"
                  className="wardrobe-input wardrobe-select"
                  name="category"
                  value={formData.category}
                  onChange={handleFormChange}
                  required
                >
                  {CATEGORIES.filter((c) => c.value !== "").map((cat) => (
                    <option key={cat.value} value={cat.value}>
                      {cat.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="wardrobe-form-group">
                <label className="wardrobe-form-label" htmlFor="wardrobe-color">Farbe</label>
                <input
                  id="wardrobe-color"
                  className="wardrobe-input"
                  type="text"
                  name="color"
                  value={formData.color}
                  onChange={handleFormChange}
                  placeholder="z.B. Schwarz"
                />
              </div>

              <div className="wardrobe-form-group">
                <label className="wardrobe-form-label" htmlFor="wardrobe-notes">Notizen</label>
                <textarea
                  id="wardrobe-notes"
                  className="wardrobe-input wardrobe-textarea"
                  name="notes"
                  value={formData.notes}
                  onChange={handleFormChange}
                  rows={3}
                  placeholder="Material, Marke, Anlass..."
                />
              </div>

              <div className="wardrobe-form-group">
                <label className="wardrobe-form-label">Bild</label>
                {editingItem?.image_url && !imagePreview && (
                  <div className="wardrobe-existing-image">
                    <ItemImage imageUrl={editingItem.image_url} alt={editingItem.name} />
                  </div>
                )}
                {imagePreview && (
                  <div className="wardrobe-preview-image">
                    <img src={imagePreview} alt="Vorschau" />
                  </div>
                )}
                <label className="wardrobe-file-label" htmlFor="wardrobe-image">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                    <polyline points="17 8 12 3 7 8" />
                    <line x1="12" y1="3" x2="12" y2="15" />
                  </svg>
                  {imagePreview || editingItem?.image_url
                    ? "Anderes Bild auswählen"
                    : "Bild auswählen"}
                </label>
                <input
                  ref={fileInputRef}
                  id="wardrobe-image"
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  onChange={handleFileChange}
                  style={{ display: "none" }}
                />
              </div>

              <div className="wardrobe-modal-actions">
                <button type="button" className="btn-secondary" onClick={closeForm}>
                  Abbrechen
                </button>
                <button type="submit" className="btn-primary" disabled={submitting}>
                  {submitting ? "Speichert..." : editingItem ? "Speichern" : "Anlegen"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <ConfirmDialog
        open={deleteTargetId !== null}
        onConfirm={() => {
          if (deleteTargetId !== null) handleDelete(deleteTargetId);
        }}
        onCancel={() => setDeleteTargetId(null)}
      />

      {toast && <Toast toast={toast} onClose={clearToast} />}
    </div>
  );
}
