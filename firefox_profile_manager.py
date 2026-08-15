# Firefox Profile Manager
# Copyright (c) 2026 RezGabBud (https://github.com/RezGabBud/)
# Licensed under the MIT License – see LICENSE file for details.

import tkinter as tk
from tkinter import colorchooser, messagebox, simpledialog, filedialog
import os
import subprocess
import json
import sys
import ctypes

try:
    from PIL import Image, ImageTk, ImageDraw

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import winreg

    WINREG_AVAILABLE = True
except ImportError:
    WINREG_AVAILABLE = False

# --- Konstansok és Téma ---
FIREFOX_EXE = r"C:\Program Files\Mozilla Firefox\firefox.exe"
CONFIG_FILE = os.path.join(os.environ.get("APPDATA", ""), "Mozilla", "Firefox", "profile_manager_config.json")

CARD_W = 230
CARD_H = 290
GAP = 30
OUTER_PAD = 100
HEADER_H = 120
FOOTER_H = 72
CORNER_R = 16

DEFAULT_COLORS = [
    "#8F6FEF", "#E9649A", "#42B4C8", "#4DB858",
    "#F4A12C", "#E05C4B", "#2196F3", "#9C27B0",
    "#00BCD4", "#FF7043", "#66BB6A", "#AB47BC",
]


def get_system_theme():
    if WINREG_AVAILABLE:
        try:
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            if value == 1:
                return "light"
        except Exception:
            pass
    return "dark"


THEMES = {
    "dark": {
        "BG": "#1C1B22",
        "CARD": "#2B2A33",
        "CARD_HOVER": "#38374B",
        "TEXT": "#F9F9FB",
        "TEXT_SEC": "#CFCFD8",
        "ACCENT": "#8F6FEF",
        "BORDER": "#52525E",
        "PLACEHOLDER": "#23222B",
    },
    "light": {
        "BG": "#F9F9FB",
        "CARD": "#FFFFFF",
        "CARD_HOVER": "#EFEFF4",
        "TEXT": "#15141A",
        "TEXT_SEC": "#5C5C66",
        "ACCENT": "#0060DF",
        "BORDER": "#D7D7DB",
        "PLACEHOLDER": "#EDEDF0",
    }
}

T = THEMES[get_system_theme()]


# ---------------------------------------------------------------------------
# Adatok beolvasása
# ---------------------------------------------------------------------------

def betolt_profilok():
    """
    Kizárólag a %APPDATA%\\Mozilla\\Firefox\\Profiles\\ mappát olvassa be.
    profiles.ini-t nem használ.
    Érvényes profilmappának számít, amiben van prefs.js, times.json vagy compatibility.ini.
    A profil megjelenítési neve: a mappaév pontja utáni rész (pl. "abc12345.Munka" → "Munka").
    Ha nincs pont, a teljes mappaév a név.
    """
    profiles_dir = os.path.join(
        os.environ.get("APPDATA", ""), "Mozilla", "Firefox", "Profiles"
    )
    if not os.path.exists(profiles_dir):
        messagebox.showerror(
            "Error",
            f"Profiles folder not found:\n{profiles_dir}"
        )
        sys.exit(1)

    profilok = {}  # {megjelenítési_név: teljes_elérési_út}
    marker_fajlok = {"prefs.js", "times.json", "compatibility.ini"}

    for mappa_nev in sorted(os.listdir(profiles_dir)):
        mappa_ut = os.path.join(profiles_dir, mappa_nev)
        if not os.path.isdir(mappa_ut):
            continue
        # Csak érvényes profilmappák (van legalább egy marker fájl)
        if not any(os.path.exists(os.path.join(mappa_ut, m)) for m in marker_fajlok):
            continue

        # Név levezetése: "8karakter.ProfilNev" → "ProfilNev"
        reszek = mappa_nev.split(".", 1)
        if len(reszek) == 2 and len(reszek[0]) == 8:
            baze_nev = reszek[1]
        else:
            baze_nev = mappa_nev

        # Ütközéskezelés (két mappa ugyanolyan névvel)
        vegleges_nev = baze_nev
        counter = 1
        while vegleges_nev in profilok:
            vegleges_nev = f"{baze_nev} ({counter})"
            counter += 1

        profilok[vegleges_nev] = os.path.normpath(mappa_ut)

    return profilok


