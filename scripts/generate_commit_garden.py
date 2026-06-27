import os
import json
import urllib.request
from datetime import datetime, timedelta, timezone

USERNAME = os.getenv("USERNAME", "yaren0600")
TOKEN = os.getenv("GITHUB_TOKEN")

if not TOKEN:
    raise RuntimeError("GITHUB_TOKEN bulunamadı.")

today = datetime.now(timezone.utc).date()
start_date = today - timedelta(days=365)

query = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        weeks {
          contributionDays {
            date
            contributionCount
            color
          }
        }
      }
    }
  }
}
"""

variables = {
    "login": USERNAME,
    "from": f"{start_date}T00:00:00Z",
    "to": f"{today}T23:59:59Z"
}

request_data = json.dumps({
    "query": query,
    "variables": variables
}).encode("utf-8")

request = urllib.request.Request(
    "https://api.github.com/graphql",
    data=request_data,
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    }
)

with urllib.request.urlopen(request) as response:
    result = json.loads(response.read().decode("utf-8"))

weeks = result["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]

CELL = 11
GAP = 4
LEFT = 52
TOP = 98

WIDTH = LEFT + len(weeks) * (CELL + GAP) + 55
HEIGHT = 370

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Pastel contribution renkleri
def contribution_color(count):
    if count == 0:
        return "#1a1d2e"
    if count <= 2:
        return "#3b4d63"
    if count <= 5:
        return "#5f7ea3"
    if count <= 9:
        return "#85b0c9"
    return "#b8e0d2"

def draw_sparkle(x, y, color, size=5):
    return f"""
  <line x1="{x}" y1="{y-size}" x2="{x}" y2="{y+size}" stroke="{color}" stroke-width="1.5" opacity="0.95"/>
  <line x1="{x-size}" y1="{y}" x2="{x+size}" y2="{y}" stroke="{color}" stroke-width="1.5" opacity="0.95"/>
"""

def draw_star(x, y, color):
    return f"""
  <circle cx="{x}" cy="{y}" r="1.6" fill="{color}" opacity="0.95"/>
  <line x1="{x}" y1="{y-4}" x2="{x}" y2="{y+4}" stroke="{color}" stroke-width="1.2" opacity="0.85"/>
  <line x1="{x-4}" y1="{y}" x2="{x+4}" y2="{y}" stroke="{color}" stroke-width="1.2" opacity="0.85"/>
"""

def draw_butterfly(x, y, scale=1.0, color="#f9a8d4"):
    return f"""
  <ellipse cx="{x-4*scale}" cy="{y-2*scale}" rx="{4*scale}" ry="{3*scale}" fill="{color}" opacity="0.9"/>
  <ellipse cx="{x+4*scale}" cy="{y-2*scale}" rx="{4*scale}" ry="{3*scale}" fill="{color}" opacity="0.9"/>
  <ellipse cx="{x-3*scale}" cy="{y+2*scale}" rx="{3*scale}" ry="{2.4*scale}" fill="#c084fc" opacity="0.9"/>
  <ellipse cx="{x+3*scale}" cy="{y+2*scale}" rx="{3*scale}" ry="{2.4*scale}" fill="#c084fc" opacity="0.9"/>
  <line x1="{x}" y1="{y-5*scale}" x2="{x}" y2="{y+5*scale}" stroke="#2e2a4d" stroke-width="1.2"/>
  <line x1="{x}" y1="{y-5*scale}" x2="{x-2.5*scale}" y2="{y-8*scale}" stroke="#2e2a4d" stroke-width="0.9"/>
  <line x1="{x}" y1="{y-5*scale}" x2="{x+2.5*scale}" y2="{y-8*scale}" stroke="#2e2a4d" stroke-width="0.9"/>
