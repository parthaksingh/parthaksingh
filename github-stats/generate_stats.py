import os
import requests
from datetime import datetime, timedelta

USERNAME = "parthaksingh"
OUTPUT_FILE = "github-stats/stats.svg"

TOKEN = os.getenv("GITHUB_TOKEN")

if not TOKEN:
    raise RuntimeError("GITHUB_TOKEN is not available")

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }

    repositories(
      first: 1
      ownerAffiliations: OWNER
      privacy: PUBLIC
    ) {
      totalCount
    }

    followers {
      totalCount
    }
  }
}
"""

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

response = requests.post(
    "https://api.github.com/graphql",
    json={
        "query": QUERY,
        "variables": {
            "login": USERNAME
        }
    },
    headers=headers,
    timeout=30
)

response.raise_for_status()

data = response.json()

if "errors" in data:
    raise RuntimeError(data["errors"])

user = data["data"]["user"]

calendar = user["contributionsCollection"]["contributionCalendar"]

total_contributions = calendar["totalContributions"]

public_repositories = user["repositories"]["totalCount"]

followers = user["followers"]["totalCount"]


# Get contribution dates

contribution_days = []

for week in calendar["weeks"]:
    for day in week["contributionDays"]:

        if day["contributionCount"] > 0:
            contribution_days.append(
                datetime.strptime(
                    day["date"],
                    "%Y-%m-%d"
                ).date()
            )

contribution_days.sort()


# Current streak

today = datetime.utcnow().date()

current_streak = 0

if contribution_days:

    latest = contribution_days[-1]

    if latest == today:
        check_date = today

    elif latest == today - timedelta(days=1):
        check_date = today - timedelta(days=1)

    else:
        check_date = None

    if check_date:

        contribution_set = set(contribution_days)

        while check_date in contribution_set:
            current_streak += 1
            check_date -= timedelta(days=1)


# Longest streak

longest_streak = 0
running_streak = 0
previous_date = None

for date in contribution_days:

    if previous_date is not None:

        if date == previous_date + timedelta(days=1):
            running_streak += 1

        else:
            running_streak = 1

    else:
        running_streak = 1

    longest_streak = max(
        longest_streak,
        running_streak
    )

    previous_date = date


# Date range

if contribution_days:

    first_date = contribution_days[0].strftime(
        "%b %d, %Y"
    )

    last_date = contribution_days[-1].strftime(
        "%b %d, %Y"
    )

else:

    first_date = "N/A"
    last_date = "N/A"


updated = datetime.utcnow().strftime(
    "%b %d, %Y"
)


# Generate SVG

svg = f'''<svg
width="900"
height="390"
viewBox="0 0 900 390"
xmlns="http://www.w3.org/2000/svg">

<rect
width="900"
height="390"
rx="18"
fill="#0d1117"
/>

<rect
x="25"
y="25"
width="850"
height="340"
rx="18"
fill="#161b22"
stroke="#30363d"
/>


<!-- Header -->

<text
x="60"
y="75"
font-family="Arial, sans-serif"
font-size="27"
font-weight="700"
fill="#f0f6fc">
GitHub Activity
</text>

<text
x="60"
y="105"
font-family="Arial, sans-serif"
font-size="14"
fill="#8b949e">
@{USERNAME} • Live contribution statistics
</text>


<!-- Divider -->

<line
x1="60"
y1="130"
x2="840"
y2="130"
stroke="#30363d"
/>


<!-- Vertical dividers -->

<line
x1="310"
y1="155"
x2="310"
y2="300"
stroke="#30363d"
/>

<line
x1="590"
y1="155"
x2="590"
y2="300"
stroke="#30363d"
/>


<!-- Total Contributions -->

<text
x="185"
y="195"
text-anchor="middle"
font-family="Arial, sans-serif"
font-size="38"
font-weight="700"
fill="#58a6ff">
{total_contributions}
</text>

<text
x="185"
y="225"
text-anchor="middle"
font-family="Arial, sans-serif"
font-size="15"
font-weight="600"
fill="#8b949e">
Total Contributions
</text>

<text
x="185"
y="252"
text-anchor="middle"
font-family="Arial, sans-serif"
font-size="13"
fill="#3fb950">
{first_date} - Present
</text>


<!-- Current Streak -->

<circle
cx="450"
cy="205"
r="52"
fill="none"
stroke="#58a6ff"
stroke-width="6"
/>

<text
x="450"
y="218"
text-anchor="middle"
font-family="Arial, sans-serif"
font-size="38"
font-weight="700"
fill="#bc8cff">
{current_streak}
</text>

<text
x="450"
y="270"
text-anchor="middle"
font-family="Arial, sans-serif"
font-size="15"
font-weight="600"
fill="#bc8cff">
Current Streak
</text>


<!-- Longest Streak -->

<text
x="700"
y="195"
text-anchor="middle"
font-family="Arial, sans-serif"
font-size="38"
font-weight="700"
fill="#58a6ff">
{longest_streak}
</text>

<text
x="700"
y="225"
text-anchor="middle"
font-family="Arial, sans-serif"
font-size="15"
font-weight="600"
fill="#8b949e">
Longest Streak
</text>

<text
x="700"
y="252"
text-anchor="middle"
font-family="Arial, sans-serif"
font-size="13"
fill="#3fb950">
Contribution streak
</text>


<!-- Footer -->

<line
x1="60"
y1="310"
x2="840"
y2="310"
stroke="#30363d"
/>

<text
x="450"
y="340"
text-anchor="middle"
font-family="Arial, sans-serif"
font-size="12"
fill="#8b949e">
Automatically updated from GitHub • Last updated {updated} UTC
</text>

</svg>
'''

os.makedirs(
    "github-stats",
    exist_ok=True
)

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as file:

    file.write(svg)


print("GitHub stats generated successfully!")

print(
    f"Total Contributions: {total_contributions}"
)

print(
    f"Current Streak: {current_streak}"
)

print(
    f"Longest Streak: {longest_streak}"
)

print(
    f"Public Repositories: {public_repositories}"
)

print(
    f"Followers: {followers}"
)