def betolt_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def ment_config(config_data):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Konfigurációs hiba: {e}")


def indit_firefox(profil_utvonal):
    if not os.path.exists(FIREFOX_EXE):
        messagebox.showerror("Error", f"Firefox not found:\n{FIREFOX_EXE}")
        return False
    try:
        subprocess.Popen([FIREFOX_EXE, "-profile", profil_utvonal, "-no-remote"])
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Failed to launch Firefox:\n{e}")
        return False


# ---------------------------------------------------------------------------
# Rajzolás segédfüggvények
# ---------------------------------------------------------------------------

def rounded_rect(canvas, x1, y1, x2, y2, r, **kwargs):
    canvas.create_arc(x1, y1, x1 + 2 * r, y1 + 2 * r, start=90, extent=90, style="pieslice", outline="", **kwargs)
    canvas.create_arc(x2 - 2 * r, y1, x2, y1 + 2 * r, start=0, extent=90, style="pieslice", outline="", **kwargs)
    canvas.create_arc(x1, y2 - 2 * r, x1 + 2 * r, y2, start=180, extent=90, style="pieslice", outline="", **kwargs)
    canvas.create_arc(x2 - 2 * r, y2 - 2 * r, x2, y2, start=270, extent=90, style="pieslice", outline="", **kwargs)
    canvas.create_rectangle(x1 + r, y1, x2 - r, y2, outline="", **kwargs)
    canvas.create_rectangle(x1, y1 + r, x2, y2 - r, outline="", **kwargs)


def draw_hollow_rounded_rect(canvas, x1, y1, x2, y2, r, color, width=2):
    canvas.create_arc(x1, y1, x1 + 2 * r, y1 + 2 * r, start=90, extent=90, style="arc", outline=color, width=width)
    canvas.create_arc(x2 - 2 * r, y1, x2, y1 + 2 * r, start=0, extent=90, style="arc", outline=color, width=width)
    canvas.create_arc(x1, y2 - 2 * r, x1 + 2 * r, y2, start=180, extent=90, style="arc", outline=color, width=width)
    canvas.create_arc(x2 - 2 * r, y2 - 2 * r, x2, y2, start=270, extent=90, style="arc", outline=color, width=width)
    canvas.create_line(x1 + r, y1, x2 - r, y1, fill=color, width=width)
    canvas.create_line(x1 + r, y2, x2 - r, y2, fill=color, width=width)
    canvas.create_line(x1, y1 + r, x1, y2 - r, fill=color, width=width)
    canvas.create_line(x2, y1 + r, x2, y2 - r, fill=color, width=width)


# ---------------------------------------------------------------------------
# Kártya widget
# ---------------------------------------------------------------------------

