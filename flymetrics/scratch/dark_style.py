import re

path = r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\css\style.css"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update Root variables
root_orig = """:root {
  --bg-color: #f4f6f9;
  --text-main: #343a40;          /* Asphalt */
  --text-muted: #6c757d;         /* Concrete */
  
  /* Corporate Palette */
  --primary-blue: #003049;       /* Navy Pilot */
  --primary-blue-glow: rgba(0, 48, 73, 0.2);
  --accent-cyan: #1c82ad;        /* Aero Link */
  --accent-cyan-glow: rgba(28, 130, 173, 0.15);
  --geo-sand: #e4c7a1;           /* Geo Sand */
  --geo-sand-glow: rgba(228, 199, 161, 0.2);
  
  /* Glass colors */
  --glass-bg: rgba(255, 255, 255, 0.85);
  --glass-border: rgba(108, 117, 125, 0.2);
  --glass-border-hover: rgba(28, 130, 173, 0.4);
  --glass-highlight: rgba(255, 255, 255, 0.95);
  
  /* Fuentes */
  --font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  
  /* Curva de Animación Apple */
  --ease-apple: cubic-bezier(0.16, 1, 0.3, 1);
  --transition: all 0.5s var(--ease-apple);
}"""

root_new = """:root {
  --bg-color: #03060f;           /* Fondo oscuro Navy Pilot profundo */
  --text-main: #f4f6f9;          /* Off-white para alta legibilidad en modo oscuro */
  --text-muted: #8e9aa6;         /* Concrete / Slate grey para textos secundarios */
  
  /* Corporate Palette */
  --primary-blue: #003049;       /* Navy Pilot */
  --primary-blue-glow: rgba(0, 48, 73, 0.45);
  --accent-cyan: #1c82ad;        /* Aero Link */
  --accent-cyan-glow: rgba(28, 130, 173, 0.35);
  --geo-sand: #e4c7a1;           /* Geo Sand */
  --geo-sand-glow: rgba(228, 199, 161, 0.3);
  
  /* Glass colors */
  --glass-bg: rgba(0, 48, 73, 0.25); /* Navy Pilot translúcido */
  --glass-border: rgba(28, 130, 173, 0.25); /* Aero Link border */
  --glass-border-hover: rgba(228, 199, 161, 0.45); /* Geo Sand border hover */
  --glass-highlight: rgba(255, 255, 255, 0.08);
  
  /* Fuentes */
  --font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  
  /* Curva de Animación Apple */
  --ease-apple: cubic-bezier(0.16, 1, 0.3, 1);
  --transition: all 0.5s var(--ease-apple);
}"""

content = content.replace(root_orig, root_new)

# 2. Update background-canvas and blobs for premium dark mode
bg_orig = """.background-canvas {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: -1;
  overflow: hidden;
  background: radial-gradient(circle at 50% 50%, #f4f6f9, #edf2f7);
}

.bg-blob {
  position: absolute;
  border-radius: 50%;
  opacity: 0.6;
  mix-blend-mode: multiply; /* Better blend for light backgrounds */
  will-change: transform;
  transform: translateZ(0);
  backface-visibility: hidden;
}

.blob-blue {
  width: 650px;
  height: 650px;
  background: radial-gradient(circle, rgba(0, 48, 73, 0.12) 0%, rgba(0, 48, 73, 0.04) 40%, transparent 70%);
  top: -10%;
  left: 10%;
  animation: float-slow 20s ease-in-out infinite alternate;
}

.blob-cyan {
  width: 750px;
  height: 750px;
  background: radial-gradient(circle, rgba(28, 130, 173, 0.1) 0%, rgba(28, 130, 173, 0.03) 45%, transparent 70%);
  bottom: -15%;
  right: 15%;
  animation: float-slow 25s ease-in-out infinite alternate-reverse;
}

.blob-purple {
  width: 550px;
  height: 550px;
  background: radial-gradient(circle, rgba(228, 199, 161, 0.15) 0%, rgba(228, 199, 161, 0.05) 40%, transparent 70%);
  top: 40%;
  right: 5%;
  animation: float-medium 18s ease-in-out infinite alternate;
}"""

