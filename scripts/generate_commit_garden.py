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
HEIGHT = 360

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

def contribution_color(count):
    if count == 0:
        return "#161b22"
    if count <= 2:
        return "#0e4429"
    if count <= 5:
        return "#006d32"
    if count <= 9:
        return "#26a641"
    return "#39d353"

def draw_sparkle(x, y, color):
    return f"""
  <line x1="{x}" y1="{y-5}" x2="{x}" y2="{y+5}" stroke="{color}" stroke-width="1.5" opacity="0.9"/>
  <line x1="{x-5}" y1="{y}" x2="{x+5}" y2="{y}" stroke="{color}" stroke-width="1.5" opacity="0.9"/>
"""

def draw_grass_tuft(x, y, scale=1.0):
    h1 = 10 * scale
    h2 = 14 * scale
    h3 = 9 * scale
    return f"""
  <path d="M {x} {y} Q {x-3*scale} {y-h1} {x-5*scale} {y-2}"
        stroke="#7ee787" stroke-width="1.6" fill="none"/>
  <path d="M {x} {y} Q {x+2*scale} {y-h2} {x+4*scale} {y-2}"
        stroke="#7ee787" stroke-width="1.6" fill="none"/>
  <path d="M {x} {y} Q {x+6*scale} {y-h3} {x+8*scale} {y-2}"
        stroke="#56d364" stroke-width="1.4" fill="none"/>
"""

def draw_flower(x, base_y, level, style, petal_color):
    stem = "#7ee787"
    leaf = "#56d364"
    center = "#ffd166"

    if level == 1:
        return f"""
  <line x1="{x}" y1="{base_y}" x2="{x}" y2="{base_y-18}" stroke="{stem}" stroke-width="2"/>
  <ellipse cx="{x-5}" cy="{base_y-10}" rx="5" ry="2.5" fill="{leaf}"/>
  <ellipse cx="{x+5}" cy="{base_y-14}" rx="5" ry="2.5" fill="{leaf}"/>
"""

    if level == 2:
        # küçük çiçek / lale
        if style in ("tulip", "bud"):
            return f"""
  <line x1="{x}" y1="{base_y}" x2="{x}" y2="{base_y-27}" stroke="{stem}" stroke-width="2.2"/>
  <ellipse cx="{x-5}" cy="{base_y-13}" rx="5" ry="2.5" fill="{leaf}"/>
  <ellipse cx="{x+5}" cy="{base_y-19}" rx="5" ry="2.5" fill="{leaf}"/>
  <path d="M {x-7} {base_y-31} Q {x} {base_y-42} {x+7} {base_y-31} L {x+4} {base_y-23} Q {x} {base_y-27} {x-4} {base_y-23} Z"
        fill="{petal_color}"/>
"""
        else:
            return f"""
  <line x1="{x}" y1="{base_y}" x2="{x}" y2="{base_y-29}" stroke="{stem}" stroke-width="2.2"/>
  <ellipse cx="{x-5}" cy="{base_y-14}" rx="5" ry="2.5" fill="{leaf}"/>
  <ellipse cx="{x+5}" cy="{base_y-20}" rx="5" ry="2.5" fill="{leaf}"/>
  <circle cx="{x}" cy="{base_y-33}" r="3.8" fill="{center}"/>
  <circle cx="{x-5}" cy="{base_y-33}" r="3.8" fill="{petal_color}"/>
  <circle cx="{x+5}" cy="{base_y-33}" r="3.8" fill="{petal_color}"/>
  <circle cx="{x}" cy="{base_y-38}" r="3.8" fill="{petal_color}"/>
  <circle cx="{x}" cy="{base_y-28}" r="3.8" fill="{petal_color}"/>
"""

    # büyük çiçek
    if style == "sunflower":
        return f"""
  <line x1="{x}" y1="{base_y}" x2="{x}" y2="{base_y-47}" stroke="{stem}" stroke-width="3"/>
  <ellipse cx="{x-8}" cy="{base_y-18}" rx="7" ry="3.4" fill="{leaf}"/>
  <ellipse cx="{x+8}" cy="{base_y-27}" rx="7" ry="3.4" fill="{leaf}"/>
  <circle cx="{x}" cy="{base_y-54}" r="6.2" fill="#8b5a2b"/>
  <circle cx="{x-8}" cy="{base_y-54}" r="5" fill="{petal_color}"/>
  <circle cx="{x+8}" cy="{base_y-54}" r="5" fill="{petal_color}"/>
  <circle cx="{x}" cy="{base_y-63}" r="5" fill="{petal_color}"/>
  <circle cx="{x}" cy="{base_y-45}" r="5" fill="{petal_color}"/>
  <circle cx="{x-6}" cy="{base_y-61}" r="4.5" fill="{petal_color}"/>
  <circle cx="{x+6}" cy="{base_y-61}" r="4.5" fill="{petal_color}"/>
  <circle cx="{x-6}" cy="{base_y-47}" r="4.5" fill="{petal_color}"/>
  <circle cx="{x+6}" cy="{base_y-47}" r="4.5" fill="{petal_color}"/>
"""
    elif style == "blossom":
        return f"""
  <line x1="{x}" y1="{base_y}" x2="{x}" y2="{base_y-45}" stroke="{stem}" stroke-width="3"/>
  <ellipse cx="{x-8}" cy="{base_y-18}" rx="7" ry="3.4" fill="{leaf}"/>
  <ellipse cx="{x+8}" cy="{base_y-27}" rx="7" ry="3.4" fill="{leaf}"/>
  <circle cx="{x}" cy="{base_y-52}" r="5" fill="{center}"/>
  <circle cx="{x-8}" cy="{base_y-52}" r="5.8" fill="{petal_color}"/>
  <circle cx="{x+8}" cy="{base_y-52}" r="5.8" fill="{petal_color}"/>
  <circle cx="{x}" cy="{base_y-60}" r="5.8" fill="{petal_color}"/>
  <circle cx="{x}" cy="{base_y-44}" r="5.8" fill="{petal_color}"/>
  <circle cx="{x-6}" cy="{base_y-58}" r="4.8" fill="{petal_color}"/>
  <circle cx="{x+6}" cy="{base_y-58}" r="4.8" fill="{petal_color}"/>
"""
    else:
        # büyük lale
        return f"""
  <line x1="{x}" y1="{base_y}" x2="{x}" y2="{base_y-44}" stroke="{stem}" stroke-width="3"/>
  <ellipse cx="{x-8}" cy="{base_y-18}" rx="7" ry="3.4" fill="{leaf}"/>
  <ellipse cx="{x+8}" cy="{base_y-27}" rx="7" ry="3.4" fill="{leaf}"/>
  <path d="M {x-11} {base_y-49} Q {x} {base_y-66} {x+11} {base_y-49} L {x+7} {base_y-37} Q {x} {base_y-43} {x-7} {base_y-37} Z"
        fill="{petal_color}"/>
"""

