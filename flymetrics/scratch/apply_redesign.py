import os
import re

html_path = r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\index.html"
css_path = r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\css\style.css"

# 1. Update style.css
if os.path.exists(css_path):
    print("Modifying style.css...")
    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()

    # Add topographic logo watermark behind the canvas
    watermark_style = """.background-canvas::after {
  content: '';
  position: absolute;
  inset: 0;
  background-image: url('../img/logo.png');
  background-repeat: no-repeat;
  background-position: right 8% bottom 12%;
  background-size: 650px;
  opacity: 0.05; /* Marca de agua ultra sutil */
  pointer-events: none;
  z-index: 1;
}"""
    if ".background-canvas::after" not in css:
        css = css.replace(".background-canvas {", watermark_style + "\n\n.background-canvas {")

    # Navbar height increase (74px / 62px scrolled)
    css = css.replace("height: 64px;", "height: 74px;")
    css = css.replace("height: 54px;", "height: 62px;")

    # Navbar brand logo container scale-up animations (scale 1.25 on hover, scale 0.95 on active)
    css = css.replace("transform: scale(1.32) rotate(6deg);", "transform: scale(1.22);")
    css = css.replace("transform: scale(0.92) rotate(-4deg);", "transform: scale(0.95);")

    # Navbar brand active highlight and sutil scale (no white text, Navy Pilot text scaled 1.03)
    active_orig = """.nav-link.active {
  color: #ffffff !important;
}"""
    active_new = """.nav-link.active {
  color: var(--primary-blue) !important;
  font-weight: 700;
  transform: scale(1.03);
}"""
    css = css.replace(active_orig, active_new)

    # Active Indicator Pill highlight settings
    pill_orig = """.nav-active-pill {
  position: absolute;
  background: var(--primary-blue); /* Solid Navy Pilot for readability */
  border: 1px solid var(--accent-cyan); /* Aero Link border */
  border-radius: 20px;
  z-index: 1;
  /* Premium squash & stretch transitions */
  transition: 
    left 0.48s cubic-bezier(0.25, 1, 0.3, 1), 
    width 0.48s cubic-bezier(0.25, 1, 0.3, 1), 
    transform 0.42s cubic-bezier(0.34, 1.85, 0.64, 1), /* Spring squash back */
    height 0.3s var(--ease-apple), 
    top 0.3s var(--ease-apple);
  box-shadow: 0 4px 14px rgba(0, 48, 73, 0.25);
  pointer-events: none;
  top: 50%;
  transform: translateY(-50%) scale(1, 1);
  will-change: left, width, transform;
}"""
    pill_new = """.nav-active-pill {
  position: absolute;
  background: rgba(28, 130, 173, 0.12); /* Aero Link soft highlight */
  border: 1px solid rgba(28, 130, 173, 0.35);
  border-radius: 20px;
  z-index: 1;
  /* Premium squash & stretch transitions */
  transition: 
    left 0.48s cubic-bezier(0.25, 1, 0.3, 1), 
    width 0.48s cubic-bezier(0.25, 1, 0.3, 1), 
    transform 0.42s cubic-bezier(0.34, 1.85, 0.64, 1), 
    height 0.3s var(--ease-apple), 
    top 0.3s var(--ease-apple);
  box-shadow: 0 4px 12px rgba(28, 130, 173, 0.08);
  pointer-events: none;
  top: 50%;
  transform: translateY(-50%) scale(1, 1);
  will-change: left, width, transform;
}"""
    css = css.replace(pill_orig, pill_new)

    # Brand Title typography transitions (letter-spacing and color shifting)
    brand_hover_orig = """.brand:hover .brand-text {
  transform: scale(1.05) rotate(-1deg);
  filter: drop-shadow(0 2px 8px rgba(28, 130, 173, 0.35));
}"""
    brand_hover_new = """.brand:hover .brand-text {
  transform: scale(1.04);
  letter-spacing: 0.01em; /* Typography movement */
}"""
    css = css.replace(brand_hover_orig, brand_hover_new)

    brand_orig = """.brand-text {
  font-weight: 900;
  font-style: italic; /* Cursivo más prolijo y deportivo */
  font-size: 1.45rem;
  letter-spacing: -0.03em;
  background: linear-gradient(135deg, var(--primary-blue) 0%, var(--accent-cyan) 50%, var(--geo-sand) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  transition: all 0.4s var(--ease-apple);
  will-change: transform, filter;
}"""
    brand_new = """.brand-text {
  font-weight: 900;
  font-style: italic; /* Cursivo prolijo y deportivo */
  font-size: 1.45rem;
  letter-spacing: -0.03em;
  background: linear-gradient(135deg, var(--primary-blue) 0%, var(--accent-cyan) 60%, var(--geo-sand) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  transition: all 0.4s var(--ease-apple);
  will-change: transform, letter-spacing;
}"""
    css = css.replace(brand_orig, brand_new)

    # Round buttons (Acceder and Registrar rounded capsule style)
    css = css.replace("border-radius: 20px;", "border-radius: 24px;")

    # Prevent logo clipping (F letter cut off) in navbar brand
    brand_container_orig = """.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
  cursor: pointer;
}"""
    brand_container_new = """.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
  cursor: pointer;
  padding: 4px 8px; /* Margen para evitar recortes tipográficos */
  border: none !important;
  outline: none !important;
}"""
    css = css.replace(brand_container_orig, brand_container_new)

    # Auth Modal pop-up animation from the top-right corner
    pop_animation = """@keyframes authPop {
  from {
    opacity: 0;
    transform: scale(0.2) translate(300px, -200px);
    filter: blur(10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translate(0, 0);
    filter: blur(0);
  }
}

.modal-content {
  animation: authPop 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  transform-origin: top right;
}"""
    if "authPop" not in css:
        css += "\n\n" + pop_animation

    # Specs table liquid glass in modal details
    table_css = """.specs-table-container {
  background: rgba(255, 255, 255, 0.45) !important;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(108, 117, 125, 0.15);
  border-radius: 16px;
  padding: 12px;
  box-shadow: 0 8px 32px rgba(0, 48, 73, 0.05);
}

.specs-table td {
  padding: 10px 14px;
  border-bottom: 1px solid rgba(108, 117, 125, 0.1);
  color: var(--text-main);
}"""
    if ".specs-table-container" not in css:
        css += "\n\n" + table_css

    with open(css_path, "w", encoding="utf-8") as f:
        f.write(css)
    print("  style.css updated successfully!")

# 2. Update index.html to prevent registration icon clipping and set modal classes
if os.path.exists(html_path):
    print("Modifying index.html...")
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Re-draw the registration person icon with viewbox padding to prevent clipping
    icon_orig = """            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="15" height="15" style="vertical-align: middle;">
              <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2M8 7a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM20 8v6M23 11h-6"/>
            </svg>"""
    icon_new = """            <svg viewBox="-2 -2 28 28" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" style="vertical-align: middle; padding: 1px;">
              <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2M8 7a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM20 8v6M23 11h-6"/>
            </svg>"""
    html = html.replace(icon_orig, icon_new)

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("  index.html updated successfully!")

print("Redesign implementation script complete.")
