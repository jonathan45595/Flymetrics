import re
import glob

emoji_map = {
    '🚀': '<i class="fa-solid fa-rocket"></i>',
    '📄': '<i class="fa-solid fa-file-lines"></i>',
    '📊': '<i class="fa-solid fa-chart-simple"></i>',
    '📥': '<i class="fa-solid fa-download"></i>',
    '📤': '<i class="fa-solid fa-upload"></i>',
    '🔑': '<i class="fa-solid fa-key"></i>',
    '🔒': '<i class="fa-solid fa-lock"></i>',
    '🔓': '<i class="fa-solid fa-lock-open"></i>',
    '⚙️': '<i class="fa-solid fa-gear"></i>',
    '⚙': '<i class="fa-solid fa-gear"></i>',
    '🌾': '<i class="fa-solid fa-wheat-awn"></i>',
    '🛸': '<i class="fa-solid fa-plane-up"></i>',
    '🔍': '<i class="fa-solid fa-magnifying-glass"></i>',
    '📍': '<i class="fa-solid fa-location-dot"></i>',
    '🗺️': '<i class="fa-solid fa-map-location-dot"></i>',
    '🗺': '<i class="fa-solid fa-map-location-dot"></i>',
    '✨': '<i class="fa-solid fa-sparkles"></i>',
    '🎉': '<i class="fa-solid fa-circle-check"></i>',
    '✓': '<i class="fa-solid fa-check"></i>',
    '⚠': '<i class="fa-solid fa-triangle-exclamation"></i>',
    '⚠️': '<i class="fa-solid fa-triangle-exclamation"></i>',
    '⚡': '<i class="fa-solid fa-bolt"></i>',
    '🕒': '<i class="fa-solid fa-clock"></i>',
    '📅': '<i class="fa-solid fa-calendar-days"></i>',
    '💳': '<i class="fa-solid fa-credit-card"></i>',
    '👤': '<i class="fa-solid fa-user"></i>',
    '👥': '<i class="fa-solid fa-users"></i>',
    '🔴': '<i class="fa-solid fa-circle-dot" style="color:#ef4444;"></i>',
    '🟢': '<i class="fa-solid fa-circle-dot" style="color:#10b981;"></i>',
    '🟡': '<i class="fa-solid fa-circle-dot" style="color:#f59e0b;"></i>',
    '🔐': '<i class="fa-solid fa-shield-halved"></i>',
    '🛑': '<i class="fa-solid fa-circle-stop"></i>',
    '📷': '<i class="fa-solid fa-camera"></i>',
    '🤖': '<i class="fa-solid fa-microchip"></i>',
    '📡': '<i class="fa-solid fa-satellite-dish"></i>',
    '🪪': '<i class="fa-solid fa-id-card"></i>',
    '🏡': '<i class="fa-solid fa-house-chimney"></i>',
    '📋': '<i class="fa-solid fa-clipboard-list"></i>',
    '✉️': '<i class="fa-solid fa-envelope"></i>',
    '✉': '<i class="fa-solid fa-envelope"></i>',
    '1️⃣': '1.',
    '2️⃣': '2.',
    '3️⃣': '3.',
    '4️⃣': '4.'
}

targets = [
    'frontend/admin.html',
    'frontend/cliente.html',
    'frontend/tecnico.html',
    'frontend/index.html',
    'frontend/staff.html',
    'frontend/agendar.html',
    'frontend/js/admin.js',
    'frontend/js/app.js'
]

for filepath in targets:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        initial_len = len(content)
        for emoji, fa in emoji_map.items():
            content = content.replace(emoji, fa)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filepath} successfully.")
    except Exception as e:
        print(f"Error updating {filepath}: {e}")
