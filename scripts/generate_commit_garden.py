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
LEFT = 55
TOP = 60

WIDTH = LEFT + len(weeks) * (CELL + GAP) + 55
HEIGHT = 330

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

svg = f"""
<svg width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" xmlns="http://www.w3.org/2000/svg">

  <defs>
    <filter id="glow">
      <feGaussianBlur stdDeviation="2.5" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>

    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0d1117"/>
      <stop offset="100%" stop-color="#1e1e2f"/>
    </linearGradient>
  </defs>

  <rect width="100%" height="100%" rx="24" fill="url(#bg)"/>
  <rect x="12" y="12" width="{WIDTH-24}" height="{HEIGHT-24}" rx="24"
        fill="none" stroke="#ff9ff3" stroke-opacity="0.35" stroke-width="2"/>

  <text x="{WIDTH/2}" y="35" text-anchor="middle"
        fill="#ff9ff3" font-family="monospace" font-size="18" font-weight="bold">
    🌷 Commit Garden 🌷
  </text>

  <text x="{WIDTH/2}" y="56" text-anchor="middle"
        fill="#c9d1d9" font-family="monospace" font-size="12">
    Growing through every commit
  </text>
"""

month_positions = {}
for week_index, week in enumerate(weeks):
    for day in week["contributionDays"]:
        date = datetime.strptime(day["date"], "%Y-%m-%d").date()
        month_name = months[date.month - 1]

        if date.day <= 7 and month_name not in month_positions:
            month_positions[month_name] = LEFT + week_index * (CELL + GAP)

for month, x in month_positions.items():
    svg += f"""
  <text x="{x}" y="{TOP - 12}" fill="#c9d1d9"
        font-family="monospace" font-size="11">{month}</text>
"""

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

# Contribution kutuları
for week_index, week in enumerate(weeks):
    for day_index, day in enumerate(week["contributionDays"]):
        x = LEFT + week_index * (CELL + GAP)
        y = TOP + day_index * (CELL + GAP)
        count = day["contributionCount"]
        color = contribution_color(count)

        svg += f"""
  <rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3"
        fill="{color}" opacity="0.85">
    <title>{day["date"]}: {count} contribution</title>
  </rect>
"""

GROUND_Y = TOP + 7 * (CELL + GAP) + 52

svg += f"""
  <rect x="{LEFT-15}" y="{GROUND_Y}" width="{WIDTH-LEFT-40}" height="7"
        rx="4" fill="#238636"/>
  <rect x="{LEFT-15}" y="{GROUND_Y+7}" width="{WIDTH-LEFT-40}" height="9"
        rx="2" fill="#4b2e1f" opacity="0.75"/>
"""

def draw_flower(x, base_y, level, color="#ff9ff3"):
    if level == 0:
        return ""

    if level == 1:
        return f"""
  <line x1="{x}" y1="{base_y}" x2="{x}" y2="{base_y-18}" stroke="#4ade80" stroke-width="2"/>
  <ellipse cx="{x-5}" cy="{base_y-10}" rx="6" ry="3" fill="#7ee787"/>
  <ellipse cx="{x+5}" cy="{base_y-15}" rx="6" ry="3" fill="#7ee787"/>
"""

    if level == 2:
        return f"""
  <line x1="{x}" y1="{base_y}" x2="{x}" y2="{base_y-30}" stroke="#4ade80" stroke-width="2"/>
  <ellipse cx="{x-6}" cy="{base_y-15}" rx="6" ry="3" fill="#7ee787"/>
  <ellipse cx="{x+6}" cy="{base_y-22}" rx="6" ry="3" fill="#7ee787"/>
  <circle cx="{x}" cy="{base_y-34}" r="4" fill="#ffd166"/>
  <circle cx="{x-5}" cy="{base_y-34}" r="4" fill="{color}"/>
  <circle cx="{x+5}" cy="{base_y-34}" r="4" fill="{color}"/>
  <circle cx="{x}" cy="{base_y-39}" r="4" fill="{color}"/>
  <circle cx="{x}" cy="{base_y-29}" r="4" fill="{color}"/>
"""

    return f"""
  <line x1="{x}" y1="{base_y}" x2="{x}" y2="{base_y-45}" stroke="#4ade80" stroke-width="3"/>
  <ellipse cx="{x-8}" cy="{base_y-18}" rx="8" ry="4" fill="#7ee787"/>
  <ellipse cx="{x+8}" cy="{base_y-28}" rx="8" ry="4" fill="#7ee787"/>
  <circle cx="{x}" cy="{base_y-51}" r="5" fill="#ffd166"/>
  <circle cx="{x-7}" cy="{base_y-51}" r="6" fill="{color}"/>
  <circle cx="{x+7}" cy="{base_y-51}" r="6" fill="{color}"/>
  <circle cx="{x}" cy="{base_y-58}" r="6" fill="{color}"/>
  <circle cx="{x}" cy="{base_y-44}" r="6" fill="{color}"/>
"""

flower_colors = ["#ff9ff3", "#f78fb3", "#c084fc", "#facc15", "#fb7185"]

# Haftalık toplam contribution'a göre düzenli çiçekler
for week_index, week in enumerate(weeks):
    weekly_total = sum(day["contributionCount"] for day in week["contributionDays"])

    if weekly_total == 0:
        continue

    x = LEFT + week_index * (CELL + GAP) + CELL / 2
    color = flower_colors[week_index % len(flower_colors)]

    if weekly_total <= 2:
        level = 1
    elif weekly_total <= 8:
        level = 2
    else:
        level = 3

    svg += draw_flower(x, GROUND_Y, level, color)

svg += f"""
  <text x="{WIDTH/2}" y="{HEIGHT-28}" text-anchor="middle"
        fill="#a3e635" font-family="monospace" font-size="14">
    Every commit grows something new 🌱
  </text>

</svg>
"""

os.makedirs("assets", exist_ok=True)

with open("assets/commit-garden.svg", "w", encoding="utf-8") as file:
    file.write(svg.strip())

print("Commit garden generated successfully.")
