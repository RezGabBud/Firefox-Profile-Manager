# Firefox Profile Manager

> 🇭🇺 [Magyar leírás lent](#magyar-leírás) · 🇬🇧 [English description below](#english-description)

---

## English Description

A fast, modern graphical Firefox profile launcher for Windows 11, built with Python and Tkinter. Inspired by Firefox's own profile manager UI.

### Features

- **Auto-detects all Firefox profiles** from `%APPDATA%\Mozilla\Firefox\Profiles\`
- **Tile-based UI** – each profile is shown as a card with an avatar (initial letter or custom image)
- **Dynamic grid layout** – automatically calculates columns and rows to fit all profiles on screen without scrolling; adapts to any resolution including 4K
- **Drag & drop reordering** – drag cards to rearrange profiles
- **Adjustable grid** – change columns/rows with the spinboxes in the header
- **Custom accent color** per profile (persisted across sessions)
- **Custom display name** per profile (does not affect the actual Firefox profile)
- **Custom image** per profile (requires Pillow)
- **Dark / light theme** – follows the Windows 11 system setting automatically
- **Single-instance isolation** – launches Firefox with `-no-remote` so each profile runs independently
- Closes itself after launching Firefox

### Requirements

| Requirement | Version |
|---|---|
| Python | 3.9+ |
| Windows | 10 / 11 |
| Firefox | Any (path: `C:\Program Files\Mozilla Firefox\firefox.exe`) |
| Pillow *(optional)* | `pip install pillow` – needed for custom profile images |

### Download

> **[⬇ Download latest EXE](https://github.com/RezGabBud/Firefox-Profile-Manager/releases/latest)**

No Python required – just download and run the `.exe` from the latest release.

### Installation


```bash
# Clone the repo
git clone https://github.com/RezGabBud/Firefox-Profile-Manager.git
cd Firefox-Profile-Manager

# (Optional) Install Pillow for image support
pip install pillow

# Run directly
python firefox_profile_manager.py
```

### Build a standalone EXE

Requires PyInstaller:

```bash
pip install pyinstaller
```

Place `firefox_profile.ico` in the same folder as the script, then run:

```bash
pyinstaller --onefile --windowed --icon=firefox_profile.ico --name="Firefox Profile Manager" --add-data "firefox_profile.ico;." firefox_profile_manager.py
```

The resulting `.exe` will appear in the `dist\` folder.

### Configuration

Settings are saved automatically to:

```
%APPDATA%\Mozilla\Firefox\profile_manager_config.json
```

Stored data: custom colors, display names, custom image paths, grid layout (column/row counts and card positions).

### How it works

1. On startup the app scans `%APPDATA%\Mozilla\Firefox\Profiles\` for valid profile folders (must contain `prefs.js`, `times.json`, or `compatibility.ini`).
2. The display name is derived from the folder name: `xxxxxxxx.ProfileName` → `ProfileName`.
3. Clicking a card launches Firefox with:
   ```
   "C:\Program Files\Mozilla Firefox\firefox.exe" -profile "<full profile path>" -no-remote
   ```
4. The app then closes itself.

### License

[MIT License](LICENSE)

---

## Magyar leírás

Gyors, modern grafikus Firefox profilindító Windows 11-re, Python + Tkinter alapon. A Firefox saját profilkezelőjéhez hasonló megjelenéssel.

### Funkciók

- **Automatikus profillista** – beolvassa az összes profilt a `%APPDATA%\Mozilla\Firefox\Profiles\` mappából
- **Csempés felület** – minden profil kártyaként jelenik meg, kezdőbetűs avatarral vagy egyéni képpel
- **Dinamikus elrendezés** – automatikusan számítja ki az optimális rácsot, hogy minden profil egyszerre látható legyen, görgetés nélkül; 4K felbontásig működik
- **Fogd és vidd rendezés** – a kártyák szabadon átrendezhetők húzással
- **Állítható rács** – az oszlop- és sorszám módosítható a fejlécben lévő forgatógombokkal
- **Egyéni szín** profilonként (újraindítás után is megmarad)
- **Egyéni megjelenítési név** profilonként (az eredeti Firefox profil nevét nem módosítja)
- **Egyéni kép** profilonként (Pillow szükséges)
- **Sötét / világos téma** – automatikusan követi a Windows 11 rendszerbeállítást
- **Izolált indítás** – a Firefox `-no-remote` kapcsolóval indul, így minden profil külön folyamatban fut
- Indítás után bezárja magát

### Követelmények

| Követelmény | Verzió |
|---|---|
| Python | 3.9+ |
| Windows | 10 / 11 |
| Firefox | Bármely (elérési út: `C:\Program Files\Mozilla Firefox\firefox.exe`) |
| Pillow *(opcionális)* | `pip install pillow` – egyéni profilképekhez szükséges |

### Letöltés

> **[⬇ Legújabb EXE letöltése](https://github.com/RezGabBud/Firefox-Profile-Manager/releases/latest)**

Python nem szükséges – töltsd le az `.exe` fájlt a legújabb release-ből és futtasd.

### Telepítés


```bash
# Repo klónozása
git clone https://github.com/RezGabBud/Firefox-Profile-Manager.git
cd Firefox-Profile-Manager

# (Opcionális) Pillow telepítése képtámogatáshoz
pip install pillow

# Közvetlen futtatás
python firefox_profile_manager.py
```

### EXE készítése

PyInstaller szükséges:

```bash
pip install pyinstaller
```

A `firefox_profile.ico` fájlt tedd ugyanabba a mappába, majd futtasd:

```bash
pyinstaller --onefile --windowed --icon=firefox_profile.ico --name="Firefox Profile Manager" --add-data "firefox_profile.ico;." firefox_profile_manager.py
```

A kész `.exe` a `dist\` mappában jelenik meg.

### Konfiguráció

A beállítások automatikusan mentődnek ide:

```
%APPDATA%\Mozilla\Firefox\profile_manager_config.json
```

Tárolt adatok: egyéni színek, megjelenítési nevek, képútvonalak, rácselrendezés (oszlop/sor szám és kártyapozíciók).

### Működés

1. Indításkor a program végigolvassa a `%APPDATA%\Mozilla\Firefox\Profiles\` mappát, és megkeresi az érvényes profilmappákat (amelyekben van `prefs.js`, `times.json` vagy `compatibility.ini`).
2. A megjelenítési nevet a mappaévből vezeti le: `xxxxxxxx.ProfilNev` → `ProfilNev`.
3. Egy kártyára kattintva a Firefox így indul el:
   ```
   "C:\Program Files\Mozilla Firefox\firefox.exe" -profile "<teljes profil elérési út>" -no-remote
   ```
4. Ezután az alkalmazás bezárja magát.

### Licenc

[MIT licenc](LICENSE)

---

### Trademark Notice / Védjegynyilatkozat

Firefox is a trademark of the Mozilla Foundation. This project is not affiliated with or endorsed by Mozilla.

A Firefox a Mozilla Foundation védjegye. Ez a projekt nem áll kapcsolatban a Mozillával, és nem élvezi annak jóváhagyását.