bg_new = """.background-canvas {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: -1;
  overflow: hidden;
  background: radial-gradient(circle at 50% 50%, #040814, #010206);
}

.bg-blob {
  position: absolute;
  border-radius: 50%;
  opacity: 0.65;
  mix-blend-mode: screen; /* Fusión perfecta para modo oscuro */
  will-change: transform;
  transform: translateZ(0);
  backface-visibility: hidden;
}

.blob-blue {
  width: 700px;
  height: 700px;
  background: radial-gradient(circle, rgba(0, 48, 73, 0.4) 0%, rgba(0, 48, 73, 0.05) 50%, transparent 75%);
  top: -15%;
  left: 10%;
  animation: float-slow 20s ease-in-out infinite alternate;
}

.blob-cyan {
  width: 800px;
  height: 800px;
  background: radial-gradient(circle, rgba(28, 130, 173, 0.3) 0%, rgba(28, 130, 173, 0.04) 50%, transparent 75%);
  bottom: -20%;
  right: 15%;
  animation: float-slow 25s ease-in-out infinite alternate-reverse;
}

.blob-purple {
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(228, 199, 161, 0.2) 0%, rgba(228, 199, 161, 0.03) 50%, transparent 75%);
  top: 35%;
  right: 5%;
  animation: float-medium 18s ease-in-out infinite alternate;
}"""

content = content.replace(bg_orig, bg_new)

# 3. Update navbar styling
nav_orig = """  /* Estilos base del cristal líquido */
  background: rgba(8, 20, 42, 0.15);
  backdrop-filter: blur(40px) saturate(260%);
  -webkit-backdrop-filter: blur(40px) saturate(260%);
  transform: translateZ(0); /* Aceleración por hardware */
  backface-visibility: hidden;
}

.navbar.scrolled {
  height: 54px;
  background: rgba(8, 20, 42, 0.25);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
}"""

nav_new = """  /* Estilos base del cristal líquido */
  background: rgba(0, 48, 73, 0.35); /* Navy Pilot translúcido */
  backdrop-filter: blur(40px) saturate(260%);
  -webkit-backdrop-filter: blur(40px) saturate(260%);
  border: 1px solid rgba(28, 130, 173, 0.25);
  box-shadow: 0 8px 32px rgba(0,0,0,0.5);
  transform: translateZ(0); /* Aceleración por hardware */
  backface-visibility: hidden;
}

.navbar.scrolled {
  height: 54px;
  background: rgba(0, 48, 73, 0.6);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.7);
}"""

content = content.replace(nav_orig, nav_new)

# 4. Make liquid glass cards dark-glass aligned with Navy Pilot
glass_orig = """/* ── CLASES UTILITARIAS DE CRISTAL LÍQUIDO CON DIFRACCIÓN DE LUZ ── */
.liquid-glass {
  position: relative;
  background: rgba(255, 255, 255, 0.85); /* Cristal esmerilado claro premium */
  backdrop-filter: blur(40px) saturate(260%); /* Alta definición de fondo */
  -webkit-backdrop-filter: blur(40px) saturate(260%);
  border: none;
  box-shadow: 
    0 8px 32px 0 rgba(0, 48, 73, 0.08), 
    inset 0 1.5px 0 0 rgba(255, 255, 255, 0.95),
    inset 0 -1px 0 0 rgba(255, 255, 255, 0.5);
}

/* Borde redondeado con gradiente alineado a la paleta corporativa */
.liquid-glass::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  padding: 1.3px; /* Grosor del borde */
  background: linear-gradient(
    135deg, 
    rgba(255, 255, 255, 0.7) 0%, 
    rgba(28, 130, 173, 0.35) 25%, /* Aero Link */
    rgba(0, 48, 73, 0.25) 50%,     /* Navy Pilot */
    rgba(228, 199, 161, 0.3) 75%,  /* Geo Sand */
    rgba(255, 255, 255, 0.2) 100%
  );
  -webkit-mask: 
    linear-gradient(#fff 0 0) content-box, 
    linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
  z-index: 1;
  opacity: 0.8;
  transition: opacity 0.5s var(--ease-apple), background 0.5s var(--ease-apple);
}

.liquid-glass-hover:hover {
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 
    0 16px 40px 0 rgba(28, 130, 173, 0.15), 
    inset 0 1.5px 0 0 rgba(255, 255, 255, 1);
}

.liquid-glass-hover:hover::after {
  opacity: 1;
  background: linear-gradient(
    135deg, 
    rgba(255, 255, 255, 0.9) 0%, 
    rgba(28, 130, 173, 0.55) 25%, /* Aero Link hover glow */
    rgba(0, 48, 73, 0.45) 50%,     /* Navy Pilot */
    rgba(228, 199, 161, 0.5) 75%,  /* Geo Sand hover glow */
    rgba(255, 255, 255, 0.4) 100%
  );
}"""

