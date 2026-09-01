import re

filepath = r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\index.html"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Replace Navbar Quick Links (Desktop and Mobile Drawer)
nav_links_target = """      <!-- Desktop Links -->
      <ul class="nav-links" id="nav-links">
        <li><a href="#inicio" class="nav-link active">Principal</a></li>
        <li><a href="#servicios" class="nav-link">Servicios</a></li>
        <li><a href="#simuladores" class="nav-link">Simuladores</a></li>
        <li><a href="#ubicaciones" class="nav-link">Ubicaciones</a></li>
        <li><a href="#contacto" class="nav-link">Datos de contacto</a></li>
        <div class="nav-active-pill" id="nav-active-pill"></div>
      </ul>"""

nav_links_replacement = """      <!-- Desktop Links -->
      <ul class="nav-links" id="nav-links">
        <li><a href="#inicio" class="nav-link active">Principal</a></li>
        <li><a href="#servicios" class="nav-link">Servicios</a></li>
        <li><a href="#simuladores" class="nav-link">Simulador</a></li>
        <li><a href="#flota" class="nav-link">Flota</a></li>
        <li><a href="#ubicaciones" class="nav-link">Ubicaciones</a></li>
        <li><a href="#faq" class="nav-link">Preguntas</a></li>
        <div class="nav-active-pill" id="nav-active-pill"></div>
      </ul>"""

content = content.replace(nav_links_target, nav_links_replacement)

drawer_links_target = """    <!-- Links -->
    <ul class="drawer-links" id="drawer-links">
      <li><a href="#inicio" class="drawer-link active">Principal</a></li>
      <li><a href="#servicios" class="drawer-link">Servicios</a></li>
      <li><a href="#simuladores" class="drawer-link">Simuladores</a></li>
      <li><a href="#ubicaciones" class="drawer-link">Ubicaciones</a></li>
      <li><a href="#contacto" class="drawer-link">Datos de contacto</a></li>
      <div class="drawer-active-pill" id="drawer-active-pill"></div>
    </ul>"""

drawer_links_replacement = """    <!-- Links -->
    <ul class="drawer-links" id="drawer-links">
      <li><a href="#inicio" class="drawer-link active">Principal</a></li>
      <li><a href="#servicios" class="drawer-link">Servicios</a></li>
      <li><a href="#simuladores" class="drawer-link">Simulador</a></li>
      <li><a href="#flota" class="drawer-link">Flota</a></li>
      <li><a href="#ubicaciones" class="drawer-link">Ubicaciones</a></li>
      <li><a href="#faq" class="drawer-link">Preguntas</a></li>
      <div class="drawer-active-pill" id="drawer-active-pill"></div>
    </ul>"""

content = content.replace(drawer_links_target, drawer_links_replacement)

# 2. Update Hero Buttons and Title
hero_target = """    <!-- Section 1: Hero (Principal) -->
    <section id="inicio" class="hero-section">
      <h1 class="hero-title">FlyMetrics Aérea</h1>
      <p class="hero-subtitle">
        Diseño exclusivo con interfaz de cristal líquido translúcido. Soluciones aéro-agrícolas de precisión con drones comerciales en Colombia.
      </p>
      <div style="display: flex; gap: 16px; margin-top: 12px; flex-wrap: wrap; justify-content: center;">
        <a href="#servicios" class="btn-solid">Explorar Servicios</a>
        <a href="#simuladores" class="btn-glass">Simulador de Telemetría</a>
      </div>
    </section>"""

hero_replacement = """    <!-- Section 1: Hero (Principal) -->
    <section id="inicio" class="hero-section">
      <h1 class="hero-title" style="margin-bottom: 8px;">FlyMetrics Tecnología</h1>
      <p class="hero-subtitle">
        Soluciones aéro-agrícolas de precisión con drones inteligentes en Colombia. Interfaz de cristal líquido de alta tecnología.
      </p>
      <div style="display: flex; gap: 16px; margin-top: 12px; flex-wrap: wrap; justify-content: center; z-index: 10;">
        <a href="#servicios" class="btn-solid" style="text-decoration: none;">Explorar Servicios</a>
        <a href="#simuladores" class="btn-glass" style="text-decoration: none;">Simulador de Ahorros</a>
      </div>
    </section>"""

content = content.replace(hero_target, hero_replacement)

# 3. Update Services Section with custom SVGs and clean heading style
services_target = """    <!-- Section 2: Servicios -->
    <section id="servicios" style="padding: 80px 0; border-top: 1px solid rgba(255, 255, 255, 0.05);">
      <h2 style="font-family: 'Syne', sans-serif; font-size: 2.2rem; text-align: center; margin-bottom: 12px;">Nuestros Servicios</h2>
      <p style="text-align: center; color: var(--text-muted); max-width: 500px; margin: 0 auto 48px;">
        Haz clic en cada servicio para ver la ficha técnica en nuestro panel interactivo.
      </p>
      
      <div class="showcase-grid">
        <article class="showcase-card liquid-glass liquid-glass-hover" data-service-id="0" style="cursor: pointer;">
          <div style="font-size: 2rem; color: var(--primary-blue);">🌾</div>
          <h3>Fumigación Agrícola</h3>
          <p>Aplicación de fitosanitarios por hectárea con drones DJI Agras T40. Dosificación variable ultra eficiente.</p>
        </article>

        <article class="showcase-card liquid-glass liquid-glass-hover" data-service-id="1" style="cursor: pointer;">
          <div style="font-size: 2rem; color: var(--accent-cyan);">🌿</div>
          <h3>Monitoreo NDVI</h3>
          <p>Detección temprana de estrés hídrico y salud del cultivo a través de cámaras multiespectrales a color.</p>
        </article>

        <article class="showcase-card liquid-glass liquid-glass-hover" data-service-id="2" style="cursor: pointer;">
          <div style="font-size: 2rem; color: var(--primary-blue);">🗺️</div>
          <h3>Fotogrametría 3D</h3>
          <p>Planificación y curvas de nivel mediante ortomosaicos de alta resolución centimétrica RTK.</p>
        </article>

        <article class="showcase-card liquid-glass liquid-glass-hover" data-service-id="3" style="cursor: pointer;">
          <div style="font-size: 2rem; color: var(--accent-cyan);">📹</div>
          <h3>Inspección Térmica</h3>
          <p>Auditorías aéreas termográficas y visuales detalladas de subestaciones y paneles solares.</p>
        </article>
      </div>
    </section>"""

