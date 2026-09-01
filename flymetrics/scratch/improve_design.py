import os
import re

html_path = r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\index.html"
css_path = r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\css\style.css"

# 1. Update HTML Background Canvas to add topography SVG contours
if os.path.exists(html_path):
    print("Updating index.html...")
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    canvas_orig = """  <!-- ── BLURRY MULTICOLOR BACKGROUND (macOS Sonoma Vibe) ── -->
  <div class="background-canvas" aria-hidden="true">
    <div class="bg-blob blob-blue"></div>
    <div class="bg-blob blob-cyan"></div>
    <div class="bg-blob blob-purple"></div>
  </div>"""

    canvas_new = """  <!-- ── BLURRY MULTICOLOR BACKGROUND (macOS Sonoma Vibe) ── -->
  <div class="background-canvas" aria-hidden="true">
    <!-- Curvas de nivel topográficas de fondo (Diseño DJI / Guía Agro) -->
    <svg class="topo-lines" viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice" style="position: absolute; inset: 0; width: 100%; height: 100%; opacity: 0.08; pointer-events: none; z-index: 0;">
      <path d="M 100,-100 C 200,100 150,300 350,450 C 550,600 700,500 900,750 C 1100,1000 1300,800 1500,1100" fill="none" stroke="var(--primary-blue)" stroke-width="1.8" />
      <path d="M 150,-100 C 250,120 200,320 400,470 C 600,620 750,520 950,770 C 1150,1020 1350,820 1550,1120" fill="none" stroke="var(--primary-blue)" stroke-width="1.8" />
      <path d="M 200,-100 C 300,140 250,340 450,490 C 650,640 800,540 1000,790 C 1200,1040 1400,840 1600,1140" fill="none" stroke="var(--primary-blue)" stroke-width="1.8" />
      <path d="M 250,-100 C 350,160 300,360 500,510 C 700,660 850,560 1050,810 C 1250,1060 1450,860 1650,1160" fill="none" stroke="var(--primary-blue)" stroke-width="1.8" />
      <path d="M 300,-100 C 400,180 350,380 550,530 C 750,680 900,580 1100,830 C 1300,1080 1500,880 1700,1180" fill="none" stroke="var(--accent-cyan)" stroke-width="1.2" stroke-dasharray="6 4" />
      <path d="M 350,-100 C 450,200 400,400 600,550 C 800,700 950,600 1150,850 C 1350,1100 1550,900 1750,1200" fill="none" stroke="var(--primary-blue)" stroke-width="1.8" />
      <path d="M 400,-100 C 500,220 450,420 650,570 C 850,720 1000,620 1200,870 C 1400,1120 1600,920 1800,1220" fill="none" stroke="var(--primary-blue)" stroke-width="1.8" />
      
      <path d="M-100,600 C 200,500 400,700 700,650 C 1000,600 1200,800 1500,750" fill="none" stroke="var(--primary-blue)" stroke-width="1.5" />
      <path d="M-100,650 C 220,520 420,720 720,670 C 1020,620 1220,820 1520,770" fill="none" stroke="var(--primary-blue)" stroke-width="1.5" />
      <path d="M-100,700 C 240,540 440,740 740,690 C 1040,640 1240,840 1540,790" fill="none" stroke="var(--accent-cyan)" stroke-width="1" stroke-dasharray="5 5" />
    </svg>
    <div class="bg-blob blob-blue"></div>
    <div class="bg-blob blob-cyan"></div>
    <div class="bg-blob blob-purple"></div>
  </div>"""

    if canvas_orig in html_content:
        html_content = html_content.replace(canvas_orig, canvas_new)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print("  index.html updated successfully!")
    else:
        print("  Could not find blurry background in index.html (already updated?).")

# 2. Update CSS styles for mobile-drawer corner animation and active pill contrasts
if os.path.exists(css_path):
    print("Updating style.css...")
    with open(css_path, "r", encoding="utf-8") as f:
        css_content = f.read()

    # Corner animation properties on mobile-drawer
    drawer_orig = """  transition: all 0.4s var(--ease-apple);
  will-change: transform, opacity, filter;
  opacity: 0;
  transform: translateY(-20px) scale(0.95);
  filter: blur(10px);
  pointer-events: none; /* Deactivate when closed */
}

.mobile-drawer.open {
  right: 24px;
  opacity: 1;
  transform: translateY(0) scale(1);
  filter: blur(0);
  pointer-events: auto; /* Activate interaction when open */
}"""

    drawer_new = """  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  will-change: transform, opacity, filter;
  opacity: 0;
  transform-origin: top right; /* Despliegue desde la esquina superior derecha */
  transform: scale(0) translateY(-20px);
  filter: blur(10px);
  pointer-events: none; /* Deactivate when closed */
}

.mobile-drawer.open {
  right: 24px;
  opacity: 1;
  transform: scale(1) translateY(0);
  filter: blur(0);
  pointer-events: auto; /* Activate interaction when open */
}"""

    css_content = css_content.replace(drawer_orig, drawer_new)

    # Active indicator pill contrasts (solid background + white active text)
    pill_orig = """.nav-active-pill {
  position: absolute;
  background: rgba(28, 130, 173, 0.14);
  border: 1px solid rgba(28, 130, 173, 0.35);
  border-radius: 20px;
  z-index: 1;
  /* Premium squash & stretch transitions */
  transition: 
    left 0.48s cubic-bezier(0.25, 1, 0.3, 1), 
    width 0.48s cubic-bezier(0.25, 1, 0.3, 1), 
    transform 0.42s cubic-bezier(0.34, 1.85, 0.64, 1), /* Spring squash back */
    height 0.3s var(--ease-apple), 
    top 0.3s var(--ease-apple);
  box-shadow: 0 0 16px rgba(28, 130, 173, 0.22);
  pointer-events: none;
  top: 50%;
  transform: translateY(-50%) scale(1, 1);
  will-change: left, width, transform;
}"""

    pill_new = """.nav-active-pill {
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

    css_content = css_content.replace(pill_orig, pill_new)

    # Active Link Text color overrides to ensure it's white when pill is behind it
    active_orig = """.nav-link.active {
  color: #ffffff;
}"""

    active_new = """.nav-link.active {
  color: #ffffff !important;
}"""

    css_content = css_content.replace(active_orig, active_new)

    with open(css_path, "w", encoding="utf-8") as f:
        f.write(css_content)
    print("  style.css updated successfully!")

print("All design improvements complete.")