glass_new = """/* ── CLASES UTILITARIAS DE CRISTAL LÍQUIDO CON DIFRACCIÓN DE LUZ ── */
.liquid-glass {
  position: relative;
  background: rgba(0, 48, 73, 0.28); /* Navy Pilot translúcido esmerilado */
  backdrop-filter: blur(40px) saturate(260%);
  -webkit-backdrop-filter: blur(40px) saturate(260%);
  border: none;
  box-shadow: 
    0 12px 40px rgba(0, 0, 0, 0.65), 
    inset 0 1.5px 0 0 rgba(255, 255, 255, 0.12),
    inset 0 -1px 0 0 rgba(255, 255, 255, 0.02);
}

/* Borde redondeado con gradiente alineado a la paleta corporativa */
.liquid-glass::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  padding: 1.3px; /* Grosor del borde */
  background: linear-gradient(
    135deg, 
    rgba(255, 255, 255, 0.25) 0%, 
    rgba(28, 130, 173, 0.45) 25%, /* Aero Link */
    rgba(0, 48, 73, 0.15) 50%,     /* Navy Pilot */
    rgba(228, 199, 161, 0.4) 75%,  /* Geo Sand */
    rgba(255, 255, 255, 0.08) 100%
  );
  -webkit-mask: 
    linear-gradient(#fff 0 0) content-box, 
    linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
  z-index: 1;
  opacity: 0.85;
  transition: opacity 0.5s var(--ease-apple), background 0.5s var(--ease-apple);
}

.liquid-glass-hover:hover {
  background: rgba(0, 48, 73, 0.4);
  box-shadow: 
    0 20px 48px rgba(28, 130, 173, 0.25), 
    inset 0 1.5px 0 0 rgba(255, 255, 255, 0.2);
}

.liquid-glass-hover:hover::after {
  opacity: 1;
  background: linear-gradient(
    135deg, 
    rgba(255, 255, 255, 0.4) 0%, 
    rgba(28, 130, 173, 0.65) 25%, /* Aero Link hover glow */
    rgba(0, 48, 73, 0.3) 50%,      /* Navy Pilot */
    rgba(228, 199, 161, 0.6) 75%,  /* Geo Sand hover glow */
    rgba(255, 255, 255, 0.25) 100%
  );
}"""

content = content.replace(glass_orig, glass_new)

# 5. Fix .btn-solid on dark mode: make it stand out with Aero Link background and Geo Sand glow
btn_orig = """.btn-solid {
  position: relative;
  background: var(--primary-blue);
  border: 1px solid var(--accent-cyan);
  color: #ffffff;
  padding: 10px 24px;
  font-size: 0.88rem;
  font-weight: 700;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s var(--ease-apple);
  backdrop-filter: blur(25px) saturate(200%);
  -webkit-backdrop-filter: blur(25px) saturate(200%);
  box-shadow: 
    0 4px 20px rgba(0, 48, 73, 0.2), 
    inset 0 1px 1px rgba(255, 255, 255, 0.3),
    0 0 15px rgba(28, 130, 173, 0.1);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.4);
  overflow: hidden;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-solid::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.25),
    transparent
  );
  transition: all 0.6s var(--ease-apple);
}

.btn-solid:hover {
  background: var(--accent-cyan);
  border-color: var(--geo-sand);
  box-shadow: 
    0 10px 28px rgba(28, 130, 173, 0.35), 
    inset 0 1px 1.5px rgba(255, 255, 255, 0.4),
    0 0 25px rgba(28, 130, 173, 0.2);
  transform: translateY(-2px);
}"""

btn_new = """.btn-solid {
  position: relative;
  background: var(--accent-cyan); /* Aero Link background for high contrast */
  border: 1px solid var(--geo-sand); /* Geo Sand border for accent */
  color: #ffffff;
  padding: 10px 24px;
  font-size: 0.88rem;
  font-weight: 700;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s var(--ease-apple);
  backdrop-filter: blur(25px) saturate(200%);
  -webkit-backdrop-filter: blur(25px) saturate(200%);
  box-shadow: 
    0 6px 24px rgba(28, 130, 173, 0.3), 
    inset 0 1px 1px rgba(255, 255, 255, 0.4),
    0 0 15px rgba(228, 199, 161, 0.15);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.4);
  overflow: hidden;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-solid::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.25),
    transparent
  );
  transition: all 0.6s var(--ease-apple);
}

.btn-solid:hover {
  background: var(--primary-blue); /* Hover changes to Navy Pilot */
  border-color: var(--accent-cyan);
  box-shadow: 
    0 10px 28px rgba(0, 48, 73, 0.5), 
    inset 0 1px 1.5px rgba(255, 255, 255, 0.3),
    0 0 25px rgba(28, 130, 173, 0.28);
  transform: translateY(-2px);
}"""

content = content.replace(btn_orig, btn_new)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Dark mode conversion completed for style.css")
