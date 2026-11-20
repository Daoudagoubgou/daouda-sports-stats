
import time
import requests

from datetime import date, timedelta
from flask import Flask, request, render_template_string, url_for
from config import API_FOOTBALL_KEY, API_FOOTBALL_URL

app = Flask(__name__)

# ==========================================
# CONFIGURATION
# ==========================================

BASE_URL = API_FOOTBALL_URL.rstrip("/")
HEADERS = {"x-apisports-key": API_FOOTBALL_KEY}

CACHE = {}
CACHE_TIME = 30


# ==========================================
# CONNEXION API FOOTBALL
# ==========================================

def api(endpoint, params=None):
    if not API_FOOTBALL_KEY:
        return []

    params = params or {}
    key = (endpoint, tuple(sorted(params.items())))
    now = time.time()

    if key in CACHE:
        saved_time, result = CACHE[key]
        if now - saved_time < CACHE_TIME:
            return result

    try:
        response = requests.get(
            f"{BASE_URL}/{endpoint}",
            headers=HEADERS,
            params=params,
            timeout=20
        )

        response.raise_for_status()
        data = response.json()

        if data.get("errors"):
            print("API ERROR:", data["errors"])
            return []

        result = data.get("response", [])
        CACHE[key] = (now, result)

        return result

    except requests.RequestException as error:
        print("CONNECTION ERROR:", error)
        return []


# ==========================================
# RECUPERATION DES MATCHS
# ==========================================

def get_matches(day=None):

    day = day or date.today().isoformat()

    live = api("fixtures", {"live": "all"})
    today = api("fixtures", {"date": day})

    matches = {}

    for match in live + today:
        fixture_id = match["fixture"]["id"]
        matches[fixture_id] = match

    return list(matches.values())


# ==========================================
# CLASSEMENT PAR CHAMPIONNAT
# ==========================================

def group_matches(matches):

    groups = {}

    for match in matches:

        league = match.get("league", {})

        league_id = league.get("id")

        if league_id not in groups:
            groups[league_id] = {
                "name": league.get("name"),
                "country": league.get("country"),
                "logo": league.get("logo"),
                "flag": league.get("flag"),
                "matches": []
            }

        groups[league_id]["matches"].append(match)

    return groups


# ==========================================
# DESIGN GENERAL
# ==========================================

