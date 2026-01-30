"""
Programa interactivo: Historia y evolución de la graficación por computadora
Con síntesis de voz (Text-to-Speech) y mejoras visuales
Autor: Sistema Mejorado
Descripción:
 - Interfaz Tkinter con línea del tiempo por décadas
 - Filtros por década, búsqueda, navegación
 - Exportación a CSV/JSON
 - Cuestionario (8 preguntas) con puntaje
 - NUEVO: Síntesis de voz para leer el contenido
 - NUEVO: Colores mejorados y diseño moderno
 - Opcional: carga de imágenes locales si existe Pillow (PIL) y archivos en ./assets/
"""
import json
import csv
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading

# Intento opcional de cargar Pillow para imágenes
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

# Intento de cargar pyttsx3 para síntesis de voz
try:
    import pyttsx3
    TTS_AVAILABLE = True
except Exception:
    TTS_AVAILABLE = False
    print("⚠️ pyttsx3 no disponible. Instala con: pip install pyttsx3")

# ---------------------------
# Paleta de colores moderna
# ---------------------------
COLORS = {
    'primary': '#2563eb',        # Azul vibrante
    'primary_dark': '#1e40af',   # Azul oscuro
    'primary_light': '#60a5fa',  # Azul claro
    'success': '#10b981',        # Verde
    'warning': '#f59e0b',        # Naranja
    'danger': '#ef4444',         # Rojo
    'info': '#06b6d4',           # Cyan
    'bg_main': '#f8fafc',        # Gris muy claro
    'bg_card': '#ffffff',        # Blanco
    'bg_hover': '#e0f2fe',       # Azul muy claro
    'text_primary': '#1e293b',   # Gris oscuro
    'text_secondary': '#64748b', # Gris medio
    'border': '#cbd5e1',         # Borde gris claro
    'accent': '#8b5cf6',         # Morado
}

# ---------------------------
# Datos de la línea del tiempo
# ---------------------------
MILESTONES = [
    (1950, "Pantallas CRT en investigación",
     "Uso de tubos de rayos catódicos (CRT) en radares y simuladores; base para visualización electrónica.",
     ["CRT", "visualización", "radares"], "crt.png"),
    
    (1957, "Primera imagen digitalizada (Kirsch)",
     "Russell Kirsch digitaliza una fotografía con la computadora SEAC; inicio de la imagen digital.",
     ["imagen digital", "SEAC", "Kirsch"], "kirsch.png"),
    
    (1963, "Sketchpad (Ivan Sutherland)",
     "Sistema pionero CAD con lápiz óptico: selección, arrastre, zoom y estructuras jerárquicas de objetos.",
     ["CAD", "Sketchpad", "interacción"], "sketchpad.png"),
    
    (1968, "Mother of All Demos (Engelbart)",
     "Presentación de NLS: mouse, ventanas, hipervínculos, edición y colaboración; clave para interfaces gráficas.",
     ["GUI", "NLS", "interfaz"], "nls.png"),
    
    (1972, "Pong",
     "Uno de los primeros videojuegos comerciales; impulso a gráficos interactivos en tiempo real.",
     ["videojuegos", "Atari"], "pong.png"),
    
    (1973, "SuperPaint",
     "Primeros sistemas con frame buffer en color; edición y pintura digital temprana.",
     ["raster", "framebuffer"], "superpaint.png"),
    
    (1984, "GUI en computadoras personales",
     "Popularización de entornos gráficos (Macintosh) y posterior adopción masiva (Windows).",
     ["GUI", "Mac", "Windows"], "gui80s.png"),
    
    (1992, "OpenGL",
     "API estándar multiplataforma para gráficos 2D/3D; cataliza gráficos interactivos y científicos.",
     ["OpenGL", "API", "3D"], "opengl.png"),
    
    (1995, "Toy Story",
     "Primer largometraje completamente por animación 3D; hito de la industria CGI.",
     ["cine", "CGI", "Pixar"], "toystory.png"),
    
    (1999, "GPUs y sombreadores programables",
     "Las GPUs dan salto a programabilidad (shaders); rendimiento masivo en gráficos 3D.",
     ["GPU", "shaders"], "gpu99.png"),
    
    (2006, "Programación de shaders consolidada",
     "Sombreadores de vértice/píxel/geom. ampliamente usados en videojuegos y visualización.",
     ["shaders", "programable"], "shaders.png"),
    
    (2018, "Ray tracing en tiempo real",
     "Soporte de hardware para trazado de rayos en tiempo real (línea RTX); realismo de iluminación.",
     ["ray tracing", "RTX"], "rtx.png"),
    
    (2020, "VR/AR y altas resoluciones",
     "Aplicaciones inmersivas, 4K/8K, simulaciones complejas y uso transversal en ciencia, medicina y educación.",
     ["VR", "AR", "4K/8K"], "vrar.png"),
]

