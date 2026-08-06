# Glamouröser Kleiderschrank-Manager

Eine elegante Web-App zur Garderoben-Verwaltung im Hollywood-Stil. Benutzer registrieren sich, legen Kleidungsstücke mit Bildern und Kategorien an, durchstöbern ihre Garderobe und kombinieren im Outfit-Creator Einzelteile zu gespeicherten Outfits.

## Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **Datenbank**: SQLite mit SQLAlchemy ORM
- **Auth**: JWT (python-jose) + bcrypt (passlib)
- **Dateispeicher**: Lokales Upload-Verzeichnis `backend/uploads/`
- **Frontend**: Vite + React 18

## Installation

```bash
cd backend
pip install -r requirements.txt
```

## Entwicklung starten

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Das Backend ist dann unter `http://localhost:8000` erreichbar.

Um JWT-Signierung zu ermöglichen, setze die Umgebungsvariable `JWT_SECRET` (z. B. einen zufälligen 64-Zeichen-Hex-String):

```bash
# Windows PowerShell
$env:JWT_SECRET = "dein-geheimer-schlüssel"

# Linux/macOS
export JWT_SECRET="dein-geheimer-schlüssel"
```

Ohne gesetzten `JWT_SECRET` generiert der Server beim Start einen temporären Wert – für Entwicklung ausreichend, für Produktion nicht geeignet.

## API-Endpunkte

### Health

| Methode | Pfad          | Beschreibung            |
|---------|---------------|-------------------------|
| GET     | `/api/health` | Server-Status (200 OK)  |

### Auth (Stubs – Ticket #6)

| Methode | Pfad              | Request Body              | Response            |
|---------|-------------------|---------------------------|---------------------|
| POST    | `/api/auth/register` | `{email, password}`    | 201 `{id, email}`   |
| POST    | `/api/auth/login`    | `{email, password}`    | 200 `{access_token, token_type}` |
| GET     | `/api/auth/me`       | –                        | 200 `{id, email}`   |
| DELETE  | `/api/auth/me`       | –                        | 204                  |

### Kleiderschrank (Stubs – Ticket #4)

| Methode | Pfad                      | Request                          | Response       |
|---------|---------------------------|----------------------------------|----------------|
| GET     | `/api/wardrobe/items`     | Query: `?category=`              | 200 `[{ItemOut}]` |
| POST    | `/api/wardrobe/items`     | Multipart: image+name+category   | 201 `ItemOut`  |
| GET     | `/api/wardrobe/items/{id}`| –                                | 200 `ItemOut`  |
| PUT     | `/api/wardrobe/items/{id}`| Multipart                        | 200 `ItemOut`  |
| DELETE  | `/api/wardrobe/items/{id}`| –                                | 204            |
| GET     | `/api/wardrobe/images/{filename}` | –                         | 200 Bild       |

### Outfits (Stubs – Ticket #1)

| Methode | Pfad                     | Request Body                        | Response          |
|---------|--------------------------|-------------------------------------|-------------------|
| GET     | `/api/outfits`           | –                                   | 200 `[{OutfitOut}]` |
| POST    | `/api/outfits`           | `{name, item_ids: [int]}`           | 201 `OutfitOut`   |
| GET     | `/api/outfits/{id}`      | –                                   | 200 `OutfitOut`   |
| PUT     | `/api/outfits/{id}`      | `{name?, item_ids?}`                | 200 `OutfitOut`   |
| DELETE  | `/api/outfits/{id}`      | –                                   | 204               |

Alle `/wardrobe`-, `/outfits`- und `/items`-Endpunkte erfordern einen gültigen JWT im `Authorization: Bearer <token>`-Header.

## Features

- Benutzerregistrierung und -login mit JWT-Authentifizierung
- Verwaltung von Kleidungsstücken mit Bild-Upload und Kategorisierung
- Garderoben-Galerie mit Filter nach Kategorie
- Outfit-Creator zum Kombinieren von Kleidungsstücken
- Elegante Red-Carpet-Optik mit dunklem Hintergrund und Goldakzenten
