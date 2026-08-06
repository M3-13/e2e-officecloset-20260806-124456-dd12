# Design — Project Identity

> This document is project-long-lived. Tokens are not changed without
> the Architect's approval. Developers MUST use these tokens
> instead of improvising their own colors/spacings.

## Style Direction

Tiefdunkles, luxuriöses Red-Carpet-Ambiente mit warmem Champagner-Gold (#D4AF37) als einzigem Akzent. Elegante Serifen-Typografie für Überschriften trifft auf klare Sans-Serif-Lesbarkeit. Reduziert wie das Portfolio eines exklusiven Modehauses – die Kleidungsstücke sind die Stars.

## Colors

- `--color-bg`: **#0B0A0A**
- `--color-bg_card`: **#151413**
- `--color-bg_elevated`: **#1D1B1A**
- `--color-fg`: **#EDEAE6**
- `--color-fg_muted`: **#9D9792**
- `--color-accent`: **#D4AF37**
- `--color-accent_hover`: **#E5C558**
- `--color-accent_pressed`: **#B8942E**
- `--color-border`: **#2C2926**
- `--color-border_focus`: **#D4AF37**
- `--color-error`: **#E05555**
- `--color-success`: **#5CAD6F**
- `--color-overlay`: **rgba(11,10,10,0.82)**

## Typography

- `font_family`: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif
- `heading_font_family`: "Playfair Display", "Times New Roman", serif
- `heading_weight`: 700
- `body_weight`: 400
- `body_size`: 16px
- `heading_scale`: h1: 2.5rem; h2: 1.875rem; h3: 1.375rem; h4: 1.125rem

## Spacing Scale

- `--space-0`: 4px
- `--space-1`: 8px
- `--space-2`: 16px
- `--space-3`: 24px
- `--space-4`: 32px
- `--space-5`: 48px
- `--space-6`: 64px

## Border-Radii

- `--radius-sm`: 4px
- `--radius-md`: 8px
- `--radius-lg`: 16px
- `--radius-pill`: 999px

## Components

### Button (Primary)

bg=accent #D4AF37, color=#0B0A0A, font-weight=600, padding 12px 28px, radius=md 8px, border=none, cursor=pointer, min-height=44px, transition=all 0.2s ease. hover: bg=#E5C558 (accent_hover), box-shadow=0 4px 20px rgba(212,175,55,0.25). active: bg=#B8942E (accent_pressed), transform=scale(0.98). disabled: opacity=0.45, cursor=not-allowed, box-shadow=none. focus-visible: outline 2px solid #D4AF37, outline-offset 2px.

### Button (Secondary/Ghost)

bg=transparent, color=#EDEAE6, font-weight=500, padding 10px 24px, radius=md 8px, border=1px solid #2C2926, min-height=44px, transition=all 0.2s ease. hover: border-color=#D4AF37, color=#D4AF37, bg=rgba(212,175,55,0.06). active: bg=rgba(212,175,55,0.12). disabled: opacity=0.4, cursor=not-allowed.

### Card (Kleidungsstück / Outfit)

bg=#151413 (bg_card), border=1px solid #2C2926, radius=lg 16px, overflow=hidden, transition=all 0.25s ease. hover: border-color=#D4AF37, box-shadow=0 8px 32px rgba(212,175,55,0.08), transform=translateY(-2px). Image area: aspect-ratio=3/4, object-fit=cover, bg=#1D1B1A. Content area: padding=16px. Title: font-family=Playfair Display, size=1rem, color=#EDEAE6. Meta (Kategorie/Farbe): size=0.8125rem, color=#9D9792.

### Input Field

bg=#151413, color=#EDEAE6, border=1px solid #2C2926, radius=md 8px, padding 12px 16px, font-size=16px, min-height=44px, width=100%, transition=border-color 0.2s ease. placeholder color=#6B6560. focus: border-color=#D4AF37, box-shadow=0 0 0 3px rgba(212,175,55,0.12), outline=none. error state: border-color=#E05555. disabled: opacity=0.5, cursor=not-allowed. Label: color=#9D9792, font-size=0.8125rem, font-weight=500, margin-bottom=6px, text-transform=uppercase, letter-spacing=0.05em.

### Modal / Dialog

backdrop=rgba(11,10,10,0.82), centered on screen. Container: bg=#151413, border=1px solid #2C2926, radius=lg 16px, padding=32px, max-width=560px, width=90vw, box-shadow=0 24px 64px rgba(0,0,0,0.6). Title: font-family=Playfair Display, size=1.5rem, color=#EDEAE6, margin-bottom=16px. Close button: position=absolute top 16px right 16px, bg=transparent, color=#9D9792, icon=X, hover color=#EDEAE6. Actions row: display=flex, justify-content=flex-end, gap=12px, margin-top=24px.

### Navigation Bar

bg=#0B0A0A with 1px bottom border #2C2926, position=sticky top 0, z-index=100, backdrop-filter=blur(12px). Inner: max-width=1200px, margin=0 auto, padding=16px 24px, display=flex, align-items=center, justify-content=space-between. Logo/Brand: font-family=Playfair Display, size=1.5rem, color=#D4AF37, font-weight=700, letter-spacing=-0.02em. Nav links: display=flex, gap=24px. Link: color=#9D9792, font-size=0.9375rem, font-weight=500, transition=color 0.2s, text-decoration=none. Link hover/active: color=#EDEAE6. Active route indicator: color=#D4AF37, small underline.

### Toast Notification

fixed position bottom-right, margin=24px, z-index=1000. Toast box: bg=#1D1B1A, border-left=3px solid (success=#5CAD6F / error=#E05555 / info=#D4AF37), radius=md 8px, padding=16px 20px, min-width=300px, max-width=420px, box-shadow=0 8px 24px rgba(0,0,0,0.5), animation=slide-in 0.3s ease. Title: font-weight=600, color=#EDEAE6. Message: font-size=0.875rem, color=#9D9792.

### Gallery Grid

display=grid, grid-template-columns=repeat(auto-fill, minmax(240px, 1fr)), gap=24px, padding=24px 0. Filter bar above grid: display=flex, gap=8px, flex-wrap=wrap, padding-bottom=24px. Filter chip: bg=#151413, border=1px solid #2C2926, radius=pill 999px, padding=8px 18px, font-size=0.8125rem, color=#9D9792, cursor=pointer, transition=all 0.2s. Chip hover: border-color=#D4AF37, color=#EDEAE6. Chip active/selected: bg=#D4AF37, color=#0B0A0A, border-color=#D4AF37.

### Outfit Creator Strip

Horizontal selected-items area: bg=#151413, border=1px solid #2C2926, radius=lg 16px, padding=16px, min-height=120px, display=flex, gap=12px, overflow-x=auto, align-items=center. Empty state: color=#6B6560, font-style=italic, text-align=center. Selected item thumbnail: width=80px, height=80px, radius=md 8px, object-fit=cover, border=2px solid #D4AF37. Item name below thumbnail: font-size=0.6875rem, color=#EDEAE6, text-align=center, max-width=80px, truncate. Remove badge: position=absolute top -6px right -6px, bg=#E05555, color=white, radius=pill, width=20px, height=20px, icon=X, cursor=pointer.

### File Upload Dropzone

bg=#151413, border=2px dashed #2C2926, radius=lg 16px, padding=48px 32px, text-align=center, cursor=pointer, transition=all 0.2s. hover: border-color=#D4AF37, bg=rgba(212,175,55,0.03). drag-over: border-color=#D4AF37, bg=rgba(212,175,55,0.06). Icon: camera/upload icon gold 48px center. Text: color=#9D9792, font-size=0.9375rem. Emphasis: color=#D4AF37. Preview after upload: replaces dropzone, image max-height=200px, radius=md.

## Layout Principles

- Container max-width: 1200px, horizontal padding: 32px (desktop) / 24px (tablet) / 16px (mobile). Margin: 0 auto center.
- Breakpoints: Desktop ≥1024px (primary target), Tablet 768–1023px, Mobile <768px. Gallery grid columns: 4 desktop / 3 tablet / 2 mobile.
- Page vertical rhythm: section padding-top 48px, padding-bottom 48px. Header-to-content gap 32px.
- Typography hierarchy: Playfair Display exclusively for page titles (h1), section headings (h2), card titles, and the brand logo. Body text always Inter at 16px / line-height 1.6. Small meta text at 0.8125rem / line-height 1.5.
- Color dominance: 90% dark surface (#0B0A0A, #151413, #1D1B1A), max 5% gold accent per viewport – sparsam eingesetzt, nur für primäre CTAs, aktive Zustände und Logo.
- Image-first layout: Kleidungsstück-Bilder dominieren jede Karte (>60% der Kartenfläche). Text ist sekundär und unterstützend.
- Spacing between gallery cards: 24px. Spacing between sections: 48px. Form groups: 20px apart. Consistent 16px inner card padding.
- Accessibility: All interactive elements ≥44px touch target. Focus styles visible (gold ring). Contrast ratio: text on dark ≥4.5:1 (fg #EDEAE6 on bg #0B0A0A = ~14:1 ✓). Never rely solely on color to convey state.
- Scroll behavior: gallery and outfit strips scroll smoothly, with visible scrollbar hint (thin, semi-transparent). No horizontal scroll on the full page.