services_replacement = """    <!-- Section 2: Servicios -->
    <section id="servicios" style="padding: 80px 0; border-top: 1px solid rgba(255, 255, 255, 0.05);">
      <h2 class="section-title">Nuestros Servicios de Precisión</h2>
      <p style="text-align: center; color: var(--text-muted); max-width: 500px; margin: 0 auto 48px;">
        Haz clic en cada servicio para ver la ficha técnica interactiva.
      </p>
      
      <div class="showcase-grid">
        <article class="showcase-card liquid-glass liquid-glass-hover" data-service-id="0" style="cursor: pointer;">
          <div style="margin-bottom: 8px;">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="width: 42px; height: 42px; color: var(--primary-blue);">
              <path d="M12 2a4 4 0 0 0-4 4v2H6a3 3 0 0 0-3 3v6a1 1 0 0 0 1 1h16a1 1 0 0 0 1-1v-6a3 3 0 0 0-3-3h-2V6a4 4 0 0 0-4-4z" />
              <path d="M8 14h8M12 11v6" />
              <path d="M5 21v1M19 21v1M12 21v1" />
            </svg>
          </div>
          <h3>Fumigación Agrícola</h3>
          <p>Aplicación de fitosanitarios por hectárea con drones DJI Agras. Dosificación variable ultra eficiente y reducción de desperdicios.</p>
        </article>

        <article class="showcase-card liquid-glass liquid-glass-hover" data-service-id="1" style="cursor: pointer;">
          <div style="margin-bottom: 8px;">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="width: 42px; height: 42px; color: var(--accent-cyan);">
              <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 21 2c-2.48 4-3 5.5-4.1 11.2A7 7 0 0 1 11 20z" />
              <path d="M9 11a3 3 0 1 0 6 0 3 3 0 1 0-6 0z" />
            </svg>
          </div>
          <h3>Monitoreo NDVI</h3>
          <p>Detección temprana de estrés hídrico, plagas y salud general del cultivo mediante cámaras multiespectrales RGB + NIR.</p>
        </article>

        <article class="showcase-card liquid-glass liquid-glass-hover" data-service-id="2" style="cursor: pointer;">
          <div style="margin-bottom: 8px;">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="width: 42px; height: 42px; color: var(--primary-blue);">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
            </svg>
          </div>
          <h3>Fotogrametría 3D</h3>
          <p>Planificación de predios, curvas de nivel y cálculo de volúmenes precisos mediante ortomosaicos georreferenciados RTK.</p>
        </article>

        <article class="showcase-card liquid-glass liquid-glass-hover" data-service-id="3" style="cursor: pointer;">
          <div style="margin-bottom: 8px;">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="width: 42px; height: 42px; color: var(--accent-cyan);">
              <path d="M23 7l-7 5 7 5V7z" />
              <rect x="1" y="5" width="15" height="14" rx="2" ry="2" />
              <circle cx="8" cy="12" r="3" />
            </svg>
          </div>
          <h3>Inspección Térmica</h3>
          <p>Auditorías aéreas termográficas para paneles solares, líneas eléctricas y detección de fugas térmicas industriales.</p>
        </article>
      </div>
    </section>"""

content = content.replace(services_target, services_replacement)

