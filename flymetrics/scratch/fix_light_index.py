import os

path = r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\index.html"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace H3 colors inside cards from white to Navy Pilot (#003049)
content = content.replace(
    '<h3 style="font-family: \'Space Grotesk\', sans-serif; font-size: 1.25rem; font-weight: 700; color: #fff;">Nuestra Misión</h3>',
    '<h3 style="font-family: \'Space Grotesk\', sans-serif; font-size: 1.25rem; font-weight: 700; color: var(--primary-blue);">Nuestra Misión</h3>'
)

content = content.replace(
    '<h3 style="font-family: \'Space Grotesk\', sans-serif; font-size: 1.25rem; font-weight: 700; color: #fff;">Sostenibilidad</h3>',
    '<h3 style="font-family: \'Space Grotesk\', sans-serif; font-size: 1.25rem; font-weight: 700; color: var(--primary-blue);">Sostenibilidad</h3>'
)

content = content.replace(
    '<h3 style="font-family: \'Space Grotesk\', sans-serif; font-size: 1.25rem; font-weight: 700; color: #fff;">Salud del Agricultor</h3>',
    '<h3 style="font-family: \'Space Grotesk\', sans-serif; font-size: 1.25rem; font-weight: 700; color: var(--primary-blue);">Salud del Agricultor</h3>'
)

# Replace the text-muted paragraph colors in those cards to use Asphalt (--text-main) for maximum reading clarity
content = content.replace(
    '<p style="font-size: 0.88rem; color: var(--text-muted); line-height: 1.6;">\n            Tecnificar el campo colombiano',
    '<p style="font-size: 0.88rem; color: var(--text-main); line-height: 1.6;">\n            Tecnificar el campo colombiano'
)
content = content.replace(
    '<p style="font-size: 0.88rem; color: var(--text-muted); line-height: 1.6;">\n            Comprometidos con el medio ambiente:',
    '<p style="font-size: 0.88rem; color: var(--text-main); line-height: 1.6;">\n            Comprometidos con el medio ambiente:'
)
content = content.replace(
    '<p style="font-size: 0.88rem; color: var(--text-muted); line-height: 1.6;">\n            Eliminamos la exposición directa del',
    '<p style="font-size: 0.88rem; color: var(--text-main); line-height: 1.6;">\n            Eliminamos la exposición directa del'
)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("index.html text colors updated for light mode contrast!")