class ProfilKartya(tk.Canvas):
    def __init__(self, parent, eredeti_nev, megjeleno_nev, szin, kep_utvonal, callbacks, **kwargs):
        super().__init__(parent, width=CARD_W, height=CARD_H, bg=T["BG"], highlightthickness=0, cursor="hand2")
        self.eredeti_nev, self.megjeleno_nev, self.szin, self.kep_utvonal = eredeti_nev, megjeleno_nev, szin, kep_utvonal
        self.cb = callbacks
        self._hover = False
        self._is_dragging = False
        self._photo_img = None
        self._rajzol()
        self._esemenyek_kotese()

    def _rajzol(self):
        self.delete("all")
        w, h = CARD_W, CARD_H
        bg = T["CARD_HOVER"] if self._hover else T["CARD"]
        bord = T["ACCENT"] if self._hover else T["BORDER"]

        rounded_rect(self, 0, 0, w, h, CORNER_R, fill=bg)
        draw_hollow_rounded_rect(self, 1, 1, w - 1, h - 1, CORNER_R, bord, width=1)

        cx, cy = w // 2, int(h * 0.38)
        img_size = 170

        if PIL_AVAILABLE and self.kep_utvonal and os.path.exists(self.kep_utvonal):
            try:
                img = Image.open(self.kep_utvonal).convert("RGBA")
                min_dim = min(img.width, img.height)
                left, top = (img.width - min_dim) / 2, (img.height - min_dim) / 2
                img = img.crop((left, top, left + min_dim, top + min_dim)).resize((img_size, img_size),
                                                                                  Image.Resampling.LANCZOS)
                mask = Image.new("L", (img_size, img_size), 0)
                ImageDraw.Draw(mask).rounded_rectangle((0, 0, img_size, img_size), radius=CORNER_R, fill=255)
                img.putalpha(mask)
                self._photo_img = ImageTk.PhotoImage(img)
                self.create_image(cx, cy, image=self._photo_img)
            except:
                self._rajzol_avatar(cx, cy, img_size // 2)
        else:
            self._rajzol_avatar(cx, cy, img_size // 2)

        rovid_nev = self.megjeleno_nev if len(self.megjeleno_nev) <= 15 else self.megjeleno_nev[:14] + "…"
        self.create_text(w // 2, int(h * 0.74), text=rovid_nev, font=("Segoe UI", 20, "bold"), fill=T["TEXT"],
                         tags="nev")

        self.create_text(w * 0.20, int(h * 0.90), text="● color", font=("Segoe UI", 9), fill=T["TEXT_SEC"],
                         tags="szin_btn")
        self.create_text(w * 0.50, int(h * 0.90), text="✎ name", font=("Segoe UI", 9), fill=T["TEXT_SEC"],
                         tags="nev_btn")
        self.create_text(w * 0.80, int(h * 0.90), text="🖼️ image", font=("Segoe UI", 9), fill=T["TEXT_SEC"],
                         tags="kep_btn")

    def _rajzol_avatar(self, cx, cy, r):
        self.create_oval(cx - r + 3, cy - r + 3, cx + r + 3, cy + r + 3,
                         fill="#111018" if T["BG"] == "#1C1B22" else "#EFEFF4", outline="")
        self.create_oval(cx - r, cy - r, cx + r, cy + r, fill=self.szin, outline="#8888AA", width=2)
        self.create_text(cx, cy, text=(self.megjeleno_nev[0].upper() if self.megjeleno_nev else "?"),
                         font=("Segoe UI", int(r * 0.80), "bold"), fill="#FFFFFF")

    def _esemenyek_kotese(self):
        self.bind("<ButtonPress-1>", self._drag_start)
        self.bind("<B1-Motion>", self._drag_motion)
        self.bind("<ButtonRelease-1>", self._drag_release)
        self.bind("<Enter>", lambda e: self._set_hover(True))
        self.bind("<Leave>", lambda e: self._set_hover(False))
        for btn in ["szin_btn", "nev_btn", "kep_btn"]:
            self.tag_bind(btn, "<Enter>", lambda e, b=btn: self.itemconfig(b, fill=T["ACCENT"]))
            self.tag_bind(btn, "<Leave>", lambda e, b=btn: self.itemconfig(b, fill=T["TEXT_SEC"]))

    def _set_hover(self, state):
        self._hover = state
        self._rajzol()

    def _drag_start(self, event):
        for tag in ["szin_btn", "nev_btn", "kep_btn"]:
            items = self.find_withtag(tag)
            for item in items:
                bbox = self.bbox(item)
                if bbox and bbox[0] <= event.x <= bbox[2] and bbox[1] <= event.y <= bbox[3]:
                    self._gomb_kattintas(tag)
                    self._is_dragging = False
                    return
        self.start_x_root, self.start_y_root = event.x_root, event.y_root
        self.start_place_x, self.start_place_y = self.winfo_x(), self.winfo_y()
        self.tk.call('raise', self._w)  # <-- A KÖZVETLEN TCL HÍVÁS, AMI JAVÍTJA A HIBÁT
        self._is_dragging = False

    def _drag_motion(self, event):
        if not hasattr(self, 'start_x_root'): return
        dx, dy = event.x_root - self.start_x_root, event.y_root - self.start_y_root
        if abs(dx) > 5 or abs(dy) > 5: self._is_dragging = True
        if self._is_dragging:
            self.place(x=self.start_place_x + dx, y=self.start_place_y + dy)

    def _drag_release(self, event):
        if not hasattr(self, 'start_x_root'): return
        if not self._is_dragging:
            self.cb['select'](self.eredeti_nev)
        else:
            self._is_dragging = False
            self.cb['drop'](self.eredeti_nev, self.winfo_x() + (CARD_W // 2), self.winfo_y() + (CARD_H // 2))

    def _gomb_kattintas(self, tag):
        if tag == "szin_btn":
            szin = colorchooser.askcolor(color=self.szin, title=f"Color – {self.megjeleno_nev}", parent=self)
            if szin and szin[1]:
                self.szin = szin[1]
                self.cb['color_change'](self.eredeti_nev, self.szin)
                self._rajzol()
        elif tag == "nev_btn":
            self.cb['rename'](self)
        elif tag == "kep_btn":
            if not PIL_AVAILABLE:
                messagebox.showinfo("Error", "Image support requires Pillow: pip install pillow")
                return
            f = filedialog.askopenfilename(title="Choose image", filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp")])
            if f:
                self.kep_utvonal = f
                self.cb['image_change'](self.eredeti_nev, f)
                self._rajzol()


# ---------------------------------------------------------------------------
# Főablak
# ---------------------------------------------------------------------------

class FoAblak(tk.Tk):
    def __init__(self):
        super().__init__()

        self.config_data = betolt_config()
        for k in ["colors", "custom_names", "custom_images"]:
            if k not in self.config_data: self.config_data[k] = {}

        self.cols = self.config_data.get("cols", 4)
        self.rows = self.config_data.get("rows", 3)

        self.profilok = betolt_profilok()
        if not self.profilok:
            messagebox.showwarning("Warning", "No Firefox profiles found.")
            sys.exit(0)

        # Rács biztonsági ellenőrzése (ne lehessen kevesebb hely, mint ahány profil van)
        while self.cols * self.rows < len(self.profilok):
            self.rows += 1

        self._init_grid_order()

        self.kartyak = {}
        self.withdraw()
        self.title("Firefox Profile Manager")
        self.configure(bg=T["BG"])
        self.resizable(False, False)

        if getattr(sys, 'frozen', False):
            ico_path = os.path.join(sys._MEIPASS, "firefox_profile.ico")
        else:
            ico_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "firefox_profile.ico")
        if os.path.exists(ico_path):
            try:
                self.iconbitmap(ico_path)
            except:
                pass

        # Fő háttér vászon a helyőrzőknek
        self.bg_canvas = tk.Canvas(self, bg=T["BG"], highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)

        self._epites()
        self._ablak_meretez()
        self.deiconify()

    def _init_grid_order(self):
        """
        Inicializálja a rács-elrendezést.
        Szabályok:
          - Ami korábban el volt mentve, pontosan oda kerül vissza, ahol volt.
          - Ami megszűnt (törölt profil), a helye None marad – semmi más nem csúszik.
          - Ami új (még nem volt elmentve), az első szabad helyre kerül (balról jobbra, felülről lefelé).
          - Semmi sem rendeződik automatikusan a sor elejére.
        """
        elmentett = self.config_data.get("grid_order", [])
        uj_order = [None] * (self.cols * self.rows)

        lehelyezett = set()

        # 1. Visszarakjuk az elmentett profilokat az eredeti pozíciójukba
        #    (csak ha a profil még létezik és a pozíció belefér az új rácsba)
        for i, p in enumerate(elmentett):
            if p is not None and p in self.profilok and i < len(uj_order):
                uj_order[i] = p
                lehelyezett.add(p)

        # 2. Új profilok (amiket az előző mentés óta hoztak létre):
        #    az első szabad helyre kerülnek, balról jobbra, felülről lefelre.
        for p in self.profilok.keys():
            if p not in lehelyezett:
                try:
                    ures_idx = uj_order.index(None)
                    uj_order[ures_idx] = p
                except ValueError:
                    pass  # Nincs több szabad hely (a biztonsági ellenőrzés miatt nem fordulhat elő)

        self.grid_order = uj_order

    def _ablak_meretez(self):
        w = 2 * OUTER_PAD + self.cols * CARD_W + (self.cols - 1) * GAP
        h = HEADER_H + self.rows * CARD_H + (self.rows - 1) * GAP + FOOTER_H
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")
        self._hatter_rajzolas()
        self._kartya_elrendezes()

    def _epites(self):
        self.fejlec = tk.Frame(self, bg=T["BG"])
        self.fejlec.place(x=OUTER_PAD, y=40, width=1500)  # Széles keret a tartalomnak

        tk.Label(self.fejlec, text="Firefox Profile Manager", font=("Segoe UI", 28, "bold"), fg=T["TEXT"],
                 bg=T["BG"]).pack(side="left")

        tk.Label(self.fejlec, text="Columns:", font=("Segoe UI", 11), fg=T["TEXT_SEC"], bg=T["BG"]).pack(side="left",
                                                                                                          padx=(30, 5))
        self.spin_col = tk.Spinbox(self.fejlec, from_=1, to=20, width=3, font=("Segoe UI", 11), bg=T["CARD"],
                                   fg=T["TEXT"], buttonbackground=T["BORDER"], command=self._meret_valtozas)
        self.spin_col.pack(side="left")
        self.spin_col.delete(0, 'end')
        self.spin_col.insert(0, str(self.cols))

        tk.Label(self.fejlec, text="Rows:", font=("Segoe UI", 11), fg=T["TEXT_SEC"], bg=T["BG"]).pack(side="left",
                                                                                                       padx=(20, 5))
        self.spin_row = tk.Spinbox(self.fejlec, from_=1, to=20, width=3, font=("Segoe UI", 11), bg=T["CARD"],
                                   fg=T["TEXT"], buttonbackground=T["BORDER"], command=self._meret_valtozas)
        self.spin_row.pack(side="left")
        self.spin_row.delete(0, 'end')
        self.spin_row.insert(0, str(self.rows))

        callbacks = {'select': self._profil_indit, 'color_change': self._szin_valtozas, 'rename': self._nev_valtozas,
                     'image_change': self._kep_valtozas, 'drop': self._profil_ejejtve}
        for p in self.profilok.keys():
            idx = list(self.profilok.keys()).index(p)
            szin = self.config_data["colors"].get(p, DEFAULT_COLORS[idx % len(DEFAULT_COLORS)])
            kartya = ProfilKartya(self, eredeti_nev=p, megjeleno_nev=self.config_data["custom_names"].get(p, p),
                                  szin=szin, kep_utvonal=self.config_data["custom_images"].get(p, None),
                                  callbacks=callbacks)
            self.kartyak[p] = kartya

    def _meret_valtozas(self):
        try:
            uj_cols = int(self.spin_col.get())
            uj_rows = int(self.spin_row.get())
        except ValueError:
            return

        if uj_cols * uj_rows < len(self.profilok):
            messagebox.showwarning("Grid too small", "Not enough cells for all profiles!")
            self.spin_col.delete(0, 'end');
            self.spin_col.insert(0, str(self.cols))
            self.spin_row.delete(0, 'end');
            self.spin_row.insert(0, str(self.rows))
            return

        # Ha változott, próbáljuk megtartani a régi 2D koordinátákat
        uj_order = [None] * (uj_cols * uj_rows)
        leesettek = []
        for i, p in enumerate(self.grid_order):
            if p is None: continue
            c, r = i % self.cols, i // self.cols
            if c < uj_cols and r < uj_rows:
                uj_order[r * uj_cols + c] = p
            else:
                leesettek.append(p)

        # Leesett profilok: jobbra csúszás az utolsó elem után,
        # sorvég után az alatta lévő sor bal oldala következik.
        # Mindig az első szabad helyre kerülnek, balról jobbra, felülről lefelé.
        for p in leesettek:
            try:
                idx = uj_order.index(None)
                uj_order[idx] = p
            except ValueError:
                pass  # Nem férne el (biztonsági fallback, a korábbi ellenőrzés miatt nem fordulhat elő)

        self.cols, self.rows = uj_cols, uj_rows
        self.grid_order = uj_order
        self.config_data["cols"], self.config_data["rows"] = uj_cols, uj_rows
        self._mentes()

        self.fejlec.place_configure(width=self.cols * CARD_W + (self.cols - 1) * GAP)
        self._ablak_meretez()

    def _hatter_rajzolas(self):
        self.bg_canvas.delete("all")
        # Elválasztó vonal
        fw = self.cols * CARD_W + (self.cols - 1) * GAP
        self.bg_canvas.create_line(OUTER_PAD, 85, OUTER_PAD + fw, 85, fill=T["BORDER"])

        # Helyőrzők rajzolása
        for r in range(self.rows):
            for c in range(self.cols):
                x = OUTER_PAD + c * (CARD_W + GAP)
                y = HEADER_H + r * (CARD_H + GAP)
                rounded_rect(self.bg_canvas, x, y, x + CARD_W, y + CARD_H, CORNER_R, fill=T["PLACEHOLDER"])

    def _kartya_elrendezes(self):
        for i, p in enumerate(self.grid_order):
            if p is None: continue
            col, row = i % self.cols, i // self.cols
            x = OUTER_PAD + col * (CARD_W + GAP)
            y = HEADER_H + row * (CARD_H + GAP)
            self.kartyak[p].place(x=x, y=y, width=CARD_W, height=CARD_H)
            self.kartyak[p].tk.call('raise', self.kartyak[p]._w)

    def _profil_ejejtve(self, nev, cx, cy):
        rel_x, rel_y = cx - OUTER_PAD, cy - HEADER_H
        col = max(0, min(self.cols - 1, int((rel_x + GAP / 2) // (CARD_W + GAP))))
        row = max(0, min(self.rows - 1, int((rel_y + GAP / 2) // (CARD_H + GAP))))

        tgt_idx = row * self.cols + col
        src_idx = self.grid_order.index(nev)

        if src_idx == tgt_idx:
            self._kartya_elrendezes()
            return

        total = self.cols * self.rows
        order = list(self.grid_order)

        # 1. Forrás pozíció felszabadítása
        order[src_idx] = None

        # 2. Ha a cél foglalt: jobbra csúsztatás lánc, amíg üres helyet nem találunk.
        #    Sorvégen a következő sor elejére lép (lineáris index, körkörös a rácson belül).
        if order[tgt_idx] is not None:
            ures_idx = None
            for offset in range(1, total):
                idx = (tgt_idx + offset) % total
                if order[idx] is None:
                    ures_idx = idx
                    break

            if ures_idx is not None:
                # Mindenki tgt_idx+1..ures_idx közt eggyel jobbra csúszik
                idx = ures_idx
                while idx != tgt_idx:
                    prev = (idx - 1) % total
                    order[idx] = order[prev]
                    idx = prev
                order[tgt_idx] = None  # hely felszabadult a húzott kártyának

        # 3. Húzott kártya a célra kerül
        order[tgt_idx] = nev

        self.grid_order = order
        self._mentes()
        self._kartya_elrendezes()

    def _mentes(self):
        self.config_data["grid_order"] = self.grid_order
        ment_config(self.config_data)

    def _profil_indit(self, eredeti_nev):
        if indit_firefox(self.profilok.get(eredeti_nev)): self.destroy()

    def _szin_valtozas(self, nev, szin):
        self.config_data["colors"][nev] = szin
        self._mentes()

    def _kep_valtozas(self, nev, utvonal):
        self.config_data["custom_images"][nev] = utvonal
        self._mentes()

    def _nev_valtozas(self, kartya):
        uj = simpledialog.askstring("Rename", "New name:", initialvalue=kartya.megjeleno_nev, parent=self)
        if uj is not None:
            uj = uj.strip()
            if uj == "":
                if kartya.eredeti_nev in self.config_data["custom_names"]: del self.config_data["custom_names"][
                    kartya.eredeti_nev]
                kartya.megjeleno_nev = kartya.eredeti_nev
            else:
                self.config_data["custom_names"][kartya.eredeti_nev] = uj
                kartya.megjeleno_nev = uj
            self._mentes()
            kartya._rajzol()


if __name__ == "__main__":
    if os.name == 'nt':
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('custom.firefox.profilemanager.1')
        except:
            pass
    app = FoAblak()
    app.mainloop()