"""

def draw_grass_tuft(x, y, scale=1.0):
    return f"""
  <path d="M {x} {y} Q {x-3*scale} {y-10*scale} {x-5*scale} {y-2}"
        stroke="#86efac" stroke-width="1.5" fill="none"/>
  <path d="M {x} {y} Q {x+2*scale} {y-13*scale} {x+4*scale} {y-2}"
        stroke="#86efac" stroke-width="1.5" fill="none"/>
  <path d="M {x} {y} Q {x+6*scale} {y-9*scale} {x+8*scale} {y-2}"
        stroke="#4ade80" stroke-width="1.3" fill="none"/>
"""

def draw_flower(x, base_y, level, style, petal_color):
    stem = "#86efac"
    leaf = "#6ee7b7"
    center = "#fde68a"

    if level == 1:
        return f"""
  <line x1="{x}" y1="{base_y}" x2="{x}" y2="{base_y-18}" stroke="{stem}" stroke-width="2"/>
  <ellipse cx="{x-5}" cy="{base_y-10}" rx="5" ry="2.4" fill="{leaf}"/>
  <ellipse cx="{x+5}" cy="{base_y-14}" rx="5" ry="2.4" fill="{leaf}"/>
"""

    if level == 2:
        if style in ("tulip", "bud"):
            return f"""
  <line x1="{x}" y1="{base_y}" x2="{x}" y2="{base_y-28}" stroke="{stem}" stroke-width="2.2"/>
  <ellipse cx="{x-5}" cy="{base_y-13}" rx="5" ry="2.4" fill="{leaf}"/>
  <ellipse cx="{x+5}" cy="{base_y-19}" rx="5" ry="2.4" fill="{leaf}"/>
  <path d="M {x-7} {base_y-32} Q {x} {base_y-43} {x+7} {base_y-32} L {x+4} {base_y-24} Q {x} {base_y-28} {x-4} {base_y-24} Z"
        fill="{petal_color}"/>
"""
        else:
            return f"""
  <line x1="{x}" y1="{base_y}" x2="{x}" y2="{base_y-30}" stroke="{stem}" stroke-width="2.2"/>
  <ellipse cx="{x-5}" cy="{base_y-14}" rx="5" ry="2.4" fill="{leaf}"/>
  <ellipse cx="{x+5}" cy="{base_y-20}" rx="5" ry="2.4" fill="{leaf}"/>
  <circle cx="{x}" cy="{base_y-34}" r="3.7" fill="{center}"/>
  <circle cx="{x-5}" cy="{base_y-34}" r="3.7" fill="{petal_color}"/>
  <circle cx="{x+5}" cy="{base_y-34}" r="3.7" fill="{petal_color}"/>
  <circle cx="{x}" cy="{base_y-39}" r="3.7" fill="{petal_color}"/>
  <circle cx="{x}" cy="{base_y-29}" r="3.7" fill="{petal_color}"/>
"""

    if style == "sunflower":
        return f"""
  <line x1="{x}" y1="{base_y}" x2="{x}" y2="{base_y-47}" stroke="{stem}" stroke-width="3"/>
  <ellipse cx="{x-8}" cy="{base_y-18}" rx="7" ry="3.4" fill="{leaf}"/>
  <ellipse cx="{x+8}" cy="{base_y-27}" rx="7" ry="3.4" fill="{leaf}"/>
  <circle cx="{x}" cy="{base_y-54}" r="6" fill="#9a6b2f"/>
  <circle cx="{x-8}" cy="{base_y-54}" r="5" fill="{petal_color}"/>
  <circle cx="{x+8}" cy="{base_y-54}" r="5" fill="{petal_color}"/>
  <circle cx="{x}" cy="{base_y-63}" r="5" fill="{petal_color}"/>
  <circle cx="{x}" cy="{base_y-45}" r="5" fill="{petal_color}"/>
  <circle cx="{x-6}" cy="{base_y-61}" r="4.4" fill="{petal_color}"/>
  <circle cx="{x+6}" cy="{base_y-61}" r="4.4" fill="{petal_color}"/>
  <circle cx="{x-6}" cy="{base_y-47}" r="4.4" fill="{petal_color}"/>
  <circle cx="{x+6}" cy="{base_y-47}" r="4.4" fill="{petal_color}"/>