# 4. Redesign Simulator section completely (lines 220 to 540)
# We will match the entire section using regex or a direct replace block
# Let's inspect where simulator starts and ends in content to be sure.
# The simulator section starts with <section id="simuladores" ...> and ends before Section 3.5: Flota
sim_start_idx = content.find('<section id="simuladores"')
sim_end_idx = content.find('<!-- Section 3.5: Flota')
if sim_start_idx != -1 and sim_end_idx != -1:
    print("Found simulator section range")
    
    sim_section_replacement = """<!-- Section 3: Simuladores (3D Terrain) -->
    <section id="simuladores" style="padding: 80px 0; border-top: 1px solid rgba(255, 255, 255, 0.05);">
      <h2 class="section-title">Simulador & Comparador de Costos</h2>
      <p style="text-align: center; color: var(--text-muted); max-width: 600px; margin: 0 auto 48px;">
        Visualiza la telemetría del dron en tiempo real y calcula tus ahorros económicos, hídricos y temporales.
      </p>
      
      <div class="simulator-wrapper">
        
        <!-- COL 1: Canvas & HUD -->
        <div class="liquid-glass sim-panel-canvas" style="padding: 24px; border-radius: 28px;">
          <!-- Tabs -->
          <div style="display: flex; gap: 12px; margin-bottom: 20px; border-bottom: 1px solid var(--glass-border); padding-bottom: 16px; flex-wrap: wrap;">
            <button id="sim-tab-terrain" onclick="switchSimTab('terrain')" style="padding: 9px 20px; border-radius: 20px; font-size: 0.82rem; font-weight: 600; cursor: pointer; transition: all 0.25s; background: rgba(30,144,255,0.15); border: 1px solid rgba(30,144,255,0.4); color: #1E90FF; font-family: 'Space Grotesk',sans-serif;">🏡 Terreno 3D</button>
            <button id="sim-tab-telemetry" onclick="switchSimTab('telemetry')" style="padding: 9px 20px; border-radius: 20px; font-size: 0.82rem; font-weight: 600; cursor: pointer; transition: all 0.25s; background: transparent; border: 1px solid rgba(255,255,255,0.1); color: rgba(255,255,255,0.5); font-family: 'Space Grotesk',sans-serif;">📡 Telemetría DJI</button>
          </div>

          <!-- 3D Terrain Tab Content -->
          <div id="sim-pane-terrain">
            <div style="position: relative; border-radius: 16px; overflow: hidden; border: 1px solid rgba(30,144,255,0.15);">
              <canvas id="terrain-canvas" style="width:100%; height: 350px; display: block; background: #050810;"></canvas>
              <!-- Drone path overlay -->
              <div style="position:absolute; top:12px; left:12px; background: rgba(0,0,0,0.65); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); border: 1px solid rgba(30,144,255,0.3); border-radius: 10px; padding: 10px 14px; font-size: 0.72rem; font-family: monospace; z-index: 5;">
                <div style="color:#00FF88; font-weight:700; margin-bottom:4px;">● VUELO ACTIVO</div>
                <div style="color:rgba(255,255,255,0.65);">Alt: <span id="sim-alt" style="color:#fff;">52m</span></div>
                <div style="color:rgba(255,255,255,0.65);">Vel: <span id="sim-vel" style="color:#fff;">8.4 m/s</span></div>
                <div style="color:rgba(255,255,255,0.65);">Progreso: <span id="sim-ha" style="color:#fff;">0.0</span> Ha</div>
              </div>
              <div id="sim-ha-bar" style="position:absolute; bottom:0; left:0; height:3px; background:linear-gradient(90deg,#1E90FF,#00FF88); width:0%; transition:width 0.5s ease;"></div>
            </div>

            <!-- Mini HUD stats -->
            <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:12px; margin-top:16px;">
              <div class="hud-stat-box">
                <div class="hud-stat-val" id="sim-area">0</div>
                <div class="hud-stat-lbl">Hectáreas</div>
              </div>
              <div class="hud-stat-box">
                <div class="hud-stat-val" id="sim-batt" style="color: #00FF88;">94%</div>
                <div class="hud-stat-lbl">Batería</div>
              </div>
              <div class="hud-stat-box">
                <div class="hud-stat-val" id="sim-wind" style="color: #FFB800;">3.2 m/s</div>
                <div class="hud-stat-lbl">Viento</div>
              </div>
              <div class="hud-stat-box">
                <div class="hud-stat-val" id="sim-signal">GPS:16</div>
                <div class="hud-stat-lbl">Señal</div>
              </div>
            </div>
          </div>

          <!-- Telemetry Tab Content -->
          <div id="sim-pane-telemetry" style="display:none;">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px;">
              <div class="telemetry-card">
                <span class="telemetry-lbl">Batería Inteligente</span>
                <strong class="telemetry-val" id="tel-batt" style="color: var(--accent-cyan);">94%</strong>
                <div style="height: 4px; background: rgba(255,255,255,0.1); border-radius: 2px; overflow: hidden; margin-top: 6px;"><div id="tel-batt-bar" style="width: 94%; height: 100%; background: var(--accent-cyan); transition:width 1s;"></div></div>
              </div>
              <div class="telemetry-card">
                <span class="telemetry-lbl">Seguridad de Vuelo</span>
                <strong class="telemetry-val" id="tel-wind" style="color: #ffb800;">4.2 m/s</strong>
                <span style="font-size: 0.72rem; color: #00ff88; margin-top: 4px; display: block;">✓ Seguro para vuelo</span>
              </div>
              <div class="telemetry-card">
                <span class="telemetry-lbl">Carga Útil</span>
                <strong class="telemetry-val" id="tel-payload" style="color: var(--text-main);">38.5 L</strong>
                <span style="font-size: 0.72rem; color: var(--text-muted); margin-top: 4px; display: block;">Pesticida / Fertilizante</span>
              </div>
            </div>
          </div>
        </div>

        <!-- COL 2: Cost & Savings Calculator -->
        <div class="liquid-glass sim-panel-calculator" style="padding: 24px; border-radius: 28px; display: flex; flex-direction: column; gap: 20px;">
          <h3 style="font-family: 'Space Grotesk', sans-serif; font-size: 1.25rem; font-weight: 700; margin-bottom: 4px; display: flex; align-items: center; gap: 8px;">
            <span>🧮 Calculadora de Ahorros</span>
          </h3>
          
          <!-- Controls inside card -->
          <div style="display: flex; flex-direction: column; gap: 12px; background: rgba(0,0,0,0.2); padding: 16px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.04);">
            <div>
              <label class="calc-label">Servicio Requerido</label>
              <select id="sim-service-type" onchange="calculateSavings()" class="calc-select">
                <option value="spraying">Aspersión / Fumigación Aérea</option>
                <option value="ndvi">Monitoreo NDVI Multiespectral</option>
                <option value="mapping">Fotogrametría y Mapas 3D</option>
                <option value="inspection">Inspección Térmica</option>
              </select>
            </div>
            
            <div>
              <label class="calc-label">Tipo de Cultivo</label>
              <select id="sim-crop" onchange="generateTerrain(); calculateSavings();" class="calc-select">
                <option value="rice">🌾 Arroz (Llano)</option>
                <option value="corn">🌽 Maíz (Ondulado)</option>
                <option value="coffee">☕ Café (Laderas)</option>
                <option value="palm">🌴 Palma (Plano)</option>
              </select>
            </div>

            <div>
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <label class="calc-label">Área del Predio</label>
                <span id="sim-ha-display" style="font-weight: 700; color: var(--primary-blue); font-size: 0.9rem;">10 Hectáreas</span>
              </div>
              <input type="range" id="sim-ha-slider" min="1" max="150" value="10" oninput="calculateSavings()" style="width: 100%; cursor: pointer; accent-color: #1E90FF; margin-top: 6px;" />
            </div>

            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px;">
              <span class="calc-label" style="margin:0;">Relieve de Terreno:</span>
              <div style="display: flex; gap: 6px; align-items: center;">
                <input type="range" id="sim-scale" min="1" max="5" value="2" oninput="updateTerrainScale()" style="cursor: pointer; accent-color: #1E90FF; width: 60px;" />
              </div>
            </div>
          </div>

          <!-- Comparison Results -->
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
            <!-- Manual -->
            <div style="background: rgba(255, 59, 48, 0.04); border: 1px solid rgba(255, 59, 48, 0.15); border-radius: 12px; padding: 12px; text-align: center;">
              <div style="font-size: 0.68rem; color: #ff453a; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">Trabajo Manual</div>
              <strong id="cost-manual" style="font-size: 1.15rem; color: #fff;">$2.100.000</strong>
              <div id="time-manual" style="font-size: 0.72rem; color: var(--text-muted); margin-top: 4px;">Tiempo: 3 días</div>
              <div id="water-manual" style="font-size: 0.72rem; color: var(--text-muted);">Agua: 4.500 L</div>
            </div>
            <!-- Drone -->
            <div style="background: rgba(0, 255, 136, 0.04); border: 1px solid rgba(0, 255, 136, 0.15); border-radius: 12px; padding: 12px; text-align: center;">
              <div style="font-size: 0.68rem; color: #00FF88; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">Dron FlyMetrics</div>
              <strong id="cost-drone" style="font-size: 1.15rem; color: #fff;">$900.000</strong>
              <div id="time-drone" style="font-size: 0.72rem; color: var(--text-muted); margin-top: 4px;">Tiempo: 2.0 horas</div>
              <div id="water-drone" style="font-size: 0.72rem; color: var(--text-muted);">Agua: 150 L</div>
            </div>
          </div>

          <!-- Savings Summary Card -->
          <div style="background: linear-gradient(135deg, rgba(30,144,255,0.1) 0%, rgba(0,255,136,0.06) 100%); border: 1px solid rgba(30,144,255,0.2); border-radius: 16px; padding: 16px; display: flex; flex-direction: column; gap: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-size: 0.8rem; color: var(--text-muted);">Ahorro Económico Neto:</span>
              <strong id="savings-cost" style="color: #00FF88; font-size: 1.2rem; font-family: 'Space Grotesk', sans-serif;">$1.200.000 COP</strong>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 8px;">
              <span style="font-size: 0.75rem; color: var(--text-muted);">Ahorro de Agua:</span>
              <strong id="savings-water" style="color: #00bfff; font-size: 0.85rem;">97% (4.350 Litros)</strong>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-size: 0.75rem; color: var(--text-muted);">Reducción de Tiempo:</span>
              <strong id="savings-time" style="color: #00bfff; font-size: 0.85rem;">97% más rápido</strong>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-size: 0.75rem; color: var(--text-muted);">Exposición Química:</span>
              <strong style="color: #00FF88; font-size: 0.85rem;">0% (Seguridad Total)</strong>
            </div>
          </div>

          <button onclick="openAuthModal('login')" class="btn-solid" style="width: 100%; padding: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; font-size: 0.8rem;">
            📅 Solicitar Cotización de Campo
          </button>
        </div>

      </div>

      <!-- 3D Terrain & Savings Simulation Logic -->
      <script>
      (function() {
        let canvas, ctx, animFrame;
        let terrain = [];
        let droneX = 0, droneY = 0;
        let flightPath = [];
        let simHa = 0, simBatt = 94, simWind = 3.2;
        let scale = 2, cropType = 'rice';
        let tick = 0;
        let cols = 30, rows = 20;
        const COLORS = {
          rice: { base: '#1a3a1a', mid: '#2d5a2d', high: '#3d7a3d', water: '#1a3d6b' },
          corn: { base: '#2a3a15', mid: '#4a6a20', high: '#6a9a30', water: '#1a3d6b' },
          coffee: { base: '#3a2a15', mid: '#5a4a25', high: '#8a6a35', water: '#2a3d5b' },
          palm: { base: '#152a15', mid: '#255a25', high: '#358a35', water: '#0a2d4b' }
        };

        function init() {
          canvas = document.getElementById('terrain-canvas');
          if (!canvas) return;
          canvas.width = canvas.offsetWidth || 800;
          canvas.height = 350;
          ctx = canvas.getContext('2d');
          cropType = document.getElementById('sim-crop').value;
          generateTerrainData();
          calculateSavings();
          loop();
        }

        function generateTerrainData() {
          terrain = [];
          const roughness = { rice: 0.5, corn: 1.2, coffee: 2.5, palm: 0.3 }[cropType] || 1;
          for (let r = 0; r < rows; r++) {
            terrain[r] = [];
            for (let c = 0; c < cols; c++) {
              let h = Math.sin(c * 0.3) * Math.cos(r * 0.25) * roughness;
              h += (Math.random() - 0.5) * 0.4 * roughness;
              terrain[r][c] = h;
            }
          }
          droneX = 0; droneY = 0; flightPath = []; simHa = 0;
        }

        function drawIso() {
          const W = canvas.width, H = canvas.height;
          ctx.clearRect(0, 0, W, H);

          // Background gradient
          const bg = ctx.createLinearGradient(0, 0, 0, H);
          bg.addColorStop(0, '#040810'); bg.addColorStop(1, '#080f1a');
          ctx.fillStyle = bg; ctx.fillRect(0, 0, W, H);

          const cellW = (W / cols) * 0.85;
          const cellH = cellW * 0.5;
          const isoX = (c, r) => (W / 2) + (c - r) * cellW / 2;
          const isoY = (c, r, h) => (H / 3) + (c + r) * cellH / 2 - h * scale * 18;

          const col = COLORS[cropType] || COLORS.rice;

          // Draw terrain cells back-to-front
          for (let r = rows - 1; r >= 0; r--) {
            for (let c = 0; c < cols; c++) {
              const h = terrain[r][c];
              const x = isoX(c, r), y = isoY(c, r, h);
              const x1 = isoX(c+1, r), y1 = isoY(c+1, r, h);
              const x2 = isoX(c+1, r+1), y2 = isoY(c+1, r+1, h);
              const x3 = isoX(c, r+1), y3 = isoY(c, r+1, h);

              const norm = Math.max(0, Math.min(1, (h + 2) / 4));
              const color = h < -0.5 ? col.water
                : norm < 0.4 ? col.base
                : norm < 0.7 ? col.mid
                : col.high;

              ctx.beginPath();
              ctx.moveTo(x, y); ctx.lineTo(x1, y1);
              ctx.lineTo(x2, y2); ctx.lineTo(x3, y3);
              ctx.closePath();
              ctx.fillStyle = color;
              ctx.fill();
              ctx.strokeStyle = 'rgba(0,0,0,0.3)';
              ctx.lineWidth = 0.5;
              ctx.stroke();

              // Side faces
              if (h > 0) {
                ctx.beginPath();
                ctx.moveTo(x, y); ctx.lineTo(x3, y3);
                ctx.lineTo(x3, y3 + h * scale * 12); ctx.lineTo(x, y + h * scale * 12);
                ctx.closePath();
                ctx.fillStyle = 'rgba(0,0,0,0.4)'; ctx.fill();
              }
            }
          }

          // Draw flight path
          if (flightPath.length > 1) {
            ctx.beginPath();
            const fp0 = flightPath[0];
            const h0 = terrain[Math.floor(fp0.r)] && terrain[Math.floor(fp0.r)][Math.floor(fp0.c)] || 0;
            ctx.moveTo(isoX(fp0.c, fp0.r), isoY(fp0.c, fp0.r, h0) - 24);
            for (let i = 1; i < flightPath.length; i++) {
              const fp = flightPath[i];
              const h = terrain[Math.floor(fp.r)] && terrain[Math.floor(fp.r)][Math.floor(fp.c)] || 0;
              ctx.lineTo(isoX(fp.c, fp.r), isoY(fp.c, fp.r, h) - 24);
            }
            ctx.strokeStyle = 'rgba(0,255,136,0.6)'; ctx.lineWidth = 2;
            ctx.setLineDash([4, 4]); ctx.stroke(); ctx.setLineDash([]);
          }

          // Draw drone
          const dc = droneX, dr = droneY;
          const dh = terrain[Math.floor(dr)] && terrain[Math.floor(dr)][Math.floor(dc)] || 0;
          const dx = isoX(dc, dr), dy = isoY(dc, dr, dh) - 24;

          // Shadow
          ctx.beginPath(); ctx.ellipse(isoX(dc,dr), isoY(dc,dr,dh) - 2, 16, 6, 0, 0, Math.PI*2);
          ctx.fillStyle = 'rgba(0,0,0,0.4)'; ctx.fill();

          // Drone body glow
          const grd = ctx.createRadialGradient(dx, dy, 0, dx, dy, 18);
          grd.addColorStop(0, 'rgba(30,144,255,0.35)');
          grd.addColorStop(1, 'rgba(30,144,255,0)');
          ctx.fillStyle = grd; ctx.beginPath(); ctx.arc(dx, dy, 18, 0, Math.PI*2); ctx.fill();

          // Arms
          [[-10,-10],[10,-10],[-10,10],[10,10]].forEach(([ax,ay]) => {
            ctx.beginPath(); ctx.moveTo(dx, dy); ctx.lineTo(dx+ax, dy+ay);
            ctx.strokeStyle = '#1E90FF'; ctx.lineWidth = 2; ctx.stroke();
            ctx.beginPath(); ctx.arc(dx+ax, dy+ay, 4, 0, Math.PI*2);
            ctx.fillStyle = '#00FF88'; ctx.fill();
          });

          // Center dot
          ctx.beginPath(); ctx.arc(dx, dy, 5, 0, Math.PI*2);
          ctx.fillStyle = '#fff'; ctx.fill();

          // Altitude line
          ctx.beginPath();
          ctx.moveTo(isoX(dc,dr), isoY(dc,dr,dh));
          ctx.lineTo(dx, dy);
          ctx.setLineDash([2,4]); ctx.strokeStyle = 'rgba(255,255,255,0.2)'; ctx.lineWidth = 1; ctx.stroke();
          ctx.setLineDash([]);

          // Grid labels
          ctx.fillStyle = 'rgba(255,255,255,0.12)'; ctx.font = '9px monospace';
          ctx.fillText('S', W/2 - 10, H - 20);
          ctx.fillText('N', W/2 - 10, H/4);
        }

        let lastTime = 0;
        function loop(ts = 0) {
          animFrame = requestAnimationFrame(loop);
          const dt = (ts - lastTime) / 1000;
          lastTime = ts;
          tick++;

          // Move drone in serpentine pattern
          const speed = 0.03;
          const row = Math.floor(droneY);
          if (row % 2 === 0) { droneX += speed; } else { droneX -= speed; }

          if (droneX >= cols - 1) { droneY += 0.5; droneX = cols - 1; }
          if (droneX <= 0) { droneY += 0.5; droneX = 0; }
          if (droneY >= rows - 1) { droneX = 0; droneY = 0; simHa = 0; }

          flightPath.push({ c: droneX, r: droneY });
          if (flightPath.length > 200) flightPath.shift();

          const maxHa = parseFloat(document.getElementById('sim-ha-slider').value);
          simHa = (droneY / (rows - 1)) * maxHa;
          simBatt = Math.max(20, 94 - (simHa / maxHa) * 35);
          simWind = 3.2 + Math.sin(tick * 0.05) * 0.8;

          // Update HUD
          if (tick % 5 === 0) {
            const altEl = document.getElementById('sim-alt');
            const velEl = document.getElementById('sim-vel');
            const haEl = document.getElementById('sim-ha');
            const areaEl = document.getElementById('sim-area');
            const battEl = document.getElementById('sim-batt');
            const windEl = document.getElementById('sim-wind');
            const haBar = document.getElementById('sim-ha-bar');
            const gpsEl = document.getElementById('sim-signal');
            if (altEl) altEl.textContent = (45 + Math.sin(tick*0.08)*8).toFixed(0) + 'm';
            if (velEl) velEl.textContent = (8.4 + Math.sin(tick*0.12)*1.2).toFixed(1) + ' m/s';
            if (haEl) haEl.textContent = simHa.toFixed(1);
            if (areaEl) areaEl.textContent = maxHa.toFixed(0);
            if (battEl) battEl.textContent = simBatt.toFixed(0) + '%';
            if (windEl) windEl.textContent = simWind.toFixed(1) + ' m/s';
            if (haBar) haBar.style.width = ((simHa/maxHa)*100) + '%';
            if (gpsEl) gpsEl.textContent = 'GPS:' + (14 + Math.floor(Math.sin(tick*0.02)*2));
          }

          drawIso();
        }

        window.generateTerrain = function() {
          cropType = document.getElementById('sim-crop').value;
          generateTerrainData();
        };
        window.updateTerrainScale = function() {
          scale = parseFloat(document.getElementById('sim-scale').value);
        };
        window.switchSimTab = function(tab) {
          document.getElementById('sim-pane-terrain').style.display = tab === 'terrain' ? 'block' : 'none';
          document.getElementById('sim-pane-telemetry').style.display = tab === 'telemetry' ? 'block' : 'none';
          const btnT = document.getElementById('sim-tab-terrain');
          const btnTel = document.getElementById('sim-tab-telemetry');
          if (tab === 'terrain') {
            btnT.style.background = 'rgba(30,144,255,0.15)'; btnT.style.borderColor = 'rgba(30,144,255,0.4)'; btnT.style.color = '#1E90FF';
            btnTel.style.background = 'transparent'; btnTel.style.borderColor = 'rgba(255,255,255,0.1)'; btnTel.style.color = 'rgba(255,255,255,0.5)';
          } else {
            btnTel.style.background = 'rgba(30,144,255,0.15)'; btnTel.style.borderColor = 'rgba(30,144,255,0.4)'; btnTel.style.color = '#1E90FF';
            btnT.style.background = 'transparent'; btnT.style.borderColor = 'rgba(255,255,255,0.1)'; btnT.style.color = 'rgba(255,255,255,0.5)';
          }
        };

        window.calculateSavings = function() {
          const svc = document.getElementById('sim-service-type').value;
          const ha = parseFloat(document.getElementById('sim-ha-slider').value);
          document.getElementById('sim-ha-display').textContent = `${ha} Hectárea${ha > 1 ? 's' : ''}`;
          
          let dronePrice = 0, manualPrice = 0;
          let droneWater = 0, manualWater = 0;
          let droneTime = 0, manualTime = 0;
          
          if (svc === 'spraying') {
            dronePrice = 90000 * ha;
            manualPrice = 210000 * ha;
            droneWater = 15 * ha;
            manualWater = 450 * ha;
            droneTime = 0.2 * ha;
            manualTime = 6 * ha;
          } else if (svc === 'ndvi') {
            dronePrice = 75000 * ha;
            manualPrice = 140000 * ha;
            droneWater = 0;
            manualWater = 0;
            droneTime = 0.15 * ha;
            manualTime = 4 * ha;
          } else if (svc === 'mapping') {
            dronePrice = 110000 * ha;
            manualPrice = 350000 * ha;
            droneWater = 0;
            manualWater = 0;
            droneTime = 0.25 * ha;
            manualTime = 12 * ha;
          } else { // inspection
            dronePrice = 180000 * ha;
            manualPrice = 480000 * ha;
            droneWater = 0;
            manualWater = 0;
            droneTime = 0.3 * ha;
            manualTime = 16 * ha;
          }
          
          // Update UI
          document.getElementById('cost-manual').textContent = `$${manualPrice.toLocaleString('es-CO')}`;
          document.getElementById('cost-drone').textContent = `$${dronePrice.toLocaleString('es-CO')}`;
          
          // Time format
          const formatTime = (t) => {
            if (t >= 24) return `${(t/24).toFixed(1)} días`;
            return `${t.toFixed(1)} horas`;
          };
          document.getElementById('time-manual').textContent = `Tiempo: ${formatTime(manualTime)}`;
          document.getElementById('time-drone').textContent = `Tiempo: ${formatTime(droneTime)}`;
          
          // Water format
          document.getElementById('water-manual').textContent = `Agua: ${manualWater.toLocaleString('es-CO')} L`;
          document.getElementById('water-drone').textContent = `Agua: ${droneWater.toLocaleString('es-CO')} L`;
          
          // Savings
          const savings = manualPrice - dronePrice;
          document.getElementById('savings-cost').textContent = `$${savings.toLocaleString('es-CO')} COP`;
          
          if (manualWater > 0) {
            const waterSaved = manualWater - droneWater;
            const waterPercent = ((waterSaved / manualWater) * 100).toFixed(0);
            document.getElementById('savings-water').textContent = `${waterPercent}% (${waterSaved.toLocaleString('es-CO')} Litros)`;
          } else {
            document.getElementById('savings-water').textContent = 'No aplica';
          }
          
          const timeSavedPercent = (((manualTime - droneTime) / manualTime) * 100).toFixed(0);
          document.getElementById('savings-time').textContent = `${timeSavedPercent}% más rápido`;
        };

        // Telemetry live simulation
        setInterval(() => {
          const tb = document.getElementById('tel-batt');
          const tbb = document.getElementById('tel-batt-bar');
          const tw = document.getElementById('tel-wind');
          const tp = document.getElementById('tel-payload');
          if (tb) { const v = Math.max(20, 94 - (Date.now()/1000 % 120) * 0.5); tb.textContent = v.toFixed(0) + '%'; if(tbb) tbb.style.width = v + '%'; }
          if (tw) tw.textContent = (3.5 + Math.sin(Date.now()/3000)*1.5).toFixed(1) + ' m/s';
          if (tp) tp.textContent = (38.5 - (Date.now()/1000 % 120) * 0.15).toFixed(1) + ' L';
        }, 1200);

        if (document.readyState === 'complete') { init(); }
        else { window.addEventListener('load', init); }
      })();
      </script>
    </section>"""
    
    content = content[:sim_start_idx] + sim_section_replacement + content[sim_end_idx:]
    print("Simulator section replaced successfully")