# Ay etiketleri - daha sade olsun diye her 2 ayda bir gösterelim
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
    <filter id="glow">
      <feGaussianBlur stdDeviation="2.2" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0d1117"/>
      <stop offset="100%" stop-color="#1a1b2e"/>
    </linearGradient>

    <linearGradient id="groundTop" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#22c55e"/>
      <stop offset="100%" stop-color="#16a34a"/>
    </linearGradient>

    <linearGradient id="soil" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#5b3a29"/>
      <stop offset="100%" stop-color="#6f442d"/>
    </linearGradient>
  </defs>

  <rect width="100%" height="100%" rx="26" fill="url(#bg)"/>
  <rect x="12" y="12" width="{WIDTH-24}" height="{HEIGHT-24}" rx="26"
        fill="none" stroke="#ff9ff3" stroke-opacity="0.35" stroke-width="2"/>

  <text x="{WIDTH/2}" y="38" text-anchor="middle"
        fill="#ff9ff3" font-family="monospace" font-size="20" font-weight="bold">
    🌷 Commit Garden 🌷
  </text>

  <text x="{WIDTH/2}" y="60" text-anchor="middle"
        fill="#d8b4fe" font-family="monospace" font-size="12">
    Growing through every commit
  </text>
"""

# Sparkles
svg += draw_sparkle(32, 38, "#f9a8d4")
svg += draw_sparkle(WIDTH - 32, 44, "#c084fc")
svg += draw_sparkle(WIDTH - 65, HEIGHT - 42, "#fcd34d")
svg += draw_sparkle(46, HEIGHT - 48, "#86efac")

# Ay etiketleri
for month, x in display_months:
    svg += f"""
  <text x="{x}" y="{TOP - 14}" fill="#c9d1d9"
        font-family="monospace" font-size="11" opacity="0.9">{month}</text>
"""

# Contribution grid
for week_index, week in enumerate(weeks):
    for day_index, day in enumerate(week["contributionDays"]):
        x = LEFT + week_index * (CELL + GAP)
        y = TOP + day_index * (CELL + GAP)
        count = day["contributionCount"]
        color = contribution_color(count)

        svg += f"""
  <rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3"
        fill="{color}" opacity="0.9">
    <title>{day["date"]}: {count} contribution(s)</title>
  </rect>
"""

GROUND_Y = TOP + 7 * (CELL + GAP) + 56

# Zemin
svg += f"""
  <rect x="{LEFT-12}" y="{GROUND_Y}" width="{WIDTH-LEFT-38}" height="7"
        rx="4" fill="url(#groundTop)"/>
  <rect x="{LEFT-12}" y="{GROUND_Y+7}" width="{WIDTH-LEFT-38}" height="10"
        rx="2" fill="url(#soil)" opacity="0.9"/>
"""

# Çimenler
for week_index in range(0, len(weeks), 2):
    gx = LEFT + week_index * (CELL + GAP) + 4
    scale = 0.8 + (week_index % 3) * 0.15
    svg += draw_grass_tuft(gx, GROUND_Y + 1, scale)

# Haftalık toplam contribution'a göre çiçekler
flower_colors = ["#f9a8d4", "#f472b6", "#c084fc", "#facc15", "#fb7185", "#fdba74"]
flower_styles = ["blossom", "tulip", "sunflower", "blossom", "tulip"]

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

    # Çok yoğun haftalarda sunflower zorla
    if weekly_total >= 15:
        style = "sunflower"

    svg += draw_flower(x, GROUND_Y, level, style, color)

svg += f"""
  <text x="{WIDTH/2}" y="{HEIGHT-28}" text-anchor="middle"
        fill="#bef264" font-family="monospace" font-size="14">
    Every commit grows something new 🌱
  </text>
</svg>
"""

os.makedirs("assets", exist_ok=True)

with open("assets/commit-garden.svg", "w", encoding="utf-8") as file:
    file.write(svg.strip())

print("Commit garden generated successfully.")