PAGE = """
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<title>{{ title }} | Daouda Sports Stats</title>

<meta http-equiv="refresh" content="60">

<style>

:root {
    --bg: #101820;
    --panel: #192630;
    --panel2: #22323e;
    --green: #00d58a;
    --text: #f4f7fa;
    --muted: #9aabb7;
    --border: #30414d;
}

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font-family: Arial, sans-serif;
}

header {
    background: #15232d;
    border-bottom: 1px solid var(--border);
    padding: 16px;
    position: sticky;
    top: 0;
    z-index: 10;
}

.logo {
    color: var(--green);
    font-size: 21px;
    font-weight: bold;
}

nav {
    display: flex;
    gap: 20px;
    overflow-x: auto;
    margin-top: 15px;
}

nav a {
    color: var(--muted);
    text-decoration: none;
    white-space: nowrap;
    font-size: 14px;
}

nav a:hover {
    color: var(--green);
}

.container {
    max-width: 950px;
    margin: auto;
    padding: 15px;
}

h2 {
    font-size: 19px;
}

.datebar {
    display: flex;
    gap: 10px;
    align-items: center;
    margin: 15px 0;
}

input, button {
    background: var(--panel2);
    color: white;
    border: 1px solid var(--border);
    padding: 10px;
    border-radius: 8px;
}

button {
    background: var(--green);
    color: #092319;
    font-weight: bold;
}

.league {
    background: var(--panel);
    border-radius: 10px;
    margin-bottom: 18px;
    overflow: hidden;
}

.league-title {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 13px;
    background: var(--panel2);
    font-weight: bold;
    text-decoration: none;
    color: white;
}

.league-title img {
    width: 25px;
    height: 25px;
    object-fit: contain;
}

.country {
    color: var(--muted);
    font-size: 12px;
    margin-left: auto;
}

.match {
    display: grid;
    grid-template-columns: 1fr 75px 1fr;
    align-items: center;
    padding: 15px 12px;
    border-top: 1px solid var(--border);
    text-decoration: none;
    color: white;
}

.team {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
}

.team img {
    width: 25px;
    height: 25px;
    object-fit: contain;
}

.away {
    justify-content: flex-end;
    text-align: right;
}

.score {
    text-align: center;
    font-weight: bold;
    font-size: 18px;
}

.status {
    display: block;
    font-size: 10px;
    color: var(--green);
    margin-top: 5px;
}

.panel {
    background: var(--panel);
    border-radius: 10px;
    padding: 15px;
    margin-bottom: 15px;
}

.match-header {
    display: flex;
    justify-content: space-around;
    align-items: center;
    text-align: center;
    padding: 25px 5px;
}

.club img {
    width: 65px;
    height: 65px;
    object-fit: contain;
}

.club-name {
    font-size: 13px;
    font-weight: bold;
    margin-top: 8px;
}

.big-score {
    font-size: 30px;
    font-weight: bold;
}

.tabs {
    display: flex;
    gap: 15px;
    overflow-x: auto;
    padding: 12px 0;
    border-bottom: 1px solid var(--border);
}

.tabs a {
    color: var(--green);
    text-decoration: none;
    white-space: nowrap;
}

.event {
    display: flex;
    justify-content: space-between;
    padding: 12px 5px;
    border-bottom: 1px solid var(--border);
    font-size: 13px;
}

.stat {
    margin: 15px 0;
}

.stat-label {
    display: flex;
    justify-content: space-between;
    font-size: 13px;
    margin-bottom: 7px;
}

.bar {
    height: 7px;
    background: var(--panel2);
    border-radius: 10px;
    overflow: hidden;
}

.bar-fill {
    height: 100%;
    background: var(--green);
}

.lineup {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
}

.player {
    padding: 7px;
    border-bottom: 1px solid var(--border);
    font-size: 12px;
}

table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
}

td, th {
    padding: 10px 5px;
    text-align: center;
    border-bottom: 1px solid var(--border);
}

th {
    color: var(--muted);
}

.club-cell {
    text-align: left;
}

.club-cell img {
    width: 20px;
    vertical-align: middle;
    margin-right: 5px;
}

footer {
    text-align: center;
    color: var(--muted);
    padding: 25px;
    font-size: 12px;
}

@media(max-width:480px) {
    .team {
        font-size: 11px;
    }

    .team img {
        width: 21px;
        height: 21px;
    }

    .match {
        grid-template-columns: 1fr 65px 1fr;
    }

    .club img {
        width: 48px;
        height: 48px;
    }
}

</style>
</head>

<body>

<header>
    <div class="logo">⚽ DAOUDA SPORTS STATS</div>

    <nav>
        <a href="/">Accueil</a>
        <a href="/championnats">Championnats</a>
        <a href="/?filter=live">En direct</a>
        <a href="/?filter=today">Aujourd'hui</a>
    </nav>
</header>

<div class="container">

{% if page == "home" %}

<h2>⚽ Scores et matchs</h2>

<form class="datebar" method="GET">
    <input type="date" name="date" value="{{ day }}">
    <button type="submit">Voir</button>
</form>

{% if groups %}

{% for league_id, league in groups.items() %}

<div class="league">

<a class="league-title"
   href="/classement/{{ league_id }}?season={{ season }}">

    {% if league.logo %}
    <img src="{{ league.logo }}">
    {% endif %}

    <span>{{ league.name }}</span>

    <span class="country">{{ league.country }}</span>

</a>

{% for m in league.matches %}

<a class="match"
   href="/match/{{ m.fixture.id }}">

    <div class="team">
        <img src="{{ m.teams.home.logo }}">
        <span>{{ m.teams.home.name }}</span>
    </div>

    <div class="score">

        {% if m.goals.home is not none %}
            {{ m.goals.home }} - {{ m.goals.away }}
        {% else %}
            - : -
        {% endif %}

        <span class="status">
            {% if m.fixture.status.elapsed %}
                {{ m.fixture.status.elapsed }}'
            {% else %}
                {{ m.fixture.status.short }}
            {% endif %}
        </span>

    </div>

    <div class="team away">
        <span>{{ m.teams.away.name }}</span>
        <img src="{{ m.teams.away.logo }}">
    </div>

</a>

{% endfor %}
</div>

{% endfor %}

{% else %}

<div class="panel">
    Aucun match disponible pour cette date.
</div>

{% endif %}


{% elif page == "detail" %}

{% if match %}

<div class="panel">

<div class="match-header">

    <div class="club">
        <img src="{{ match.teams.home.logo }}">
        <div class="club-name">{{ match.teams.home.name }}</div>
    </div>

    <div>
        <div class="big-score">
            {{ match.goals.home }} - {{ match.goals.away }}
        </div>
        <div class="status">
            {{ match.fixture.status.long }}
            {% if match.fixture.status.elapsed %}
                · {{ match.fixture.status.elapsed }}'
            {% endif %}
        </div>
    </div>

    <div class="club">
        <img src="{{ match.teams.away.logo }}">
        <div class="club-name">{{ match.teams.away.name }}</div>
    </div>

</div>

<div style="text-align:center;color:var(--muted)">
    {{ match.league.name }} · {{ match.league.country }}
</div>

</div>

<div class="panel">

<h3>⚽ Événements du match</h3>

{% for e in events %}

<div class="event">

    <span>
        {{ e.time.elapsed }}'
        {% if e.time.extra %}+{{ e.time.extra }}{% endif %}
    </span>

    <span>
        {{ e.player.name or '' }}
        · {{ e.detail }}
        {% if e.assist.name %}
            ({{ e.assist.name }})
        {% endif %}
    </span>

</div>

{% else %}
<p>Aucun événement disponible.</p>
{% endfor %}

</div>

<div class="panel">

<h3>📊 Statistiques</h3>

{% if statistics|length >= 2 %}

{% set home_stats = statistics[0].statistics %}
{% set away_stats = statistics[1].statistics %}

{% for hs in home_stats %}

{% set ns = namespace(away_value='-', home_value='-') %}

{% for a in away_stats %}
    {% if a.type == hs.type %}
        {% set ns.away_value = a.value if a.value is not none else '-' %}
    {% endif %}
{% endfor %}

{% set ns.home_value = hs.value if hs.value is not none else '-' %}

<div class="stat">

    <div class="stat-label">
        <span>{{ ns.home_value }}</span>
        <strong>{{ hs.type }}</strong>
        <span>{{ ns.away_value }}</span>
    </div>

    <div class="bar">
        <div class="bar-fill" style="width:50%"></div>
    </div>

</div>

{% endfor %}

{% else %}
<p>Statistiques non disponibles.</p>
{% endif %}

</div>

<div class="panel">

<h3>👥 Compositions</h3>

{% if lineups %}

<div class="lineup">

{% for team in lineups %}

<div>

    <h4>{{ team.team.name }}</h4>

    <p>Formation : {{ team.formation or 'Non disponible' }}</p>

    <strong>Titulaires</strong>

    {% for p in team.startXI %}
        <div class="player">
            {{ p.player.number }} · {{ p.player.name }}
            <small>{{ p.player.pos }}</small>
        </div>
    {% endfor %}

    <strong>Remplaçants</strong>

    {% for p in team.substitutes %}
        <div class="player">
            {{ p.player.number }} · {{ p.player.name }}
        </div>
    {% endfor %}

</div>

{% endfor %}

</div>

{% else %}
<p>Compositions non disponibles.</p>
{% endif %}

</div>

{% else %}

<div class="panel">Match introuvable.</div>

{% endif %}


{% elif page == "leagues" %}

<h2>🏆 Championnats</h2>

{% for item in leagues %}

<div class="league">

<a class="league-title"
   href="/classement/{{ item.league.id }}?season={{ season }}">

    <img src="{{ item.league.logo }}">

    {{ item.league.name }}

    <span class="country">{{ item.country.name }}</span>

</a>

</div>

{% endfor %}


{% elif page == "standings" %}

<h2>🏆 {{ league_name }}</h2>

<div class="panel">

<h3>Classement</h3>

{% if table %}

<table>

<tr>
    <th>#</th>
    <th>Équipe</th>
    <th>MJ</th>
    <th>G</th>
    <th>N</th>
    <th>P</th>
    <th>Pts</th>
</tr>

{% for t in table %}

<tr>
    <td>{{ t.rank }}</td>

    <td class="club-cell">
        <img src="{{ t.team.logo }}">
        {{ t.team.name }}
    </td>

    <td>{{ t.all.played }}</td>
    <td>{{ t.all.win }}</td>
    <td>{{ t.all.draw }}</td>
    <td>{{ t.all.lose }}</td>
    <td><strong>{{ t.points }}</strong></td>
</tr>

{% endfor %}

</table>

{% else %}

<p>Classement non disponible.</p>

{% endif %}

</div>

{% endif %}

</div>

<footer>
    DAOUDA SPORTS STATS · Football en direct
</footer>

</body>
</html>
"""