else:
    print("WARNING: Simulator range not found!")

# 5. Redesign Fleet Section (DJI Agras T50, DJI Agras T40, DJI Matrice 350 RTK, DJI Mavic 3 Multispectral)
# Locate Fleet section
fleet_start_idx = content.find('<section id="flota"')
fleet_end_idx = content.find('<!-- Section 4: Ubicaciones')
if fleet_start_idx != -1 and fleet_end_idx != -1:
    print("Found fleet section range")
    
    fleet_replacement = """<!-- Section 3.5: Flota de Drones Tecnológicos (Nueva) -->
    <section id="flota" style="padding: 80px 0; border-top: 1px solid rgba(255, 255, 255, 0.05);">
      <h2 class="section-title">Nuestra Flota Tecnológica</h2>
      <p style="text-align: center; color: var(--text-muted); max-width: 500px; margin: 0 auto 48px;">
        Contamos con equipos de última generación homologados ante la Aeronáutica Civil de Colombia.
      </p>

      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 24px;">
        <!-- Dron 1: DJI Agras T50 -->
        <div class="liquid-glass spec-card" style="padding: 24px; border-radius: 24px; display:flex; flex-direction:column; justify-content:space-between;">
          <div>
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 15px;">
              <div>
                <span style="font-size: 0.72rem; color: var(--accent-cyan); text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em;">Aspersión Pesada</span>
                <h3 style="font-family: 'Space Grotesk', sans-serif; font-size: 1.25rem; margin-top: 4px; font-weight: 700;">DJI Agras T50</h3>
              </div>
              <div style="color: var(--primary-blue);">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="width: 38px; height: 38px;">
                  <circle cx="12" cy="12" r="3"/><path d="M6 18L18 6M6 6l12 12M12 2v20M2 12h20"/><path d="M4 6h4M16 6h4M4 18h4M16 18h4"/>
                </svg>
              </div>
            </div>
            <p style="color: var(--text-muted); font-size: 0.82rem; margin-bottom: 15px; line-height:1.5;">
              La cúspide de la aspersión agrícola. Equipado con atomizadores centrífugos dobles y radar omnidireccional.
            </p>
          </div>
          <ul style="list-style: none; font-size: 0.78rem; display: flex; flex-direction: column; gap: 6px; border-top: 1px solid var(--glass-border); padding-top: 12px; margin:0;">
            <li style="display: flex; justify-content: space-between;"><span style="color: var(--text-muted);">Carga útil:</span> <strong>50 Kg</strong></li>
            <li style="display: flex; justify-content: space-between;"><span style="color: var(--text-muted);">Rociado:</span> <strong>16 L/min</strong></li>
            <li style="display: flex; justify-content: space-between;"><span style="color: var(--text-muted);">Ancho de franja:</span> <strong>11 metros</strong></li>
          </ul>
        </div>

        <!-- Dron 2: DJI Agras T40 -->
        <div class="liquid-glass spec-card" style="padding: 24px; border-radius: 24px; display:flex; flex-direction:column; justify-content:space-between;">
          <div>
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 15px;">
              <div>
                <span style="font-size: 0.72rem; color: var(--accent-cyan); text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em;">Aspersión Variable</span>
                <h3 style="font-family: 'Space Grotesk', sans-serif; font-size: 1.25rem; margin-top: 4px; font-weight: 700;">DJI Agras T40</h3>
              </div>
              <div style="color: var(--primary-blue);">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="width: 38px; height: 38px;">
                  <circle cx="12" cy="12" r="3"/><path d="M6 18L18 6M6 6l12 12M12 2v20M2 12h20"/><path d="M4 6h4M16 6h4M4 18h4M16 18h4"/>
                </svg>
              </div>
            </div>
            <p style="color: var(--text-muted); font-size: 0.82rem; margin-bottom: 15px; line-height:1.5;">
              Excelente rendimiento en campo con radar de matriz de fase activa para seguimiento constante de relieve.
            </p>
          </div>
          <ul style="list-style: none; font-size: 0.78rem; display: flex; flex-direction: column; gap: 6px; border-top: 1px solid var(--glass-border); padding-top: 12px; margin:0;">
            <li style="display: flex; justify-content: space-between;"><span style="color: var(--text-muted);">Carga útil:</span> <strong>40 Kg</strong></li>
            <li style="display: flex; justify-content: space-between;"><span style="color: var(--text-muted);">Rociado:</span> <strong>12 L/min</strong></li>
            <li style="display: flex; justify-content: space-between;"><span style="color: var(--text-muted);">Ancho de franja:</span> <strong>11 metros</strong></li>
          </ul>
        </div>

        <!-- Dron 3: DJI Matrice 350 RTK -->
        <div class="liquid-glass spec-card" style="padding: 24px; border-radius: 24px; display:flex; flex-direction:column; justify-content:space-between;">
          <div>
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 15px;">
              <div>
                <span style="font-size: 0.72rem; color: var(--accent-cyan); text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em;">Inspección y LiDAR</span>
                <h3 style="font-family: 'Space Grotesk', sans-serif; font-size: 1.25rem; margin-top: 4px; font-weight: 700;">DJI M350 RTK</h3>
              </div>
              <div style="color: var(--primary-blue);">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="width: 38px; height: 38px;">
                  <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
                  <polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/>
                </svg>
              </div>
            </div>
            <p style="color: var(--text-muted); font-size: 0.82rem; margin-bottom: 15px; line-height:1.5;">
              La plataforma industrial más robusta, ideal para fotogrametría 3D y auditorías termográficas.
            </p>
          </div>
          <ul style="list-style: none; font-size: 0.78rem; display: flex; flex-direction: column; gap: 6px; border-top: 1px solid var(--glass-border); padding-top: 12px; margin:0;">
            <li style="display: flex; justify-content: space-between;"><span style="color: var(--text-muted);">Autonomía:</span> <strong>55 Minutos</strong></li>
            <li style="display: flex; justify-content: space-between;"><span style="color: var(--text-muted);">Protección:</span> <strong>IP55 Clima adverso</strong></li>
            <li style="display: flex; justify-content: space-between;"><span style="color: var(--text-muted);">Sensores:</span> <strong>Triple Carga Útil</strong></li>
          </ul>
        </div>

        <!-- Dron 4: DJI Mavic 3 Multispectral -->
        <div class="liquid-glass spec-card" style="padding: 24px; border-radius: 24px; display:flex; flex-direction:column; justify-content:space-between;">
          <div>
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 15px;">
              <div>
                <span style="font-size: 0.72rem; color: var(--accent-cyan); text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em;">Mapeo NDVI</span>
                <h3 style="font-family: 'Space Grotesk', sans-serif; font-size: 1.25rem; margin-top: 4px; font-weight: 700;">Mavic 3 M</h3>
              </div>
              <div style="color: var(--primary-blue);">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="width: 38px; height: 38px;">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/>
                </svg>
              </div>
            </div>
            <p style="color: var(--text-muted); font-size: 0.82rem; margin-bottom: 15px; line-height:1.5;">
              Dron ligero multiespectral con bandas G, R, RE y NIR integradas para cálculo de índices agronómicos.
            </p>
          </div>
          <ul style="list-style: none; font-size: 0.78rem; display: flex; flex-direction: column; gap: 6px; border-top: 1px solid var(--glass-border); padding-top: 12px; margin:0;">
            <li style="display: flex; justify-content: space-between;"><span style="color: var(--text-muted);">Autonomía:</span> <strong>43 Minutos</strong></li>
            <li style="display: flex; justify-content: space-between;"><span style="color: var(--text-muted);">Cámara RGB:</span> <strong>20 MP Obturador mecánico</strong></li>
            <li style="display: flex; justify-content: space-between;"><span style="color: var(--text-muted);">Rendimiento:</span> <strong>200 Ha / vuelo</strong></li>
          </ul>
        </div>
      </div>
    </section>"""
    
    content = content[:fleet_start_idx] + fleet_replacement + content[fleet_end_idx:]
    print("Fleet section replaced successfully")
