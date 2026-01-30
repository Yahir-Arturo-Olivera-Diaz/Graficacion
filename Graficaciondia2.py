import tkinter as tk
from tkinter import scrolledtext
import pyttsx3

# Inicializar motor de voz
engine = pyttsx3.init()
engine.setProperty('rate', 170)  # Velocidad de la voz

# Diccionario con contenido por década
historia_contenido = {
    "1950-1960": """Durante las décadas de 1950 y 1960, los gráficos por
computadora eran muy primitivos.
Se utilizaban osciloscopios para mostrar imágenes simples. Ivan
Sutherland desarrolló Sketchpad en 1963,
el primer sistema de dibujo interactivo, considerado un hito fundamental
en la historia de la graficación.""",

    "1970": """En los años 70, se introdujeron bibliotecas gráficas
básicas y se empezó a utilizar la rasterización.
Los gráficos comenzaron a aplicarse en CAD y en simulaciones científicas.
La interfaz gráfica de usuario aún no era común.""",

    "1980": """Los años 80 vieron el nacimiento de las tarjetas gráficas
y los primeros gráficos 3D.
La graficación se expandió al entretenimiento con videojuegos básicos en
2D y herramientas de diseño asistido por computadora.""",

    "1990-2000": """Esta fue una época de crecimiento acelerado en el
campo. Se popularizaron APIs como OpenGL y DirectX.
Los videojuegos y animaciones 3D dominaron el mercado. Las GPUs se
volvieron esenciales para el procesamiento gráfico.""",

    "2010 en adelante": """En la actualidad, la graficación por
computadora se usa en realidad virtual, aumentada,
inteligencia artificial, videojuegos ultra realistas y simulaciones
científicas complejas en tiempo real."""
}

# Función para mostrar texto y luego hablar
def mostrar_texto_y_hablar(decada):
    contenido = historia_contenido[decada]

    text_area.config(state='normal')
    text_area.delete(1.0, tk.END)
    text_area.insert(tk.END, f"{decada}:\n\n{contenido}")
    text_area.config(state='disabled')

    ventana.update()   # Fuerza a mostrar el texto primero

    engine.stop()
    engine.say(contenido)
    engine.runAndWait()

# Crear ventana principal
ventana = tk.Tk()
ventana.title("Historia de la Graficación por Computadora")
ventana.geometry("700x500")
ventana.config(bg="#f0f4f8")

# Título
titulo = tk.Label(
    ventana,
    text="Historia y evolución de la graficación por computadora",
    font=("Arial", 16, "bold"),
    bg="#f0f4f8",
    fg="#2c3e50"
)
titulo.pack(pady=10)

# Área de texto desplazable
text_area = scrolledtext.ScrolledText(
    ventana,
    wrap=tk.WORD,
    font=("Arial", 12),
    height=10,
    width=80,
    bg="#ffffff"
)
text_area.pack(pady=10)
text_area.config(state='disabled')

# Frame para botones
frame_botones = tk.Frame(ventana, bg="#f0f4f8")
frame_botones.pack(pady=10)

# Crear botones para cada período
colores = ["#3498db", "#e67e22", "#2ecc71", "#9b59b6", "#e74c3c"]

for i, decada in enumerate(historia_contenido):
    boton = tk.Button(
        frame_botones,
        text=decada,
        width=15,
        font=("Arial", 10, "bold"),
        bg=colores[i],
        fg="white",
        command=lambda d=decada: mostrar_texto_y_hablar(d)
    )
    boton.grid(row=0, column=i, padx=5, pady=5)

# Ejecutar ventana
ventana.mainloop()