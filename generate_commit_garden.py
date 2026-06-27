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

data = json.dumps({
    "query": query,
    "variables": variables
}).encode("utf-8")

request = urllib.request.Request(
    "https://api.github.com/graphql",
    data=data,
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    }
)

with urllib.request.urlopen(request) as response:
    result = json.loads(response.read().decode("utf-8"))

weeks = result["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]

cell = 14
gap = 4
left = 40
top = 50
width = left + len(weeks) * (cell + gap) + 40
height = 260

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

svg = f"""
<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
  <rect width="100%" height="100%" rx="22" fill="#0d1117"/>
  <rect x="10" y="10" width="{width-20}" height="{height-20}" rx="22" fill="none" stroke="#30363d" stroke-width="2"/>

  <text x="{width/2}" y="32" text-anchor="middle" fill="#ff9ff3" font-family="monospace" font-size="18">
    🌷 Growing through every commit 🌷
  </text>
"""

month_positions = {}
for week_index, week in enumerate(weeks):
    for day in week["contributionDays"]:
        date = datetime.strptime(day["date"], "%Y-%m-%d").date()
        month_name = months[date.month - 1]
        if date.day <= 7 and month_name not in month_positions:
            month_positions[month_name] = left + week_index * (cell + gap)

for month, x in month_positions.items():
    svg += f'<text x="{x}" y="54" fill="#c9d1d9" font-family="monospace" font-size="13">{month}</text>\n'

def draw_sprout(x, y, count):
    ground_y = y + cell + 32

    if count == 0:
        return f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="#161b22"/>\n'

    base = f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="#1f6f3a" opacity="0.75"/>\n'

    if count == 1:
        return base + f"""
        <line x1="{x+7}" y1="{ground_y}" x2="{x+7}" y2="{ground_y-12}" stroke="#4ade80" stroke-width="2"/>
        <ellipse cx="{x+4}" cy="{ground_y-9}" rx="4" ry="2" fill="#7ee787"/>
        <ellipse cx="{x+10}" cy="{ground_y-13}" rx="4" ry="2" fill="#7ee787"/>
        """

    if count <= 3:
        return base + f"""
        <line x1="{x+7}" y1="{ground_y}" x2="{x+7}" y2="{ground_y-20}" stroke="#4ade80" stroke-width="2"/>
        <ellipse cx="{x+3}" cy="{ground_y-13}" rx="5" ry="3" fill="#7ee787"/>
        <ellipse cx="{x+11}" cy="{ground_y-18}" rx="5" ry="3" fill="#7ee787"/>
        <circle cx="{x+7}" cy="{ground_y-24}" r="4" fill="#ff9ff3"/>
        """

    if count <= 6:
        return base + f"""
        <line x1="{x+7}" y1="{ground_y}" x2="{x+7}" y2="{ground_y-28}" stroke="#4ade80" stroke-width="2"/>
        <ellipse cx="{x+2}" cy="{ground_y-15}" rx="5" ry="3" fill="#7ee787"/>
        <ellipse cx="{x+12}" cy="{ground_y-21}" rx="5" ry="3" fill="#7ee787"/>
        <circle cx="{x+7}" cy="{ground_y-31}" r="3" fill="#ffd166"/>
        <circle cx="{x+3}" cy="{ground_y-31}" r="3" fill="#ff6ec7"/>
        <circle cx="{x+11}" cy="{ground_y-31}" r="3" fill="#ff6ec7"/>
        <circle cx="{x+7}" cy="{ground_y-35}" r="3" fill="#ff6ec7"/>
        <circle cx="{x+7}" cy="{ground_y-27}" r="3" fill="#ff6ec7"/>
        """

    return base + f"""
    <line x1="{x+7}" y1="{ground_y}" x2="{x+7}" y2="{ground_y-36}" stroke="#4ade80" stroke-width="2"/>
    <ellipse cx="{x+1}" cy="{ground_y-17}" rx="6" ry="3" fill="#7ee787"/>
    <ellipse cx="{x+13}" cy="{ground_y-25}" rx="6" ry="3" fill="#7ee787"/>
    <circle cx="{x+7}" cy="{ground_y-40}" r="4" fill="#ffd166"/>
    <circle cx="{x+2}" cy="{ground_y-40}" r="4" fill="#f78fb3"/>
    <circle cx="{x+12}" cy="{ground_y-40}" r="4" fill="#f78fb3"/>
    <circle cx="{x+7}" cy="{ground_y-45}" r="4" fill="#f78fb3"/>
    <circle cx="{x+7}" cy="{ground_y-35}" r="4" fill="#f78fb3"/>
    """

for week_index, week in enumerate(weeks):
    for day_index, day in enumerate(week["contributionDays"]):
        x = left + week_index * (cell + gap)
        y = top + 18 + day_index * (cell + gap)
        count = day["contributionCount"]
        svg += draw_sprout(x, y, count)

ground_y = top + 18 + 7 * (cell + gap) + 32
svg += f"""
  <rect x="{left-10}" y="{ground_y}" width="{width-left-60}" height="6" rx="3" fill="#238636"/>
  <text x="{width/2}" y="{height-28}" text-anchor="middle" fill="#a3e635" font-family="monospace" font-size="15">
    Every commit grows something new 🌱
  </text>
</svg>
"""

os.makedirs("assets", exist_ok=True)

with open("assets/commit-garden.svg", "w", encoding="utf-8") as file:
    file.write(svg.strip())

print("Commit garden generated successfully.")