else:
    print("WARNING: Fleet range not found!")

# 6. Redesign Map and locations section (lines 590 to 675)
map_start_idx = content.find('<section id="ubicaciones"')
map_end_idx = content.find('<!-- Section 4.5: Preguntas Frecuentes')
if map_start_idx != -1 and map_end_idx != -1:
    print("Found map section range")
    
    map_section_replacement = """<!-- Section 4: Ubicaciones with Real Map -->
    <section id="ubicaciones" style="padding: 80px 0; border-top: 1px solid rgba(255, 255, 255, 0.05);">
      <h2 class="section-title">Zonas de Cobertura Nacional</h2>
      <p style="text-align: center; color: var(--text-muted); max-width: 500px; margin: 0 auto 48px;">
        Sedes y áreas de operación activa en el territorio nacional colombiano.
      </p>

      <div class="map-layout-wrapper">
        <!-- Left Panel: Coverage Info -->
        <div class="liquid-glass map-info-panel" style="padding: 30px; border-radius: 28px; display: flex; flex-direction: column; gap: 20px; justify-content: center;">
          <span style="font-size: 0.75rem; color: var(--accent-cyan); text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em;">Operación Centralizada</span>
          <h3 style="font-family: 'Space Grotesk', sans-serif; font-size: 1.6rem; font-weight: 800; margin: 0; line-height: 1.2;">Sede Principal: Bogotá D.C.</h3>
          <p style="color: var(--text-muted); font-size: 0.88rem; line-height: 1.6; margin: 0;">
            Nuestra oficina central se ubica en Bogotá, coordinando vuelos de aspersión agrícola y fotogrametría en Cundinamarca, Boyacá y el Huila. Contamos con bases operativas secundarias para garantizar desplazamientos rápidos.
          </p>
          <div style="border-top: 1px solid rgba(255,255,255,0.06); padding-top: 15px; display: flex; flex-direction: column; gap: 12px;">
            <h4 style="font-size: 0.9rem; color: #fff; margin: 0; font-family: 'Space Grotesk', sans-serif; font-weight: 600;">Zonas de Cobertura Activa:</h4>
            <div style="display: flex; flex-direction: column; gap: 10px;">
              <div class="map-zone-item" onclick="flyToLocation(4.7110, -74.0721, 'Bogotá D.C.')" style="cursor: pointer; padding: 10px 14px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; transition: all 0.3s;" onmouseover="this.style.borderColor='rgba(30,144,255,0.3)'; this.style.background='rgba(30,144,255,0.04)'" onmouseout="this.style.borderColor='rgba(255,255,255,0.06)'; this.style.background='rgba(255,255,255,0.02)'">
                <strong style="font-size: 0.85rem; color:#fff; display:block;">📍 Zona Centro (Cundinamarca & Boyacá)</strong>
                <span style="font-size: 0.75rem; color: var(--text-muted);">Base Bogotá D.C. — Radio de 120km</span>
              </div>
              <div class="map-zone-item" onclick="flyToLocation(4.1420, -73.6266, 'Villavicencio')" style="cursor: pointer; padding: 10px 14px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; transition: all 0.3s;" onmouseover="this.style.borderColor='rgba(30,144,255,0.3)'; this.style.background='rgba(30,144,255,0.04)'" onmouseout="this.style.borderColor='rgba(255,255,255,0.06)'; this.style.background='rgba(255,255,255,0.02)'">
                <strong style="font-size: 0.85rem; color:#fff; display:block;">🌾 Zona Oriente (Llanos Orientales & Meta)</strong>
                <span style="font-size: 0.75rem; color: var(--text-muted);">Base Villavicencio — Aspersión de arroz y palma</span>
              </div>
              <div class="map-zone-item" onclick="flyToLocation(6.2442, -75.5812, 'Medellín')" style="cursor: pointer; padding: 10px 14px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; transition: all 0.3s;" onmouseover="this.style.borderColor='rgba(30,144,255,0.3)'; this.style.background='rgba(30,144,255,0.04)'" onmouseout="this.style.borderColor='rgba(255,255,255,0.06)'; this.style.background='rgba(255,255,255,0.02)'">
                <strong style="font-size: 0.85rem; color:#fff; display:block;">☕ Zona Occidente (Antioquia & Eje Cafetero)</strong>
                <span style="font-size: 0.75rem; color: var(--text-muted);">Base Medellín — Cultivos de ladera y café</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Panel: Leaflet Map -->
        <div class="liquid-glass map-display-panel" style="border-radius: 28px; overflow: hidden; display: flex; flex-direction: column; border: 1px solid rgba(30,144,255,0.2);">
          <div style="padding: 16px 20px; background: rgba(0,0,0,0.3); border-bottom: 1px solid rgba(255,255,255,0.06); display:flex; align-items:center; gap:10px;">
            <span style="width:8px; height:8px; background:#00FF88; border-radius:50%; box-shadow:0 0 8px #00FF88;"></span>
            <span style="font-size:0.82rem; font-weight:600; color:rgba(255,255,255,0.7); font-family:monospace;">MAPA INTERACTIVO DE COBERTURA</span>
          </div>
          <div id="flymetrics-map" style="width:100%; height:480px; background: #040810;"></div>
        </div>
      </div>

      <!-- Leaflet Map Style & Script -->
      <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
      <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
      <script>
        (function() {
          let map = null;
          function initMap() {
            if (map) return;
            const container = document.getElementById('flymetrics-map');
            if (!container) return;
            
            map = L.map('flymetrics-map', { zoomControl: true }).setView([5.5, -73.5], 6);

            // Dark tile layer from CartoDB
            L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
              attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/">CARTO</a>',
              subdomains: 'abcd', maxZoom: 20
            }).addTo(map);

            const customIcon = L.divIcon({
              html: '<div style="width:28px;height:28px;background:rgba(30,144,255,0.9);border:2px solid #fff;border-radius:50%;box-shadow:0 0 12px rgba(30,144,255,0.7);display:flex;align-items:center;justify-content:center;font-size:12px;">🛸</div>',
              iconSize: [28, 28], iconAnchor: [14, 14], className: ''
            });

            const sedes = [
              { lat: 4.7110, lng: -74.0721, name: 'Sede Bogotá D.C. (HQ)', desc: 'Operación central — Cundinamarca, Boyacá, Huila' },
              { lat: 4.1420, lng: -73.6266, name: 'Base Villavicencio', desc: 'Llanos Orientales — Meta, Casanare' },
              { lat: 6.2442, lng: -75.5812, name: 'Base Medellín', desc: 'Antioquia, Eje Cafetero, Córdoba' }
            ];

            sedes.forEach(s => {
              L.marker([s.lat, s.lng], { icon: customIcon })
                .addTo(map)
                .bindPopup(`<b style="color:#1E90FF;">${s.name}</b><br><span style="font-size:0.8rem;color:#fff;">${s.desc}</span>`);
            });

            // Coverage circles
            sedes.forEach(s => {
              L.circle([s.lat, s.lng], { radius: 120000, color: '#1E90FF', fillColor: '#1E90FF', fillOpacity: 0.04, weight: 1, dashArray: '6 6' }).addTo(map);
            });

            window.flyToLocation = function(lat, lng, name) {
              map.flyTo([lat, lng], 9, { duration: 1.5 });
            };
          }

          if (document.readyState === 'complete' || document.readyState === 'interactive') {
            initMap();
          } else {
            window.addEventListener('load', initMap);
          }
        })();
      </script>
    </section>"""
    
    content = content[:map_start_idx] + map_section_replacement + content[map_end_idx:]
    print("Map section replaced successfully")
