# 🔗 SeroAI — Sistema de Defensa contra Deepfakes en Tiempo Real

> **Detección avanzada de deepfakes impulsada por IA con análisis forense de 5 ejes, verificación de marca de agua visual y razonamiento holístico**

---

## 🎯 Características de Tecnología Avanzada de Detección de Deepfakes

Un sistema de detección de deepfakes listo para producción que analiza videos e imágenes usando múltiples ejes de detección, combinando análisis de movimiento, verificaciones de realismo biológico, verificación de lógica de escena, detección de artefactos de textura/frecuencia y verificación avanzada de marca de agua/procedencia. Construido para equipos de confianza y seguridad, periodistas e investigadores de IA que necesitan resultados explicables y precisos.

---

## 🌐 Disponible en

[**English**](README.md) • [**한국어**](README.ko.md) • [**日本語**](README.ja.md) • [**中文**](README.zh.md) • **Español** (actual) • [**Tiếng Việt**](README.vi.md) • [**Français**](README.fr.md)

---

## ✨ Características Principales

### 🎯 **Sistema de Detección de 5 Ejes**
- **Estabilidad de Movimiento/Temporal** (50% de peso): Detecta inconsistencias entre fotogramas, anomalías de flujo óptico y artefactos temporales
- **Realismo Biológico/Físico** (20% de peso): Analiza puntos de referencia faciales, patrones de parpadeo, consistencia anatómica y movimientos corporales
- **Lógica de Escena e Iluminación** (15% de peso): Valida persistencia de objetos, consistencia física, coherencia de iluminación y límites de toma
- **Artefactos de Textura y Frecuencia** (10% de peso): Identifica huellas dactilares de GAN, patrones espectrales, artefactos de compresión e inconsistencias de textura
- **Marcas de Agua y Procedencia** (5-50% de peso): Coincidencia de logotipo visual para marcas de agua de modelos de IA verificados (Sora, Gemini, Pika, Luma, Runway, HeyGen, D-ID)

### 🔍 **Capacidades Avanzadas de Detección**
- **Coincidencia de Logotipo Visual**: Coincidencia de plantilla, coincidencia de características ORB, comparación de histograma y SSIM para detección de marca de agua verificada
- **Razonamiento Holístico**: Combina múltiples señales débiles de manera inteligente para reducir falsos positivos y aumentar la confianza
- **Detección de Imposibilidad Semántica**: Marca escenarios lógicamente imposibles (por ejemplo, celebridades fallecidas en nuevas imágenes)
- **Ajuste Dinámico de Peso**: Cambia automáticamente a pesos dominantes de marca de agua (50%) cuando se detectan logotipos de IA verificados
- **Puerta de Calidad**: Pre-filtra medios de baja calidad para prevenir falsos positivos

### 🎨 **Interfaz Web Moderna**
- **React + TypeScript + Vite**: Rápido, receptivo y listo para producción
- **Animaciones Framer Motion**: Transiciones suaves y microinteracciones
- **Modo Oscuro/Claro**: Cambio automático de tema con detección de preferencias del sistema
- **Seguimiento de Progreso en Tiempo Real**: Actualizaciones en vivo durante el análisis con indicadores de estado por método
- **Panel de Resultados Detallado**: Desglose completo del análisis con explicaciones

### 🛡️ **Listo para Producción**
- **Local-First**: Todo el procesamiento ocurre en su dispositivo; sin cargas a la nube
- **Procesamiento Rápido**: Tiempo de ejecución típico de 8-12 segundos para videos estándar
- **Umbrales Configurables**: Límites de decisión ajustables a través de configuración JSON
- **Registro Estructurado**: Registros JSON con registros de análisis detallados
- **Salida de Terminal**: Resultados de análisis en tiempo real impresos en la consola

---

## 🚀 Inicio Rápido

### Prerrequisitos

- **Python 3.9+** (3.10+ recomendado)
- **Node.js 18+** y npm
- **FFmpeg** (para procesamiento de video)
- **Tesseract OCR** (opcional, para detección de marca de agua basada en texto)

### Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/<your-org-or-user>/SeroAI.git
cd SeroAI

# 2. Crear y activar entorno virtual
python -m venv .venv
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

# 3. Instalar dependencias de Python
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 4. Instalar dependencias del frontend
cd webui
npm ci
npm run build
cd ..

# 5. Iniciar el servidor
python app.py
```

El servidor se iniciará en `http://localhost:5000`

### Dependencias del Sistema

**Windows (PowerShell)**:
```powershell
winget install ffmpeg
winget install tesseract  # Opcional
```

**macOS**:
```bash
brew install ffmpeg
brew install tesseract  # Opcional
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get update
sudo apt-get install ffmpeg tesseract-ocr  # Opcional
```

---

> **Nota**: Este documento está traducido automáticamente. La documentación completa estará disponible pronto. Por ahora, consulte la versión en inglés: [README.md](README.md)

---

## 📄 Licencia

**MIT** © 2025 Contribuidores de SeroAI

Consulte el archivo `LICENSE` para más detalles.