# ==========================================
# ACCUEIL ET MATCHS
# ==========================================

@app.route("/")
def accueil():

    day = request.args.get(
        "date",
        date.today().isoformat()
    )

    matches = get_matches(day)

    filter_type = request.args.get("filter")

    if filter_type == "live":
        matches = [
            m for m in matches
            if m["fixture"]["status"]["short"] in [
                "1H", "2H", "HT", "ET", "BT", "P", "LIVE"
            ]
        ]

    groups = group_matches(matches)

    return render_template_string(
        PAGE,
        title="Accueil",
        page="home",
        groups=groups,
        day=day,
        season=date.today().year
    )


# ==========================================
# DETAILS MATCH
# ==========================================

@app.route("/match/<int:fixture_id>")
def detail_match(fixture_id):

    result = api("fixtures", {"id": fixture_id})

    match = result[0] if result else None

    events = []
    statistics = []
    lineups = []

    if match:

        events = api(
            "fixtures/events",
            {"fixture": fixture_id}
        )

        statistics = api(
            "fixtures/statistics",
            {"fixture": fixture_id}
        )

        lineups = api(
            "fixtures/lineups",
            {"fixture": fixture_id}
        )

    return render_template_string(
        PAGE,
        title="Détails du match",
        page="detail",
        match=match,
        events=events,
        statistics=statistics,
        lineups=lineups
    )