"""
    elif style == "blossom":
        return f"""
  <line x1="{x}" y1="{base_y}" x2="{x}" y2="{base_y-45}" stroke="{stem}" stroke-width="3"/>
  <ellipse cx="{x-8}" cy="{base_y-18}" rx="7" ry="3.4" fill="{leaf}"/>
  <ellipse cx="{x+8}" cy="{base_y-27}" rx="7" ry="3.4" fill="{leaf}"/>
  <circle cx="{x}" cy="{base_y-52}" r="5" fill="{center}"/>
  <circle cx="{x-8}" cy="{base_y-52}" r="5.7" fill="{petal_color}"/>
  <circle cx="{x+8}" cy="{base_y-52}" r="5.7" fill="{petal_color}"/>
  <circle cx="{x}" cy="{base_y-60}" r="5.7" fill="{petal_color}"/>
  <circle cx="{x}" cy="{base_y-44}" r="5.7" fill="{petal_color}"/>
  <circle cx="{x-6}" cy="{base_y-58}" r="4.7" fill="{petal_color}"/>
  <circle cx="{x+6}" cy="{base_y-58}" r="4.7" fill="{petal_color}"/>
"""
    else:
        return f"""
  <line x1="{x}" y1="{base_y}" x2="{x}" y2="{base_y-44}" stroke="{stem}" stroke-width="3"/>
  <ellipse cx="{x-8}" cy="{base_y-18}" rx="7" ry="3.4" fill="{leaf}"/>
  <ellipse cx="{x+8}" cy="{base_y-27}" rx="7" ry="3.4" fill="{leaf}"/>
  <path d="M {x-11} {base_y-49} Q {x} {base_y-66} {x+11} {base_y-49} L {x+7} {base_y-37} Q {x} {base_y-43} {x-7} {base_y-37} Z"
        fill="{petal_color}"/>
"""

# Ay etiketlerini daha sade göstermek için 2 ayda bir
month_starts = []
seen_month_positions = set()

for week_index, week in enumerate(weeks):
    for day in week["contributionDays"]:
        date = datetime.strptime(day["date"], "%Y-%m-%d").date()
        if date.day <= 7:
            month_name = months[date.month - 1]
            x = LEFT + week_index * (CELL + GAP)
            key = (date.year, date.month)
            if key not in seen_month_positions:
                seen_month_positions.add(key)
                month_starts.append((month_name, x))

display_months = month_starts[::2]

svg = f"""
<svg width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="softGlow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="4" result="blur1"/>
      <feMerge>
        <feMergeNode in="blur1"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <filter id="borderGlow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="6" result="blur2"/>
      <feMerge>
        <feMergeNode in="blur2"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0f1226"/>
      <stop offset="50%" stop-color="#171a33"/>
      <stop offset="100%" stop-color="#1d1b36"/>
    </linearGradient>

    <linearGradient id="groundTop" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#86efac"/>
      <stop offset="100%" stop-color="#4ade80"/>
    </linearGradient>

    <linearGradient id="soil" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#6b4c3b"/>
      <stop offset="100%" stop-color="#7b5540"/>
    </linearGradient>

    <linearGradient id="borderGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#f9a8d4"/>
      <stop offset="50%" stop-color="#d8b4fe"/>
      <stop offset="100%" stop-color="#a5b4fc"/>
    </linearGradient>
  </defs>

  <rect width="100%" height="100%" rx="26" fill="url(#bg)"/>

  <rect x="12" y="12" width="{WIDTH-24}" height="{HEIGHT-24}" rx="26"
        fill="none" stroke="url(#borderGrad)" stroke-opacity="0.9"
        stroke-width="2.2" filter="url(#borderGlow)"/>

  <text x="{WIDTH/2}" y="38" text-anchor="middle"
        fill="#f9a8d4" font-family="monospace" font-size="20" font-weight="bold" filter="url(#softGlow)">
    🌷 Commit Garden 🌷
  </text>

  <text x="{WIDTH/2}" y="60" text-anchor="middle"
        fill="#ddd6fe" font-family="monospace" font-size="12">
    Growing through every commit
  </text>
