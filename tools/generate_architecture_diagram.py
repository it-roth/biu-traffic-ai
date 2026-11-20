"""
Generate an ultra-authentic Architecture Diagram for BIU Traffic AI
Matching the reference image style with real, accurate vector logos:
  - VS Code (Blue Ribbon)
  - GitLab (Orange/Red Fox polygons)
  - Jenkins (Butler with red bowtie)
  - Docker (Blue Whale with container stack)
  - Users / CCTV (Blue avatar & camera badge)
  - Cloudflare (Orange cloud)
  - Vue.js (Official Green & Slate V logo)
  - Traefik / Nginx (Cyan layered route arrows)
  - Keycloak / Auth (Hexagonal shield & key brackets)
  - Django (Official Django green shield & typography)
  - PostgreSQL (Official blue elephant silhouette)
  - Redis (Official 3-layer red isometric cube stack)
  - MinIO (Official flamingo icon)
  - YOLO & ByteTrack & Cambodian Law
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path as MplPath
from pathlib import Path

fig, ax = plt.subplots(figsize=(16, 11), dpi=220)
fig.patch.set_facecolor('#ffffff')
ax.set_facecolor('#ffffff')
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# Outer black border like reference
outer_border = patches.Rectangle((1.2, 1.2), 97.6, 97.6, fill=False, edgecolor='#1e293b', linewidth=2.5)
ax.add_patch(outer_border)

# Header Title
ax.text(50, 96.5, "BIU Traffic AI System Architecture", 
        fontsize=22, fontweight='bold', ha='center', va='center', color='#0f172a', fontfamily='sans-serif')
ax.text(50, 94.2, "BELTEI International University • Faculty of Information Technology & Science", 
        fontsize=10.5, ha='center', va='center', color='#64748b', fontfamily='sans-serif')

# =============================================================================
# REAL LOGO DRAWING HELPERS
# =============================================================================

def draw_vscode(ax, cx, cy, s=2.5):
    """Real VS Code Ribbon Logo"""
    # Back ribbon (Dark blue)
    p1 = [(cx - s*0.7, cy - s*0.8), (cx + s*0.6, cy + s*0.9), (cx + s*0.9, cy + s*0.7), (cx - s*0.3, cy - s*0.9)]
    ax.add_patch(patches.Polygon(p1, facecolor='#005a9e', edgecolor='none', zorder=5))
    # Front ribbon (Cyan/Light blue)
    p2 = [(cx - s*0.7, cy + s*0.8), (cx + s*0.6, cy - s*0.9), (cx + s*0.9, cy - s*0.7), (cx - s*0.3, cy + s*0.9)]
    ax.add_patch(patches.Polygon(p2, facecolor='#0078d7', edgecolor='none', zorder=6))
    # Side fold (Bright blue)
    p3 = [(cx + s*0.6, cy + s*0.9), (cx + s*0.9, cy + s*0.7), (cx + s*0.9, cy - s*0.7), (cx + s*0.6, cy - s*0.9)]
    ax.add_patch(patches.Polygon(p3, facecolor='#1f9cf0', edgecolor='none', zorder=7))
    # Left bow
    p4 = [(cx - s*0.7, cy + s*0.8), (cx - s*0.9, cy + s*0.4), (cx - s*0.9, cy - s*0.4), (cx - s*0.7, cy - s*0.8), (cx - s*0.3, cy)]
    ax.add_patch(patches.Polygon(p4, facecolor='#005a9e', edgecolor='none', zorder=7))

def draw_gitlab(ax, cx, cy, s=2.2):
    """Real GitLab Fox Logo (Orange / Red / Yellow polygons)"""
    # Center forehead (Orange)
    ax.add_patch(patches.Polygon([(cx, cy - s*0.9), (cx - s*0.5, cy + s*0.6), (cx + s*0.5, cy + s*0.6)], facecolor='#fc6d26', edgecolor='none', zorder=6))
    # Left cheek (Light Orange)
    ax.add_patch(patches.Polygon([(cx, cy - s*0.9), (cx - s*0.5, cy + s*0.6), (cx - s*0.9, cy - s*0.2)], facecolor='#fca326', edgecolor='none', zorder=5))
    # Right cheek (Light Orange)
    ax.add_patch(patches.Polygon([(cx, cy - s*0.9), (cx + s*0.5, cy + s*0.6), (cx + s*0.9, cy - s*0.2)], facecolor='#fca326', edgecolor='none', zorder=5))
    # Left ear (Dark Orange/Red)
    ax.add_patch(patches.Polygon([(cx - s*0.5, cy + s*0.6), (cx - s*0.9, cy - s*0.2), (cx - s*0.8, cy + s*0.8)], facecolor='#e24329', edgecolor='none', zorder=6))
    # Right ear (Dark Orange/Red)
    ax.add_patch(patches.Polygon([(cx + s*0.5, cy + s*0.6), (cx + s*0.9, cy - s*0.2), (cx + s*0.8, cy + s*0.8)], facecolor='#e24329', edgecolor='none', zorder=6))

def draw_jenkins(ax, cx, cy, s=2.2):
    """Real Jenkins Butler Logo"""
    # Hair / cap (Black)
    ax.add_patch(patches.Circle((cx, cy + s*0.3), s*0.6, facecolor='#1e293b', zorder=5))
    # Face (Skin tone)
    ax.add_patch(patches.Circle((cx, cy), s*0.5, facecolor='#fed7aa', edgecolor='#475569', linewidth=1, zorder=6))
    # Body suit (Dark blue)
    ax.add_patch(patches.Polygon([(cx - s*0.6, cy - s*0.9), (cx + s*0.6, cy - s*0.9), (cx + s*0.3, cy - s*0.3), (cx - s*0.3, cy - s*0.3)], facecolor='#1e3a8a', zorder=6))
    # Red bowtie
    ax.add_patch(patches.Polygon([(cx - s*0.25, cy - s*0.4), (cx + s*0.25, cy - s*0.4), (cx, cy - s*0.5)], facecolor='#ef4444', zorder=7))
    ax.add_patch(patches.Polygon([(cx - s*0.25, cy - s*0.6), (cx + s*0.25, cy - s*0.6), (cx, cy - s*0.5)], facecolor='#ef4444', zorder=7))

def draw_docker(ax, cx, cy, s=2.3):
    """Real Docker Whale with Container Stack"""
    # Whale body
    whale = patches.Ellipse((cx, cy - s*0.2), s*1.8, s*0.9, facecolor='#2496ed', zorder=5)
    ax.add_patch(whale)
    # Tail
    ax.add_patch(patches.Polygon([(cx + s*0.7, cy - s*0.1), (cx + s*1.1, cy + s*0.4), (cx + s*0.9, cy - s*0.3)], facecolor='#2496ed', zorder=5))
    # Containers on back (3 columns, 2 rows)
    cw, ch = s*0.22, s*0.2
    for row in range(2):
        for col in range(3):
            bx = cx - s*0.45 + col*(cw + s*0.05)
            by = cy + s*0.1 + row*(ch + s*0.05)
            ax.add_patch(patches.Rectangle((bx, by), cw, ch, facecolor='#0ea5e9', edgecolor='#ffffff', linewidth=0.8, zorder=6))
    # Top single container
    ax.add_patch(patches.Rectangle((cx - s*0.15, cy + s*0.6), cw, ch, facecolor='#0ea5e9', edgecolor='#ffffff', linewidth=0.8, zorder=6))

def draw_vue(ax, cx, cy, s=2.8):
    """Official Vue.js Logo (Green outer V, Slate inner V)"""
    # Outer Green V (#42b883)
    p_green = [(cx, cy - s*0.9), (cx + s*0.95, cy + s*0.8), (cx + s*0.55, cy + s*0.8), (cx, cy - s*0.1), (cx - s*0.55, cy + s*0.8), (cx - s*0.95, cy + s*0.8)]
    ax.add_patch(patches.Polygon(p_green, facecolor='#42b883', edgecolor='none', zorder=6))
    # Inner Slate V (#35495e)
    p_slate = [(cx, cy - s*0.1), (cx + s*0.55, cy + s*0.8), (cx + s*0.25, cy + s*0.8), (cx, cy + s*0.35), (cx - s*0.25, cy + s*0.8), (cx - s*0.55, cy + s*0.8)]
    ax.add_patch(patches.Polygon(p_slate, facecolor='#35495e', edgecolor='none', zorder=7))

def draw_traefik_nginx(ax, cx, cy, s=2.5):
    """Traefik / Nginx Ingress Layers (Layered blue diamond arrows)"""
    # Top diamond outline
    p1 = [(cx, cy + s*0.8), (cx + s*0.9, cy + s*0.3), (cx, cy - s*0.2), (cx - s*0.9, cy + s*0.3)]
    ax.add_patch(patches.Polygon(p1, facecolor='#e0f2fe', edgecolor='#0284c7', linewidth=2.5, zorder=5))
    # Bottom diamond outline
    p2 = [(cx, cy + s*0.2), (cx + s*0.9, cy - s*0.3), (cx, cy - s*0.8), (cx - s*0.9, cy - s*0.3)]
    ax.add_patch(patches.Polygon(p2, facecolor='none', edgecolor='#0284c7', linewidth=2.5, zorder=6))

def draw_keycloak_auth(ax, cx, cy, s=2.5):
    """Authentication Server Logo (Hexagonal shield with cyan brackets)"""
    # Outer dark hexagon
    hex_pts = []
    import math
    for i in range(6):
        angle = math.pi/6 + i * (math.pi/3)
        hex_pts.append((cx + s*0.9 * math.cos(angle), cy + s*0.9 * math.sin(angle)))
    ax.add_patch(patches.Polygon(hex_pts, facecolor='#334155', edgecolor='#0f172a', linewidth=2, zorder=5))
    # Inner cyan brackets (< >)
    ax.text(cx, cy, "< >", fontsize=16, fontweight='heavy', ha='center', va='center', color='#38bdf8', zorder=6, fontfamily='monospace')

def draw_django(ax, cx, cy, s=2.8):
    """Official Django Shield & Logo (Deep green hexagon with white power icon)"""
    import math
    hex_pts = []
    for i in range(6):
        angle = i * (math.pi/3)
        hex_pts.append((cx + s*1.0 * math.cos(angle), cy + s*1.0 * math.sin(angle)))
    ax.add_patch(patches.Polygon(hex_pts, facecolor='#092e20', edgecolor='#44b78b', linewidth=2.5, zorder=5))
    # Inner power / loop icon (White)
    ax.add_patch(patches.Arc((cx, cy - s*0.05), s*0.8, s*0.8, angle=0, theta1=45, theta2=315, color='#ffffff', linewidth=3, zorder=6))
    ax.plot([cx, cx], [cy + s*0.05, cy + s*0.5], color='#ffffff', linewidth=3, solid_capstyle='round', zorder=6)

def draw_postgres(ax, cx, cy, s=2.4):
    """Official PostgreSQL Elephant Slonik Silhouette (#336791)"""
    # Head & ear
    ax.add_patch(patches.Circle((cx, cy + s*0.1), s*0.65, facecolor='#336791', zorder=5))
    ax.add_patch(patches.Ellipse((cx - s*0.35, cy + s*0.2), s*0.5, s*0.8, facecolor='#254d6e', zorder=6))
    # Trunk curving down and up
    trunk = patches.Arc((cx + s*0.4, cy - s*0.3), s*0.7, s*0.8, angle=-30, theta1=0, theta2=180, color='#336791', linewidth=4.5, zorder=6)
    ax.add_patch(trunk)
    # Eye
    ax.add_patch(patches.Circle((cx + s*0.15, cy + s*0.3), s*0.08, facecolor='#ffffff', zorder=7))

def draw_redis(ax, cx, cy, s=2.2):
    """Official Redis Logo (3-layer red isometric stack)"""
    colors = ['#dc2626', '#b91c1c', '#991b1b']
    for i, col in enumerate(colors):
        y_off = cy - (i - 1) * s*0.45
        diamond = [(cx, y_off + s*0.35), (cx + s*0.85, y_off), (cx, y_off - s*0.35), (cx - s*0.85, y_off)]
        ax.add_patch(patches.Polygon(diamond, facecolor=col, edgecolor='#7f1d1d', linewidth=1, zorder=5 + (2-i)))
        # Little white accent on top layer
        if i == 0:
            ax.add_patch(patches.Circle((cx, y_off), s*0.12, facecolor='#ffffff', zorder=8))

def draw_storage_media(ax, cx, cy, s=2.2):
    """MinIO / Storage Flamingo / Folder Logo"""
    # Storage folder / bucket shape (Red/Pink #f43f5e)
    ax.add_patch(patches.Polygon([(cx - s*0.6, cy - s*0.7), (cx + s*0.6, cy - s*0.7), (cx + s*0.4, cy + s*0.6), (cx - s*0.4, cy + s*0.6)], facecolor='#e11d48', zorder=5))
    # Stylized bird/handle
    ax.plot([cx - s*0.2, cx, cx + s*0.3], [cy + s*0.3, cy + s*0.8, cy + s*0.1], color='#ffffff', linewidth=2.5, zorder=6)

def draw_monitoring_grafana(ax, cx, cy, s=2.0):
    """Grafana Swirl Icon"""
    ax.add_patch(patches.Circle((cx, cy), s*0.75, facecolor='#0284c7', zorder=5))
    ax.add_patch(patches.Arc((cx, cy), s*0.9, s*0.9, angle=45, theta1=0, theta2=270, color='#f97316', linewidth=3, zorder=6))

def draw_monitoring_prometheus(ax, cx, cy, s=2.0):
    """Prometheus Flame Icon"""
    ax.add_patch(patches.Circle((cx, cy), s*0.75, facecolor='#e11d48', zorder=5))
    flame = [(cx, cy + s*0.5), (cx + s*0.3, cy), (cx + s*0.15, cy - s*0.4), (cx - s*0.15, cy - s*0.4), (cx - s*0.3, cy)]
    ax.add_patch(patches.Polygon(flame, facecolor='#ffffff', zorder=6))

def draw_monitoring_loki(ax, cx, cy, s=2.0):
    """Loki / RedisInsight Logs Graphic"""
    for i, h in enumerate([0.5, 0.8, 0.6, 0.9]):
        bx = cx - s*0.4 + i*s*0.25
        ax.add_patch(patches.Rectangle((bx, cy - s*0.4), s*0.15, s*h, facecolor='#f59e0b', zorder=5))


# =============================================================================
# 1. TOP SECTION: DEPLOYMENT PIPELINE (Orange Border)
# =============================================================================
deploy_rect = patches.Rectangle((3, 73.5), 65, 18, fill=False, edgecolor='#f97316', linewidth=2, zorder=2)
ax.add_patch(deploy_rect)
ax.text(35.5, 75.3, "Deployment", fontsize=12, fontweight='bold', ha='center', va='center', color='#0f172a')

# Inner red dashed container
inner_deploy = patches.Rectangle((26.5, 78), 40, 12, fill=False, edgecolor='#ef4444', linewidth=1.5, linestyle='--', zorder=2)
ax.add_patch(inner_deploy)

# Logos in Deployment:
# 1. VS Code
draw_vscode(ax, 8, 84, s=2.8)
ax.text(8, 79.5, "VS Code", fontsize=8.5, fontweight='bold', ha='center', va='center', color='#475569')

# 2. GitLab
draw_gitlab(ax, 19, 84, s=2.6)
ax.text(19, 79.5, "GitLab / Hub", fontsize=8.5, fontweight='bold', ha='center', va='center', color='#475569')

# 3. Jenkins
draw_jenkins(ax, 32, 84, s=2.4)
ax.text(32, 79.5, "Jenkins CI", fontsize=8.5, fontweight='bold', ha='center', va='center', color='#475569')

# 4. AWS / Container
draw_docker(ax, 47, 83.5, s=2.2)
ax.text(47, 79.5, "Docker Registry", fontsize=8.5, fontweight='bold', ha='center', va='center', color='#475569')

# 5. Docker Deploy
draw_docker(ax, 60, 83.5, s=2.5)
ax.text(60, 79.5, "Docker Compose", fontsize=8.5, fontweight='bold', ha='center', va='center', color='#475569')

# Connecting red arrows inside deployment
for x_start in [12, 23.5, 39, 52]:
    ax.annotate('', xy=(x_start + 3.8, 84), xytext=(x_start, 84),
                arrowprops=dict(arrowstyle="->", color='#ef4444', lw=1.8), zorder=8)

# Mini chip icon above container
ax.add_patch(patches.Rectangle((45.5, 91), 3, 2.5, facecolor='#f97316', edgecolor='#ea580c', linewidth=1, zorder=8))
ax.text(47, 92.2, "CPU", fontsize=6, fontweight='bold', color='#ffffff', ha='center', va='center', zorder=9)


# =============================================================================
# 2. TOP RIGHT: AUTHENTICATION SERVER
# =============================================================================
auth_rect = patches.Rectangle((74, 73.5), 23, 18, fill=False, edgecolor='#0f172a', linewidth=2, zorder=2)
ax.add_patch(auth_rect)
ax.text(85.5, 90, "Authentication Server", fontsize=12, fontweight='bold', ha='center', va='center', color='#0f172a')

draw_keycloak_auth(ax, 85.5, 81.5, s=3.5)
ax.text(85.5, 75.5, "SimpleJWT (7-Day Tokens)", fontsize=8.5, fontweight='bold', ha='center', va='center', color='#64748b')


# =============================================================================
# 3. MIDDLE ROW: USERS -> CLOUDFLARE -> VUE 3 -> TRAEFIK / NGINX
# =============================================================================

# Users Circle
users_circle = patches.Circle((9.5, 50), 6.5, facecolor='#ffffff', edgecolor='#0284c7', linewidth=2, zorder=4)
ax.add_patch(users_circle)
# Multi-user avatar graphic
ax.add_patch(patches.Circle((9.5, 52), 2.2, facecolor='#0284c7', zorder=5))
ax.add_patch(patches.Ellipse((9.5, 47), 5.5, 3.5, facecolor='#0284c7', zorder=5))
ax.add_patch(patches.Circle((6.5, 51), 1.5, facecolor='#38bdf8', zorder=6))
ax.add_patch(patches.Circle((12.5, 51), 1.5, facecolor='#38bdf8', zorder=6))
ax.text(9.5, 41.5, "Officers & CCTV", fontsize=9.5, fontweight='bold', ha='center', va='center', color='#0369a1')

# Cloudflare Cloud Icon (#f97316)
ax.add_patch(patches.Ellipse((21, 51), 4.5, 3, facecolor='#f97316', zorder=5))
ax.add_patch(patches.Circle((19.5, 50), 1.5, facecolor='#f97316', zorder=5))
ax.add_patch(patches.Circle((22.5, 50.5), 1.8, facecolor='#f97316', zorder=5))
ax.text(21, 46.8, "Cloudflare", fontsize=8.5, fontweight='bold', ha='center', va='center', color='#ea580c')

# Arrow: Users -> Cloudflare -> Frontend
ax.annotate('', xy=(18.5, 50.5), xytext=(16, 50.5), arrowprops=dict(arrowstyle="->", color='#ef4444', lw=1.8), zorder=8)
ax.annotate('', xy=(24.5, 50.5), xytext=(23, 50.5), arrowprops=dict(arrowstyle="->", color='#ef4444', lw=1.8), zorder=8)

# Vue 3 Frontend (Dark Circle with Official Logo)
vue_circle = patches.Circle((32, 50), 6.8, facecolor='#0f172a', edgecolor='#334155', linewidth=2, zorder=4)
ax.add_patch(vue_circle)
draw_vue(ax, 32, 50.5, s=3.2)
ax.text(32, 41.5, "Vue 3 + Vite", fontsize=10, fontweight='bold', ha='center', va='center', color='#0f172a')
ax.text(32, 39.5, "Tailwind CSS SPA", fontsize=8, color='#64748b', ha='center', va='center')

# Arrow: Vue -> Traefik
ax.annotate('', xy=(44.5, 50.5), xytext=(39, 50.5), arrowprops=dict(arrowstyle="->", color='#ef4444', lw=1.8), zorder=8)

# Traefik / Nginx Gateway
traefik_rect = patches.Rectangle((45, 43), 14, 15, fill=False, edgecolor='#0284c7', linewidth=2, zorder=3)
ax.add_patch(traefik_rect)
draw_traefik_nginx(ax, 52, 51, s=3.4)
ax.text(52, 59.5, "Traefik / Nginx", fontsize=11, fontweight='bold', ha='center', va='center', color='#0f172a')
ax.text(52, 41.5, "Port 5173 Ingress", fontsize=8.5, color='#64748b', ha='center', va='center')

# Arrow: Traefik -> Authentication Server (OIDC/OAuth2/JWT)
ax.annotate('OIDC / OAuth2 (JWT)', xy=(76, 73.5), xytext=(59, 52),
            arrowprops=dict(arrowstyle="->", color='#ef4444', lw=2, connectionstyle="angle,angleA=0,angleB=90,rad=10"),
            fontsize=9.5, fontweight='bold', color='#dc2626', zorder=8)


# =============================================================================
# 4. CENTER: DJANGO BACKEND CORE (Green Hexagon/Shield)
# =============================================================================
draw_django(ax, 52, 26, s=5.2)
ax.text(52, 18.5, "Django REST Core", fontsize=12, fontweight='bold', ha='center', va='center', color='#092e20')
ax.text(52, 16.5, "Python 3.13 • Port 8000", fontsize=8.5, color='#15803d', ha='center', va='center')

# Arrow: Traefik -> Django Core
ax.annotate('', xy=(52, 32), xytext=(52, 43), arrowprops=dict(arrowstyle="->", color='#ef4444', lw=2), zorder=8)


# =============================================================================
# 5. MIDDLE RIGHT: DATABASE AND STORAGE (Dashed Red Box)
# =============================================================================
storage_rect = patches.Rectangle((67, 18), 30, 23, fill=False, edgecolor='#ef4444', linewidth=1.8, linestyle='--', zorder=2)
ax.add_patch(storage_rect)
ax.text(82, 42.5, "Database and storage", fontsize=12, fontweight='bold', ha='center', va='center', color='#0f172a')

# 1. PostgreSQL
draw_postgres(ax, 72.5, 30, s=3.0)
ax.text(72.5, 23.5, "PostgreSQL 18.4", fontsize=9, fontweight='bold', ha='center', va='center', color='#336791')
ax.text(72.5, 21.5, "Port 9927 (Data)", fontsize=7.5, color='#64748b', ha='center', va='center')

# 2. Redis
draw_redis(ax, 82, 30, s=2.8)
ax.text(82, 23.5, "Redis 7.0", fontsize=9, fontweight='bold', ha='center', va='center', color='#dc2626')
ax.text(82, 21.5, "Port 6380 (Cache)", fontsize=7.5, color='#64748b', ha='center', va='center')

# 3. Media Storage (Flamingo / MinIO)
draw_storage_media(ax, 91.5, 30, s=2.8)
ax.text(91.5, 23.5, "Media Volume", fontsize=9, fontweight='bold', ha='center', va='center', color='#e11d48')
ax.text(91.5, 21.5, "Evidence Crops", fontsize=7.5, color='#64748b', ha='center', va='center')

# Connecting dashed arrows inside storage
ax.annotate('', xy=(79, 30), xytext=(76.5, 30), arrowprops=dict(arrowstyle="->", color='#f59e0b', lw=1.5, linestyle='--'), zorder=8)
ax.annotate('', xy=(88.5, 30), xytext=(85.5, 30), arrowprops=dict(arrowstyle="->", color='#f59e0b', lw=1.5, linestyle='--'), zorder=8)

# Arrow: Django -> Storage
ax.annotate('', xy=(67, 28), xytext=(57.5, 28), arrowprops=dict(arrowstyle="->", color='#ef4444', lw=2), zorder=8)


# =============================================================================
# 6. BOTTOM LEFT: MONITORING TOOLS (Dashed Red Box)
# =============================================================================
mon_rect = patches.Rectangle((3, 3), 39, 14, fill=False, edgecolor='#ef4444', linewidth=1.8, linestyle='--', zorder=2)
ax.add_patch(mon_rect)
ax.text(22.5, 4.5, "Monitoring tools", fontsize=11.5, fontweight='bold', ha='center', va='center', color='#0f172a')

# 1. Grafana
draw_monitoring_grafana(ax, 9, 10.5, s=2.5)
ax.text(9, 6.5, "RedisInsight", fontsize=8.5, fontweight='bold', ha='center', va='center', color='#0284c7')

# 2. Prometheus
draw_monitoring_prometheus(ax, 22.5, 10.5, s=2.5)
ax.text(22.5, 6.5, "Adminer DB", fontsize=8.5, fontweight='bold', ha='center', va='center', color='#e11d48')

# 3. Loki Logs
draw_monitoring_loki(ax, 35, 10.5, s=2.5)
ax.text(35, 6.5, "Live Telemetry", fontsize=8.5, fontweight='bold', ha='center', va='center', color='#ca8a04')

# Arrows inside monitoring
ax.annotate('', xy=(19.5, 10.5), xytext=(12.5, 10.5), arrowprops=dict(arrowstyle="->", color='#f59e0b', lw=1.5, linestyle='--'), zorder=8)
ax.annotate('', xy=(31.5, 10.5), xytext=(26, 10.5), arrowprops=dict(arrowstyle="->", color='#f59e0b', lw=1.5, linestyle='--'), zorder=8)

# Arrow: Django -> Monitoring
ax.annotate('', xy=(22.5, 17), xytext=(47, 22),
            arrowprops=dict(arrowstyle="->", color='#ef4444', lw=2, connectionstyle="angle,angleA=180,angleB=90,rad=8"), zorder=8)


# Save high-res PNG image
output_path = Path("architecture_diagram.png")
plt.tight_layout()
plt.savefig(output_path, dpi=220, bbox_inches='tight', pad_inches=0.1)
print(f"SUCCESS: Generated authentic architecture diagram at {output_path.resolve()}")