# ==========================================
# CHAMPIONNATS
# ==========================================

@app.route("/championnats")
def championnats():

    leagues = api("leagues", {"current": "true"})

    return render_template_string(
        PAGE,
        title="Championnats",
        page="leagues",
        leagues=leagues,
        season=date.today().year
    )


# ==========================================
# CLASSEMENTS
# ==========================================

@app.route("/classement/<int:league_id>")
def classement(league_id):

    season = request.args.get(
        "season",
        date.today().year,
        type=int
    )

    result = api(
        "standings",
        {
            "league": league_id,
            "season": season
        }
    )

    table = []
    league_name = "Championnat"

    if result:
        league = result[0]["league"]
        league_name = league["name"]

        if league.get("standings"):
            table = league["standings"][0]

    return render_template_string(
        PAGE,
        title="Classement",
        page="standings",
        table=table,
        league_name=league_name,
        season=season
    )


# ==========================================
# API JSON
# ==========================================

@app.route("/api/live")
def api_live():

    matches = api("fixtures", {"live": "all"})

    return {
        "success": True,
        "total": len(matches),
        "championnats": group_matches(matches)
    }


@app.route("/api/match/<int:fixture_id>")
def api_match(fixture_id):

    return {
        "match": api("fixtures", {"id": fixture_id}),
        "events": api("fixtures/events", {"fixture": fixture_id}),
        "statistics": api("fixtures/statistics", {"fixture": fixture_id}),
        "lineups": api("fixtures/lineups", {"fixture": fixture_id})
    }


@app.route("/api/status")
def status():

    return {
        "application": "Daouda Sports Stats",
        "server": "online",
        "api_configured": bool(API_FOOTBALL_KEY)
    }


# ==========================================
# DEMARRAGE
# ==========================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
    