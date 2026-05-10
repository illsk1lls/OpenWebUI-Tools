"""
title: get_sports
author: Grok + illsk1lls
version: 1.1
description: Fetches live scores, upcoming games, and final results with times/dates for sporting events via ESPN free web API

Example prompts:
- "What are the NBA scores today?"
- "NFL games tomorrow"
- "EPL matches this weekend"
- "Lakers schedule" (or any team + "scores/schedule")
- "MLB results yesterday"
"""

from typing import Optional, List, Dict, Any
import requests
from datetime import datetime, timedelta


class Tools:
    def __init__(self):
        pass

    def parse_date_input(self, date_str: Optional[str]) -> Optional[str]:
        if not date_str:
            return None
        date_str = date_str.lower().strip()
        today = datetime.now().date()
        if date_str in ["today", "now", "current", ""]:
            return today.strftime("%Y%m%d")
        elif date_str in ["tomorrow", "tmr", "next day"]:
            return (today + timedelta(days=1)).strftime("%Y%m%d")
        elif date_str in ["yesterday", "yday", "last day"]:
            return (today - timedelta(days=1)).strftime("%Y%m%d")
        for fmt in ("%Y-%m-%d", "%Y%m%d"):
            try:
                d = datetime.strptime(date_str, fmt).date()
                return d.strftime("%Y%m%d")
            except ValueError:
                continue
        return None

    def get_league_path(self, sport_input: str) -> str:
        s = (
            sport_input.lower()
            .strip()
            .replace(" ", "")
            .replace("-", "")
            .replace(".", "")
        )
        mappings = {
            "nfl": "football/nfl",
            "football": "football/nfl",
            "nba": "basketball/nba",
            "basketball": "basketball/nba",
            "mlb": "baseball/mlb",
            "baseball": "baseball/mlb",
            "nhl": "hockey/nhl",
            "hockey": "hockey/nhl",
            "epl": "soccer/eng.1",
            "premierleague": "soccer/eng.1",
            "premier": "soccer/eng.1",
            "england": "soccer/eng.1",
            "laliga": "soccer/esp.1",
            "ligabbva": "soccer/esp.1",
            "spain": "soccer/esp.1",
            "bundesliga": "soccer/ger.1",
            "germany": "soccer/ger.1",
            "seriea": "soccer/ita.1",
            "italy": "soccer/ita.1",
            "ligue1": "soccer/fra.1",
            "france": "soccer/fra.1",
            "mls": "soccer/usa.1",
            "usa": "soccer/usa.1",
            "championsleague": "soccer/uefa.champions",
            "ucl": "soccer/uefa.champions",
        }
        if s in mappings:
            return mappings[s]
        if "/" in sport_input:
            return sport_input
        if s in ["soccer", "futbol"]:
            return "soccer/eng.1"
        return f"football/{s}"

    def get_sports_scores(self, sport: str = "nfl", date: Optional[str] = None) -> str:
        league_path = self.get_league_path(sport)
        formatted_date = self.parse_date_input(date)
        url = f"https://site.api.espn.com/apis/site/v2/sports/{league_path}/scoreboard"
        params = {"limit": 200}
        if formatted_date:
            params["dates"] = formatted_date
        try:
            resp = requests.get(
                url,
                params=params,
                timeout=15,
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; OpenWebUI-SportsTool/1.0)"
                },
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            return f"⚠️ Error fetching data from ESPN: {str(e)}\nPlease try again in a moment."
        events: List[Dict[str, Any]] = data.get("events", [])
        if not events:
            date_display = formatted_date or datetime.now().strftime("%Y-%m-%d")
            return f"**No games found** for **{league_path}** on **{date_display}**."
        games = []
        for event in events:
            try:
                name = event.get("name", "Unknown Match")
                status_info = event.get("status", {}).get("type", {})
                status_name = status_info.get("name", "UNKNOWN")
                detail = status_info.get("detail", "")
                comp = event.get("competitions", [{}])[0]
                competitors = comp.get("competitors", [])
                teams = []
                for c in competitors:
                    team = c.get("team", {})
                    teams.append(
                        {
                            "name": team.get(
                                "displayName", team.get("shortDisplayName", "Team")
                            ),
                            "abbrev": team.get("abbreviation", ""),
                            "score": c.get("score", "-"),
                            "home_away": c.get("homeAway", ""),
                            "winner": c.get("winner", False),
                        }
                    )
                if len(teams) >= 2:
                    home = next(
                        (t for t in teams if t["home_away"] == "home"), teams[0]
                    )
                    away = next(
                        (t for t in teams if t["home_away"] == "away"),
                        teams[1] if len(teams) > 1 else teams[0],
                    )
                    matchup = f"{away['name']} @ {home['name']}"
                    score_str = (
                        f" **{away['score']} - {home['score']}**"
                        if status_name in ["STATUS_FINAL", "STATUS_IN_PROGRESS"]
                        else ""
                    )
                else:
                    matchup = name
                    score_str = ""
                games.append(
                    {
                        "name": name,
                        "matchup": matchup,
                        "score_str": score_str,
                        "status": status_name,
                        "detail": detail,
                        "venue": comp.get("venue", {}).get("fullName", ""),
                    }
                )
            except Exception:
                continue
        live = [
            g
            for g in games
            if "IN_PROGRESS" in g["status"] or "HALFTIME" in g.get("detail", "").upper()
        ]
        finals = [g for g in games if "FINAL" in g["status"]]
        scheduled = [
            g for g in games if "SCHEDULED" in g["status"] or "PRE" in g["status"]
        ]
        date_display = formatted_date or datetime.now().strftime("%Y-%m-%d")
        output = f"## 🏟️ {league_path.replace('/', ' ').upper()} — Scores & Schedule\n"
        output += f"**Date:** {date_display}  |  **Source:** ESPN (live data)\n\n"
        summary_parts = []
        if live:
            summary_parts.append(f"🔴 {len(live)} Live")
        if scheduled:
            summary_parts.append(f"📅 {len(scheduled)} Upcoming")
        if finals:
            summary_parts.append(f"✅ {len(finals)} Final")
        if summary_parts:
            output += f"**{' • '.join(summary_parts)}**\n\n"
        if live:
            output += "### 🔴 LIVE GAMES\n\n"
            for g in live:
                output += f"- **{g['matchup']}**{g['score_str']}\n  *{g['detail']}*"
                if g.get("venue"):
                    output += f"  • {g['venue']}"
                output += "\n\n"
        if scheduled:
            output += "### 📅 UPCOMING / SCHEDULED\n\n"
            for g in scheduled:
                output += f"- **{g['matchup']}**\n  *{g['detail']}*"
                if g.get("venue"):
                    output += f"  • {g['venue']}"
                output += "\n\n"
        if finals:
            output += "### ✅ FINAL RESULTS\n\n"
            for g in finals:
                output += f"- **{g['matchup']}**{g['score_str']}\n  *{g['detail']}*\n\n"
        output += "\n*Times are typically shown in ET. Data updates in real time.*"
        return output