else:
    print("WARNING: Map range not found!")

# 7. Delete Contact form completely
# Locate Section 5: Contacto
contact_start_idx = content.find('<!-- Section 5: Contacto -->')
if contact_start_idx == -1:
    contact_start_idx = content.find('<section id="contacto"')
    
contact_end_idx = content.find('</main>')

if contact_start_idx != -1 and contact_end_idx != -1:
    print("Found contact section range")
    content = content[:contact_start_idx] + content[contact_end_idx:]
    print("Contact section deleted successfully")
else:
    print("WARNING: Contact range not found!")

# 8. Footer link cleanup (remove "Contacto Técnico" link and other contact links in footer)
footer_contact_target = """          <li><a href="#contacto" style="color: var(--text-muted); text-decoration: none; transition: color 0.3s;" onmouseover="this.style.color='#fff'" onmouseout="this.style.color='var(--text-muted)'">Contacto Técnico</a></li>"""
footer_contact_replacement = """          <li><a href="#" onclick="openAuthModal('login'); return false;" style="color: var(--text-muted); text-decoration: none; transition: color 0.3s;" onmouseover="this.style.color='#fff'" onmouseout="this.style.color='var(--text-muted)'">Agendar Visita</a></li>"""
content = content.replace(footer_contact_target, footer_contact_replacement)

# 9. Append Floating Action Button before </body>
fab_content = """  <!-- Floating Action Button for Agendar -->
  <button class="fab-agendar liquid-glass" onclick="openAuthModal('login')" title="Agendar Visita Técnica">
    <span class="fab-icon">📅</span>
    <span class="fab-text">Agendar Visita</span>
  </button>

  <!-- Script Files -->"""

content = content.replace("  <!-- Script Files -->", fab_content)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("HTML REDESIGN COMPLETED SUCCESSFULLY!")
