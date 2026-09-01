import re

path = r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\css\style.css"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace mobile-drawer styles
drawer_orig = """.mobile-drawer {
  position: fixed;
  top: 0;
  right: -320px;
  width: 320px;
  height: 100vh;
  z-index: 95;
  padding: 100px 32px 40px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  /* High-end spring transition for organic scale-up overshoot (pop & bounce) */
  transition: 
    right 0.65s cubic-bezier(0.34, 1.8, 0.64, 1), 
    transform 0.65s cubic-bezier(0.34, 1.8, 0.64, 1), 
    opacity 0.5s ease, 
    filter 0.5s ease;
  box-shadow: -15px 0 50px rgba(0, 0, 0, 0.65);
  will-change: right, transform, opacity, filter;
  opacity: 0;
  transform: scale(0.85) translateX(40px);
  filter: blur(15px);
}

.mobile-drawer.open {
  right: 0;
  opacity: 1;
  transform: scale(1) translateX(0);
  filter: blur(0);
}"""

drawer_new = """.mobile-drawer {
  position: fixed;
  top: 96px; /* Sits directly below the 64px navbar + padding */
  right: 24px;
  width: 290px;
  height: auto;
  border-radius: 24px;
  z-index: 200;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  background: var(--glass-bg);
  backdrop-filter: blur(40px) saturate(260%);
  -webkit-backdrop-filter: blur(40px) saturate(260%);
  border: 1px solid var(--glass-border);
  box-shadow: 0 16px 48px rgba(0, 48, 73, 0.12);
  transition: all 0.4s var(--ease-apple);
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

content = content.replace(drawer_orig, drawer_new)

# Simplify items translate movements to avoid horizontal shifting
li_orig = """.drawer-links li {
  opacity: 0;
  transform: translateX(45px) scale(0.9);
  transition: 
    opacity 0.5s cubic-bezier(0.16, 1, 0.3, 1), 
    transform 0.6s cubic-bezier(0.34, 1.6, 0.64, 1);
  will-change: opacity, transform;
}"""

li_new = """.drawer-links li {
  opacity: 0;
  transform: translateY(-10px) scale(0.98);
  transition: opacity 0.3s ease, transform 0.3s ease;
  will-change: opacity, transform;
}"""

content = content.replace(li_orig, li_new)

# Fix drawer actions slide animation
actions_orig = """.drawer-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  opacity: 0;
  transform: translateY(25px);
  transition: opacity 0.5s var(--ease-apple), transform 0.5s var(--ease-apple);
  will-change: opacity, transform;
}

.mobile-drawer.open .drawer-actions {
  opacity: 1;
  transform: translateY(0);
  transition-delay: 0.42s;
}"""

actions_new = """.drawer-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  opacity: 0;
  transform: translateY(10px);
  transition: opacity 0.3s ease, transform 0.3s ease;
  will-change: opacity, transform;
}

.mobile-drawer.open .drawer-actions {
  opacity: 1;
  transform: translateY(0);
  transition-delay: 0.2s;
}"""

content = content.replace(actions_orig, actions_new)

# Ensure mobile drawer fits screen width nicely on very small screens
media_query = """@media (max-width: 480px) {
  .mobile-drawer {
    right: 16px;
    left: 16px;
    width: calc(100% - 32px);
  }
  .mobile-drawer.open {
    right: 16px;
  }
}"""

if media_query not in content:
    content += "\n\n" + media_query

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Mobile drawer conversion done in style.css")
