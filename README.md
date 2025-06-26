# Smart Påminner Pro PWA

En moderne, progressiv web-app for smarte påminnelser med deling og e-post notifikasjoner.

## Funksjoner

- 📱 **PWA** - Installer som app på mobil/desktop
- 👥 **Deling** - Del påminnelser med andre brukere
- 📧 **E-post** - Automatiske e-post notifikasjoner
- 🔄 **Offline** - Fungerer uten internett
- 🔔 **Push notifications** - Få varsler på enheten din
- 🎨 **Responsiv** - Optimalisert for alle enheter
- 🧠 **Fokusmoduser** - Tilpass appen til dine behov (ADHD, Eldre, Stille, Jobb, Studie)
- 📋 **Delte tavler** - Samarbeid med andre på delte notis-tavler

## Nye funksjoner

### 🧠 Fokusmoduser
- **Stillemodus**: Reduserte notifikasjoner, kun høy prioritet
- **ADHD-modus**: Ekstra påminnelser, farger og struktur
- **Modus for eldre**: Større tekst og enklere grensesnitt
- **Jobbmodus**: Fokus på jobb-påminnelser i arbeidstid
- **Studiemodus**: Fokus på deadlines og læring

### 📋 Delte tavler
- Opprett delte notis-tavler med tilgangskoder
- Dra og slipp notiser på tavlen
- Samarbeid i sanntid med andre brukere
- Del tavler via lenker eller tilgangskoder

## Lokal utvikling

```bash
# Klon repository
git clone <repo-url>
cd smart_reminder_pwa

# Installer avhengigheter
pip install -r requirements.txt

# Kopier miljøvariabler
cp .env.example .env

# Rediger .env med dine innstillinger
# Spesielt e-post konfigurasjon

# Kjør app
python app.py
```

## Testing

```bash
# Kjør tester
python -m pytest tests/

# Eller kjør spesifikk test
python tests/test_app.py

# Teste API Endpoints
# Fokusmoduser
# GET /focus-modes
# POST /set-focus-mode

# Delte tavler
# GET /noteboards
# POST /create-board
# GET /board/<board_id>
# POST /join-board
# POST /add-note/<board_id>
# POST /api/update-note-position/<note_id>

# Teste deling av tavler
# Tilgangskode
# Direkte lenke
```

## API Endpoints

### Fokusmoduser
- `GET /focus-modes` - Vis fokusmoduser
- `POST /set-focus-mode` - Sett fokusmoduser

### Delte tavler
- `GET /noteboards` - Vis alle tavler
- `POST /create-board` - Opprett ny tavle
- `GET /board/<board_id>` - Vis spesifikk tavle
- `POST /join-board` - Bli med på tavle
- `POST /add-note/<board_id>` - Legg til notis
- `POST /api/update-note-position/<note_id>` - Oppdater notis-posisjon

## Deling av tavler

Tavler kan deles på to måter:
1. **Tilgangskode**: Del 8-sifret kode (f.eks. ABC12345)
2. **Direkte lenke**: `https://app.com/join-board?code=ABC12345`

## Sikkerhet

- CSRF-beskyttelse på alle skjemaer
- Brukerautorisering for alle sensitive operasjoner
- Validering av input-data
- Sikker lagring av brukerdata