"""

# Üst ve alt dekorlar
svg += draw_sparkle(30, 38, "#f9a8d4", 5)
svg += draw_sparkle(WIDTH - 30, 42, "#c084fc", 5)
svg += draw_star(55, HEIGHT - 42, "#fde68a")
svg += draw_star(WIDTH - 58, HEIGHT - 45, "#f9a8d4")
svg += draw_star(WIDTH - 85, 72, "#c4b5fd")

# Minik kelebekler
svg += draw_butterfly(78, 72, 0.9, "#f9a8d4")
svg += draw_butterfly(WIDTH - 92, 86, 0.8, "#f472b6")

# Aylar
for month, x in display_months:
    svg += f"""
  <text x="{x}" y="{TOP - 14}" fill="#e9d5ff"
        font-family="monospace" font-size="11" opacity="0.95">{month}</text>
"""

# Contribution grid
for week_index, week in enumerate(weeks):
    for day_index, day in enumerate(week["contributionDays"]):
        x = LEFT + week_index * (CELL + GAP)
        y = TOP + day_index * (CELL + GAP)
        count = day["contributionCount"]
        color = contribution_color(count)

        svg += f"""
  <rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3.2"
        fill="{color}" opacity="0.95">
    <title>{day["date"]}: {count} contribution(s)</title>
  </rect>
"""

GROUND_Y = TOP + 7 * (CELL + GAP) + 56

# Zemin
svg += f"""
  <rect x="{LEFT-12}" y="{GROUND_Y}" width="{WIDTH-LEFT-38}" height="7"
        rx="4" fill="url(#groundTop)"/>
  <rect x="{LEFT-12}" y="{GROUND_Y+7}" width="{WIDTH-LEFT-38}" height="10"
        rx="2" fill="url(#soil)" opacity="0.92"/>
"""

# Çimenler
for week_index in range(0, len(weeks), 2):
    gx = LEFT + week_index * (CELL + GAP) + 4
    scale = 0.8 + (week_index % 3) * 0.12
    svg += draw_grass_tuft(gx, GROUND_Y + 1, scale)

# Sabit pastel pembe-mor palette
flower_colors = ["#f9a8d4", "#f472b6", "#d8b4fe", "#c084fc", "#f5b0ff"]
flower_styles = ["blossom", "tulip", "blossom", "tulip", "sunflower"]

# Haftalık toplam contribution'a göre çiçekler
for week_index, week in enumerate(weeks):
    weekly_total = sum(day["contributionCount"] for day in week["contributionDays"])

    if weekly_total == 0:
        continue

    x = LEFT + week_index * (CELL + GAP) + CELL / 2

    if weekly_total <= 2:
        level = 1
    elif weekly_total <= 8:
        level = 2
    else:
        level = 3

    color = flower_colors[week_index % len(flower_colors)]
    style = flower_styles[week_index % len(flower_styles)]

    # Çok yoğun haftalarda daha dolgun çiçek
    if weekly_total >= 15:
        style = "blossom"

    svg += draw_flower(x, GROUND_Y, level, style, color)

# Alt dekor
svg += draw_butterfly(WIDTH / 2 + 140, HEIGHT - 58, 0.7, "#d8b4fe")
svg += draw_sparkle(WIDTH / 2 - 170, HEIGHT - 44, "#f9a8d4", 4)
svg += draw_sparkle(WIDTH / 2 + 175, HEIGHT - 40, "#fde68a", 4)

svg += f"""
  <text x="{WIDTH/2}" y="{HEIGHT-28}" text-anchor="middle"
        fill="#d9f99d" font-family="monospace" font-size="14">
    Every commit grows something new 🌱
  </text>
</svg>
"""

os.makedirs("assets", exist_ok=True)

with open("assets/commit-garden.svg", "w", encoding="utf-8") as file:
    file.write(svg.strip())

print("Commit garden generated successfully.")