# ---------------------------
# Preguntas del cuestionario
# ---------------------------
QUIZ = [
    {
        "q": "¿Quién desarrolló Sketchpad, considerado pionero del CAD interactivo?",
        "options": ["Ivan Sutherland", "Douglas Engelbart", "John Whitney", "Alan Kay"],
        "answer": 0
    },
    {
        "q": "¿Qué hito permitió iluminación más realista en tiempo real a partir de 2018?",
        "options": ["Mapeado de normales", "Ray tracing con soporte de hardware", "Phong shading", "Wireframe puro"],
        "answer": 1
    },
    {
        "q": "¿Cuál fue uno de los primeros videojuegos comerciales que impulsó los gráficos interactivos?",
        "options": ["Spacewar!", "Pong", "Breakout", "Doom"],
        "answer": 1
    },
    {
        "q": "OpenGL (1992) es principalmente...",
        "options": ["Un sistema operativo", "Un lenguaje de shading propietario",
                    "Una API estándar para gráficos", "Un formato de imagen"],
        "answer": 2
    },
    {
        "q": "La 'Mother of All Demos' (1968) mostró:",
        "options": ["Pantallas táctiles capacitivas", "Mouse, ventanas e hipervínculos",
                    "Headsets de VR comerciales", "Smartphones"],
        "answer": 1
    },
    {
        "q": "Toy Story (1995) es relevante porque:",
        "options": ["Fue la primera película en 3D estereoscópico",
                    "Fue el primer largometraje totalmente hecho con animación 3D",
                    "Usó por primera vez GPUs programables",
                    "Se dibujó a mano y luego se digitalizó"],
        "answer": 1
    },
    {
        "q": "Las GPUs programables popularizaron el uso de:",
        "options": ["Shaders", "Disquetes", "Microfilms", "Tubos de vacío"],
        "answer": 0
    },
    {
        "q": "SuperPaint aportó tempranamente:",
        "options": ["Ray tracing en tiempo real", "Render de path tracing",
                    "Frame buffer en color y pintura digital", "Pantallas OLED"],
        "answer": 2
    },
]


