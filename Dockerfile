# Usar una imagen base de Python con soporte para GUI
FROM python:3.9-slim

# Instalar dependencias del sistema necesarias para Pygame, X11 y audio
RUN apt-get update && apt-get install -y \
    python3-pygame \
    xvfb \
    x11-utils \
    pulseaudio \
    alsa-utils \
    libasound2-dev \
    && rm -rf /var/lib/apt/lists/*

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar requirements.txt si existe, si no, instalar pygame directamente
COPY requirements.txt* ./
RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; else pip install pygame; fi

# Copiar el código del juego y assets
COPY . .

# Establecer variables de entorno para X11 y audio
ENV DISPLAY=:99
ENV SDL_VIDEODRIVER=dummy
ENV SDL_AUDIODRIVER=dummy
ENV PULSE_SERVER=unix:/run/user/1000/pulse/native

# Exponer puerto si tu juego usa red (opcional)
EXPOSE 8000

# Crear script de inicio con configuración de audio
RUN echo '#!/bin/bash\n# Inicializar audio dummy\nexport SDL_AUDIODRIVER=dummy\n# Iniciar Xvfb\nXvfb :99 -screen 0 1024x768x24 &\nsleep 2\n# Ejecutar juego\npython juego.py' > start.sh && chmod +x start.sh

# Comando por defecto
CMD ["./start.sh"]
