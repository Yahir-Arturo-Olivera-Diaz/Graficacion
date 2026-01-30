# Ejemplo de script en R: lectura, resumen, gráfico y modelo lineal
# Guarda este archivo como "ejemplo_analisis.R" y ejecútalo con: Rscript ejemplo_analisis.R
# Requiere paquetes: tidyverse (instalar si no lo tienes)

if (!requireNamespace("tidyverse", quietly = TRUE)) {
  install.packages("tidyverse", repos = "https://cloud.r-project.org")
}
library(tidyverse)

# --- Parámetros ---
input_path <- "datos.csv"     # Cambia por la ruta a tu CSV si lo tienes
output_plot <- "grafico.png"

# --- Lectura de datos (si no existe, generamos un dataset de ejemplo) ---
if (file.exists(input_path)) {
  df <- read_csv(input_path, show_col_types = FALSE)
  message("Datos leídos desde: ", input_path)
} else {
  set.seed(42)
  df <- tibble(
    x = rnorm(120, mean = 50, sd = 10),
    y = 2.5 * x + rnorm(120, mean = 0, sd = 25),
    grupo = sample(c("A", "B"), 120, replace = TRUE)
  )
  message("No se encontró '", input_path, "'. Se generó un dataset de ejemplo.")
}

# --- Resumen rápido ---
cat("\nEstructura de datos:\n")
print(glimpse(df))
cat("\nResumen estadístico:\n")
print(df %>% summarise_all(list(~ if(is.numeric(.)) list(glimpse = summary(.)) else list(unique = length(unique(.))))))
# También se puede usar summary(df)

# --- Gráficos ---
p <- ggplot(df, aes(x = x, y = y, color = grupo)) +
  geom_point(alpha = 0.7) +
  geom_smooth(method = "lm", se = TRUE, color = "black") +
  labs(title = "Relación entre x e y",
       subtitle = "Puntos por grupo y ajuste lineal",
       x = "x", y = "y") +
  theme_minimal()

ggsave(output_plot, p, width = 7, height = 5, dpi = 300)
message("Gráfico guardado en: ", output_plot)

# --- Modelo lineal simple ---
modelo <- lm(y ~ x, data = df)
cat("\nResumen del modelo lineal (y ~ x):\n")
print(summary(modelo))

# Predicciones (ejemplo)
nuevos <- tibble(x = seq(min(df$x), max(df$x), length.out = 10))
nuevos$y_pred <- predict(modelo, newdata = nuevos)
cat("\nPredicciones de ejemplo:\n")
print(nuevos)

# --- Guardar resultados ---
write_csv(nuevos, "predicciones.csv")
message("Predicciones guardadas en: predicciones.csv")

# --- Fin ---
message("Ejecución finalizada.")