def decade_label(year: int) -> str:
    d = (year // 10) * 10
    return f"{d}s"


# ---------------------------
# Motor de Text-to-Speech
# ---------------------------
class TTSEngine:
    """Motor de síntesis de voz"""
    
    def __init__(self):
        self.engine = None
        self.is_speaking = False
        self.current_thread = None
        
        if TTS_AVAILABLE:
            try:
                self.engine = pyttsx3.init()
                # Configuración de voz
                self.engine.setProperty('rate', 150)     # Velocidad (palabras por minuto)
                self.engine.setProperty('volume', 0.9)   # Volumen (0.0 a 1.0)
                
                # Intentar establecer voz en español si está disponible
                voices = self.engine.getProperty('voices')
                for voice in voices:
                    if 'spanish' in voice.name.lower() or 'spanish' in voice.languages[0].lower():
                        self.engine.setProperty('voice', voice.id)
                        break
            except Exception as e:
                print(f"Error inicializando TTS: {e}")
                self.engine = None
    
    def speak(self, text, callback=None):
        """Habla el texto en un thread separado"""
        if not self.engine:
            return
        
        # Detener cualquier speech anterior
        self.stop()
        
        def _speak():
            try:
                self.is_speaking = True
                self.engine.say(text)
                self.engine.runAndWait()
                self.is_speaking = False
                if callback:
                    callback()
            except Exception as e:
                print(f"Error en TTS: {e}")
                self.is_speaking = False
        
        self.current_thread = threading.Thread(target=_speak, daemon=True)
        self.current_thread.start()
    
    def stop(self):
        """Detiene el speech actual"""
        if self.engine and self.is_speaking:
            try:
                self.engine.stop()
                self.is_speaking = False
            except:
                pass
    
    def is_available(self):
        """Retorna si TTS está disponible"""
        return self.engine is not None


class TimelineApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("📚 Historia y evolución de la graficación por computadora")
        self.geometry("1200x750")
        self.minsize(1100, 700)
        
        # Configurar color de fondo principal
        self.configure(bg=COLORS['bg_main'])

        # Motor TTS
        self.tts = TTSEngine()

        # Estado
        self.filtered = list(MILESTONES)
        self.current_index = 0
        self.current_decade = None

        # Estilos visuales modernos
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except:
            pass
        
        # Configurar estilos personalizados
        self.configure_styles()
        
        self.create_widgets()
        self.populate_decades()
        self.refresh_list()
        self.show_item(0)

    def configure_styles(self):
        """Configura estilos visuales modernos"""
        # Labels
        self.style.configure("Title.TLabel", 
                           font=("Segoe UI", 22, "bold"), 
                           foreground=COLORS['primary'],
                           background=COLORS['bg_card'])
        
        self.style.configure("H2.TLabel", 
                           font=("Segoe UI", 14, "bold"), 
                           foreground=COLORS['primary_dark'],
                           background=COLORS['bg_card'])
        
        self.style.configure("Body.TLabel", 
                           font=("Segoe UI", 12),
                           background=COLORS['bg_card'])
        
        self.style.configure("Tag.TLabel", 
                           font=("Segoe UI", 10), 
                           foreground=COLORS['text_secondary'],
                           background=COLORS['bg_card'])
        
        # Frames
        self.style.configure("Card.TFrame", 
                           background=COLORS['bg_card'],
                           relief="flat")
        
        self.style.configure("Sidebar.TFrame",
                           background=COLORS['bg_main'])
        
        # Botones
        self.style.configure("Primary.TButton",
                           font=("Segoe UI", 10, "bold"),
                           foreground=COLORS['bg_card'],
                           background=COLORS['primary'])
        
        self.style.map("Primary.TButton",
                      background=[('active', COLORS['primary_dark'])])
        
        self.style.configure("Success.TButton",
                           font=("Segoe UI", 10),
                           background=COLORS['success'])
        
        self.style.configure("Warning.TButton",
                           font=("Segoe UI", 10),
                           background=COLORS['warning'])
        
        self.style.configure("TTS.TButton",
                           font=("Segoe UI", 10, "bold"),
                           background=COLORS['accent'])

    def create_widgets(self):
        # Layout principal: izquierda (filtros/lista) | derecha (detalle)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # Panel izquierdo (sidebar)
        left = ttk.Frame(self, padding=15, style="Sidebar.TFrame")
        left.grid(row=0, column=0, sticky="nsw")
        left.grid_rowconfigure(7, weight=1)

        # Panel derecho (contenido principal)
        right = ttk.Frame(self, padding=15, style="Card.TFrame")
        right.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(3, weight=1)

        # --- PANEL IZQUIERDO (Filtros, búsqueda, lista) ---
        
        # Título sidebar
        sidebar_title = tk.Label(left, 
                                 text="🎨 Línea del Tiempo",
                                 font=("Segoe UI", 16, "bold"),
                                 fg=COLORS['primary'],
                                 bg=COLORS['bg_main'])
        sidebar_title.grid(row=0, column=0, sticky="w", pady=(0, 20))
        
        # Sección Filtros
        filter_label = tk.Label(left,
                               text="📊 Filtros",
                               font=("Segoe UI", 12, "bold"),
                               fg=COLORS['text_primary'],
                               bg=COLORS['bg_main'])
        filter_label.grid(row=1, column=0, sticky="w", pady=(0, 8))
        
        self.decade_var = tk.StringVar(value="Todas las décadas")
        self.decade_menu = ttk.OptionMenu(left, self.decade_var, "Todas las décadas", 
                                         command=self.on_decade_change)
        self.decade_menu.grid(row=2, column=0, sticky="ew", pady=(0, 15))

        # Sección Búsqueda
        search_label = tk.Label(left,
                               text="🔍 Búsqueda",
                               font=("Segoe UI", 12, "bold"),
                               fg=COLORS['text_primary'],
                               bg=COLORS['bg_main'])
        search_label.grid(row=3, column=0, sticky="w", pady=(0, 8))
        
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(left, textvariable=self.search_var, font=("Segoe UI", 11))
        self.search_entry.grid(row=4, column=0, sticky="ew", pady=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.on_search)

        clear_btn = ttk.Button(left, text="🔄 Limpiar filtros", command=self.clear_filters)
        clear_btn.grid(row=5, column=0, sticky="ew", pady=(0, 20))

        # Lista de eventos
        list_label = tk.Label(left,
                             text="📋 Eventos",
                             font=("Segoe UI", 12, "bold"),
                             fg=COLORS['text_primary'],
                             bg=COLORS['bg_main'])
        list_label.grid(row=6, column=0, sticky="w", pady=(0, 8))
        
        # Frame para listbox con scrollbar
        list_frame = tk.Frame(left, bg=COLORS['bg_main'])
        list_frame.grid(row=7, column=0, sticky="nsew")
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.listbox = tk.Listbox(list_frame, 
                                  activestyle="none",
                                  height=20, 
                                  font=("Segoe UI", 11),
                                  bg=COLORS['bg_card'],
                                  fg=COLORS['text_primary'],
                                  selectbackground=COLORS['primary_light'],
                                  selectforeground=COLORS['bg_card'],
                                  borderwidth=1,
                                  relief="solid",
                                  highlightthickness=0,
                                  yscrollcommand=scrollbar.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)
        
        self.listbox.bind("<<ListboxSelect>>", self.on_list_select)

        # --- PANEL DERECHO (Detalle del contenido) ---
        
        # Título principal
        self.title_lbl = tk.Label(right, 
                                  text="Título", 
                                  font=("Segoe UI", 24, "bold"),
                                  fg=COLORS['primary'],
                                  bg=COLORS['bg_card'],
                                  wraplength=900,
                                  justify="left")
        self.title_lbl.grid(row=0, column=0, sticky="w", pady=(0, 10))

        # Metadatos (año, década, etiquetas)
        self.meta_lbl = tk.Label(right,
                                text="",
                                font=("Segoe UI", 10),
                                fg=COLORS['text_secondary'],
                                bg=COLORS['bg_card'])
        self.meta_lbl.grid(row=1, column=0, sticky="w", pady=(0, 15))

        # Panel de imagen
        self.image_panel = tk.Label(right, bg=COLORS['bg_card'])
        self.image_panel.grid(row=2, column=0, sticky="w", pady=(0, 15))

        # Texto descriptivo con scrollbar
        text_frame = tk.Frame(right, bg=COLORS['bg_card'])
        text_frame.grid(row=3, column=0, sticky="nsew")
        text_frame.grid_columnconfigure(0, weight=1)
        text_frame.grid_rowconfigure(0, weight=1)
        
        text_scrollbar = tk.Scrollbar(text_frame)
        text_scrollbar.pack(side="right", fill="y")
        
        self.body_text = tk.Text(text_frame, 
                                wrap="word", 
                                height=10, 
                                font=("Segoe UI", 12),
                                bg=COLORS['bg_card'],
                                fg=COLORS['text_primary'],
                                borderwidth=1,
                                relief="solid",
                                padx=15,
                                pady=10,
                                yscrollcommand=text_scrollbar.set)
        self.body_text.pack(side="left", fill="both", expand=True)
        text_scrollbar.config(command=self.body_text.yview)
        self.body_text.configure(state="disabled")

        # Botones de control de voz
        tts_frame = tk.Frame(right, bg=COLORS['bg_card'])
        tts_frame.grid(row=4, column=0, sticky="ew", pady=(15, 10))
        tts_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        if self.tts.is_available():
            self.speak_btn = tk.Button(tts_frame,
                                      text="🔊 Leer en voz alta",
                                      font=("Segoe UI", 11, "bold"),
                                      bg=COLORS['accent'],
                                      fg=COLORS['bg_card'],
                                      activebackground=COLORS['primary_dark'],
                                      activeforeground=COLORS['bg_card'],
                                      relief="flat",
                                      padx=20,
                                      pady=10,
                                      cursor="hand2",
                                      command=self.speak_current)
            self.speak_btn.grid(row=0, column=0, sticky="ew", padx=2)
            
            self.stop_btn = tk.Button(tts_frame,
                                     text="⏸️ Detener voz",
                                     font=("Segoe UI", 11),
                                     bg=COLORS['warning'],
                                     fg=COLORS['bg_card'],
                                     activebackground=COLORS['danger'],
                                     activeforeground=COLORS['bg_card'],
                                     relief="flat",
                                     padx=20,
                                     pady=10,
                                     cursor="hand2",
                                     command=self.stop_speech)
            self.stop_btn.grid(row=0, column=1, sticky="ew", padx=2)
            
            # Label de estado
            self.tts_status = tk.Label(tts_frame,
                                      text="",
                                      font=("Segoe UI", 9, "italic"),
                                      fg=COLORS['text_secondary'],
                                      bg=COLORS['bg_card'])
            self.tts_status.grid(row=0, column=2, sticky="w", padx=10)
        else:
            no_tts_label = tk.Label(tts_frame,
                                   text="⚠️ Síntesis de voz no disponible (instala pyttsx3)",
                                   font=("Segoe UI", 10, "italic"),
                                   fg=COLORS['warning'],
                                   bg=COLORS['bg_card'])
            no_tts_label.grid(row=0, column=0, columnspan=3)

        # Navegación y exportación
        nav = tk.Frame(right, bg=COLORS['bg_card'])
        nav.grid(row=5, column=0, sticky="ew", pady=(10, 0))
        nav.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        prev_btn = tk.Button(nav,
                            text="⬅️ Anterior",
                            font=("Segoe UI", 11),
                            bg=COLORS['primary'],
                            fg=COLORS['bg_card'],
                            activebackground=COLORS['primary_dark'],
                            activeforeground=COLORS['bg_card'],
                            relief="flat",
                            padx=15,
                            pady=8,
                            cursor="hand2",
                            command=self.prev_item)
        prev_btn.grid(row=0, column=0, sticky="ew", padx=2)
        
        next_btn = tk.Button(nav,
                            text="Siguiente ➡️",
                            font=("Segoe UI", 11),
                            bg=COLORS['primary'],
                            fg=COLORS['bg_card'],
                            activebackground=COLORS['primary_dark'],
                            activeforeground=COLORS['bg_card'],
                            relief="flat",
                            padx=15,
                            pady=8,
                            cursor="hand2",
                            command=self.next_item)
        next_btn.grid(row=0, column=1, sticky="ew", padx=2)
        
        csv_btn = tk.Button(nav,
                           text="📄 CSV",
                           font=("Segoe UI", 11),
                           bg=COLORS['success'],
                           fg=COLORS['bg_card'],
                           activebackground=COLORS['info'],
                           activeforeground=COLORS['bg_card'],
                           relief="flat",
                           padx=15,
                           pady=8,
                           cursor="hand2",
                           command=self.export_csv)
        csv_btn.grid(row=0, column=2, sticky="ew", padx=2)
        
        json_btn = tk.Button(nav,
                            text="📋 JSON",
                            font=("Segoe UI", 11),
                            bg=COLORS['success'],
                            fg=COLORS['bg_card'],
                            activebackground=COLORS['info'],
                            activeforeground=COLORS['bg_card'],
                            relief="flat",
                            padx=15,
                            pady=8,
                            cursor="hand2",
                            command=self.export_json)
        json_btn.grid(row=0, column=3, sticky="ew", padx=2)

        # Botón de cuestionario (parte inferior)
        bottom = tk.Frame(self, bg=COLORS['bg_main'], pady=15)
        bottom.grid(row=1, column=0, columnspan=2, sticky="ew", padx=15)
        bottom.grid_columnconfigure(0, weight=1)
        
        quiz_btn = tk.Button(bottom,
                            text="📝 Iniciar cuestionario (8 preguntas)",
                            font=("Segoe UI", 12, "bold"),
                            bg=COLORS['accent'],
                            fg=COLORS['bg_card'],
                            activebackground=COLORS['primary_dark'],
                            activeforeground=COLORS['bg_card'],
                            relief="flat",
                            padx=30,
                            pady=12,
                            cursor="hand2",
                            command=self.start_quiz)
        quiz_btn.pack(side="right")

    def populate_decades(self):
        decades = sorted({decade_label(y) for (y, *_rest) in MILESTONES})
        menu = self.decade_menu["menu"]
        menu.delete(0, "end")
        menu.add_command(label="Todas las décadas",
                        command=lambda v="Todas las décadas": self.decade_var.set(v) or self.on_decade_change(v))
        for d in decades:
            menu.add_command(label=d, command=lambda v=d: self.decade_var.set(v) or self.on_decade_change(v))

    def on_decade_change(self, *_):
        dec = self.decade_var.get()
        self.current_decade = None if dec == "Todas las décadas" else dec
        self.apply_filters()

    def on_search(self, *_):
        self.apply_filters()

    def clear_filters(self):
        self.current_decade = None
        self.decade_var.set("Todas las décadas")
        self.search_var.set("")
        self.apply_filters()

    def apply_filters(self):
        query = self.search_var.get().strip().lower()
        dec = self.current_decade

        def match(item):
            y, title, desc, tags, _img = item
            if dec and decade_label(y) != dec:
                return False
            if not query:
                return True
            blob = " ".join([
                str(y), title.lower(), desc.lower(), " ".join(t.lower() for t in tags)
            ])
            return query in blob

        self.filtered = [m for m in MILESTONES if match(m)]
        self.refresh_list()
        if self.filtered:
            self.show_item(0)

    def refresh_list(self):
        self.listbox.delete(0, "end")
        for y, title, *_ in self.filtered:
            self.listbox.insert("end", f"{y} — {title}")

    def on_list_select(self, *_):
        idx = self.listbox.curselection()
        if not idx:
            return
        self.current_index = idx[0]
        self.show_item(self.current_index)

    def show_item(self, idx: int):
        # Detener cualquier lectura en curso
        self.tts.stop()
        if hasattr(self, 'tts_status'):
            self.tts_status.config(text="")
        
        if not self.filtered:
            self.title_lbl.config(text="Sin resultados")
            self.meta_lbl.config(text="")
            self.set_body("")
            self.set_image(None)
            return

        idx = max(0, min(idx, len(self.filtered) - 1))
        self.current_index = idx
        y, title, desc, tags, img_name = self.filtered[idx]
        
        self.title_lbl.config(text=f"{title}")
        self.meta_lbl.config(text=f"📅 Año: {y} • 📊 Década: {decade_label(y)} • 🏷️ Etiquetas: {', '.join(tags)}")
        self.set_body(desc)

        # Imagen opcional
        img_path = os.path.join("assets", img_name) if img_name else None
        if PIL_AVAILABLE and img_name and os.path.exists(img_path):
            try:
                im = Image.open(img_path)
                im.thumbnail((900, 400))
                self._photo = ImageTk.PhotoImage(im)
                self.set_image(self._photo)
            except Exception:
                self.set_image(None)
        else:
            self.set_image(None)

        # Selección en la lista
        try:
            self.listbox.selection_clear(0, "end")
            self.listbox.selection_set(self.current_index)
            self.listbox.see(self.current_index)
        except Exception:
            pass

    def set_body(self, text: str):
        self.body_text.configure(state="normal")
        self.body_text.delete("1.0", "end")
        self.body_text.insert("1.0", text)
        self.body_text.configure(state="disabled")

    def set_image(self, photo_or_none):
        if photo_or_none:
            self.image_panel.configure(image=photo_or_none, text="")
            self.image_panel.image = photo_or_none
        else:
            self.image_panel.configure(image="", text="")
            self.image_panel.image = None

    def speak_current(self):
        """Lee el contenido actual en voz alta"""
        if not self.filtered or not self.tts.is_available():
            return
        
        y, title, desc, tags, _img = self.filtered[self.current_index]
        
        # Construir texto completo para leer
        text_to_speak = f"{title}. Año {y}. {desc}"
        
        # Actualizar estado
        if hasattr(self, 'tts_status'):
            self.tts_status.config(text="🔊 Leyendo...", fg=COLORS['success'])
        
        # Callback cuando termine de hablar
        def on_finish():
            if hasattr(self, 'tts_status'):
                self.tts_status.config(text="✅ Lectura completada", fg=COLORS['info'])
        
        # Iniciar lectura
        self.tts.speak(text_to_speak, callback=on_finish)
    
    def stop_speech(self):
        """Detiene la lectura en voz alta"""
        self.tts.stop()
        if hasattr(self, 'tts_status'):
            self.tts_status.config(text="⏸️ Detenido", fg=COLORS['warning'])

    def prev_item(self):
        if not self.filtered:
            return
        self.current_index = (self.current_index - 1) % len(self.filtered)
        self.show_item(self.current_index)

    def next_item(self):
        if not self.filtered:
            return
        self.current_index = (self.current_index + 1) % len(self.filtered)
        self.show_item(self.current_index)

    def export_csv(self):
        if not self.filtered:
            messagebox.showinfo("Exportar CSV", "No hay elementos para exportar.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            title="Guardar línea del tiempo (CSV)"
        )
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["year", "title", "description", "tags"])
            for y, title, desc, tags, _img in self.filtered:
                w.writerow([y, title, desc, ";".join(tags)])
        messagebox.showinfo("Exportar CSV", f"✅ Archivo guardado:\n{path}")

    def export_json(self):
        if not self.filtered:
            messagebox.showinfo("Exportar JSON", "No hay elementos para exportar.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
            title="Guardar línea del tiempo (JSON)"
        )
        if not path:
            return
        data = [
            {"year": y, "title": title, "description": desc, "tags": tags}
            for y, title, desc, tags, _img in self.filtered
        ]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        messagebox.showinfo("Exportar JSON", f"✅ Archivo guardado:\n{path}")

    def start_quiz(self):
        QuizWindow(self, QUIZ)


class QuizWindow(tk.Toplevel):
    def __init__(self, master: TimelineApp, questions):
        super().__init__(master)
        self.title("📝 Cuestionario: Historia de la graficación")
        self.geometry("800x650")
        self.resizable(False, False)
        self.configure(bg=COLORS['bg_card'])
        
        self.questions = list(questions)
        self.index = 0
        self.score = 0
        self.user_answers = [-1] * len(self.questions)

        # Header
        header = tk.Frame(self, bg=COLORS['primary'], height=80)
        header.pack(fill="x")
        
        header_label = tk.Label(header,
                               text="📝 Cuestionario de Evaluación",
                               font=("Segoe UI", 20, "bold"),
                               fg=COLORS['bg_card'],
                               bg=COLORS['primary'])
        header_label.pack(pady=20)

        # Contenido
        content = tk.Frame(self, bg=COLORS['bg_card'], padx=30, pady=20)
        content.pack(fill="both", expand=True)

        # Progress bar
        progress_frame = tk.Frame(content, bg=COLORS['bg_card'])
        progress_frame.pack(fill="x", pady=(0, 20))
        
        self.progress_label = tk.Label(progress_frame,
                                      text="",
                                      font=("Segoe UI", 11, "bold"),
                                      fg=COLORS['primary'],
                                      bg=COLORS['bg_card'])
        self.progress_label.pack(anchor="w")

        # Pregunta
        self.q_lbl = tk.Label(content,
                             text="",
                             font=("Segoe UI", 14, "bold"),
                             fg=COLORS['text_primary'],
                             bg=COLORS['bg_card'],
                             wraplength=720,
                             justify="left")
        self.q_lbl.pack(anchor="w", pady=(0, 20))

        # Opciones
        self.opt_var = tk.IntVar(value=-1)
        self.opts = []
        for i in range(4):
            opt_frame = tk.Frame(content, bg=COLORS['bg_hover'], relief="solid", borderwidth=1)
            opt_frame.pack(fill="x", pady=8)
            
            rb = tk.Radiobutton(opt_frame,
                               text="",
                               variable=self.opt_var,
                               value=i,
                               font=("Segoe UI", 12),
                               fg=COLORS['text_primary'],
                               bg=COLORS['bg_hover'],
                               activebackground=COLORS['bg_hover'],
                               selectcolor=COLORS['primary_light'],
                               padx=15,
                               pady=10)
            rb.pack(anchor="w", fill="x")
            self.opts.append(rb)

        # Navegación
        nav = tk.Frame(content, bg=COLORS['bg_card'])
        nav.pack(fill="x", pady=(30, 0))
        
        prev_btn = tk.Button(nav,
                            text="⬅️ Anterior",
                            font=("Segoe UI", 11),
                            bg=COLORS['primary'],
                            fg=COLORS['bg_card'],
                            activebackground=COLORS['primary_dark'],
                            relief="flat",
                            padx=20,
                            pady=10,
                            cursor="hand2",
                            command=self.prev_q)
        prev_btn.pack(side="left", padx=5)
        
        next_btn = tk.Button(nav,
                            text="Siguiente ➡️",
                            font=("Segoe UI", 11),
                            bg=COLORS['primary'],
                            fg=COLORS['bg_card'],
                            activebackground=COLORS['primary_dark'],
                            relief="flat",
                            padx=20,
                            pady=10,
                            cursor="hand2",
                            command=self.next_q)
        next_btn.pack(side="left", padx=5)
        
        finish_btn = tk.Button(nav,
                              text="✅ Finalizar",
                              font=("Segoe UI", 11, "bold"),
                              bg=COLORS['success'],
                              fg=COLORS['bg_card'],
                              activebackground=COLORS['info'],
                              relief="flat",
                              padx=20,
                              pady=10,
                              cursor="hand2",
                              command=self.finish)
        finish_btn.pack(side="right", padx=5)

        self.update_question()

    def update_question(self):
        q = self.questions[self.index]
        self.progress_label.config(text=f"Pregunta {self.index+1} de {len(self.questions)}")
        self.q_lbl.config(text=q['q'])
        self.opt_var.set(self.user_answers[self.index])
        for i, opt in enumerate(q["options"]):
            self.opts[i].config(text=opt)

    def prev_q(self):
        self.user_answers[self.index] = self.opt_var.get()
        self.index = (self.index - 1) % len(self.questions)
        self.update_question()

    def next_q(self):
        self.user_answers[self.index] = self.opt_var.get()
        self.index = (self.index + 1) % len(self.questions)
        self.update_question()

    def finish(self):
        self.user_answers[self.index] = self.opt_var.get()
        score = 0
        details = []
        for i, q in enumerate(self.questions):
            correct = q["answer"]
            user = self.user_answers[i]
            ok = (user == correct)
            if ok:
                score += 1
            emoji = "✅" if ok else "❌"
            details.append(f"{emoji} Pregunta {i+1}: {q['q']}\n"
                          f"   Tu respuesta: {q['options'][user] if user >= 0 else '(Sin responder)'}\n"
                          f"   Correcta: {q['options'][correct]}\n")
        
        pct = round(100 * score / len(self.questions), 1)
        
        # Determinar calificación
        if pct >= 90:
            grade = "¡Excelente! 🌟"
            color = "green"
        elif pct >= 70:
            grade = "¡Muy bien! 👍"
            color = "blue"
        elif pct >= 50:
            grade = "Aprobado ✓"
            color = "orange"
        else:
            grade = "Necesitas repasar 📚"
            color = "red"
        
        result_text = f"PUNTUACIÓN FINAL\n\n{score}/{len(self.questions)} correctas ({pct}%)\n\n{grade}\n\n" + "\n".join(details)
        
        messagebox.showinfo("Resultado del Cuestionario", result_text)
        self.destroy()


if __name__ == "__main__":
    print("="*70)
    print("📚 HISTORIA Y EVOLUCIÓN DE LA GRAFICACIÓN POR COMPUTADORA")
    print("="*70)
    print("\n✨ Características:")
    print("   • Línea del tiempo interactiva")
    print("   • Filtros por década y búsqueda")
    print("   • 🔊 Síntesis de voz (Text-to-Speech)")
    print("   • Exportación CSV/JSON")
    print("   • Cuestionario de evaluación")
    print("   • 🎨 Diseño moderno con colores")
    print("\n🚀 Iniciando aplicación...\n")
    
    if not TTS_AVAILABLE:
        print("⚠️ pyttsx3 no detectado")
        print("   Para habilitar síntesis de voz, instala:")
        print("   pip install pyttsx3\n")
    
    app = TimelineApp()
    app.mainloop()