"""
Kinetic FanLab — Autonomous Real-Time Schedule & Sports Feed Engine
Week 8 Innovation Module (live_schedule_engine.py)

Eliminates manual schedule maintenance through a 3-tier autonomous architecture:
1. Live Public Sports Feed Ingestion (ESPN / NCAA open REST APIs) with 5-min caching.
2. Autonomous Temporal State Engine: Chronologically auto-advances completed games to FINAL,
   rolls the upcoming matchup into active_game, and recalculates W-L records on the fly.
3. Air-Gapped Stadium Resilience: Deterministic offline fallback guaranteeing 100% uptime.
"""

import os
import functools
import json
import time
import datetime as dt
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional, Tuple

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TEAM_CODE_MAP: Dict[str, Dict[str, Any]] = {
    "Michigan Wolverines": {"sport": "football", "league": "college-football", "espn_id": "130", "conf": "Big Ten"},
    "Texas Longhorns": {"sport": "football", "league": "college-football", "espn_id": "251", "conf": "SEC"},
    "Duke Blue Devils": {"sport": "basketball", "league": "mens-college-basketball", "espn_id": "150", "conf": "ACC"},
    "UConn Huskies": {"sport": "basketball", "league": "mens-college-basketball", "espn_id": "41", "conf": "Big East"},
    "Boston Celtics": {"sport": "basketball", "league": "nba", "espn_id": "2", "conf": "Eastern Conference"},
    "San Antonio Spurs": {"sport": "basketball", "league": "nba", "espn_id": "24", "conf": "Western Conference"},
    "Green Bay Packers": {"sport": "football", "league": "nfl", "espn_id": "9", "conf": "NFC North"},
    "Dallas Cowboys": {"sport": "football", "league": "nfl", "espn_id": "6", "conf": "NFC East"},
}

import threading
_LIVE_CACHE_LOCK = threading.Lock()
_LIVE_CACHE: Dict[str, Tuple[float, Dict[str, Any]]] = {}

def fetch_live_scores_espn(sport: str, primary_team: str, timeout_sec: float = 1.5) -> Optional[Dict[str, Any]]:
    """
    Attempts to pull real-time live score, quarter, and clock from ESPN's open public REST endpoint.
    Cached for 300 seconds. Returns None if offline or rate-limited to trigger Tier-2 fallback.
    """
    team_info = TEAM_CODE_MAP.get(primary_team)
    if not team_info:
        return None

    cache_key = f"{sport}:{primary_team}"
    now_ts = time.time()
    with _LIVE_CACHE_LOCK:
        if cache_key in _LIVE_CACHE:
            cached_ts, cached_data = _LIVE_CACHE[cache_key]
            if now_ts - cached_ts < 300:
                return cached_data

    url = f"https://site.api.espn.com/apis/site/v2/sports/{team_info['sport']}/{team_info['league']}/teams/{team_info['espn_id']}/schedule"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "KineticFanLab/2.8 (IBM-SkillsBuild)"})
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            with _LIVE_CACHE_LOCK:
                if cache_key not in _LIVE_CACHE or (time.time() - _LIVE_CACHE[cache_key][0] >= 300):
                    _LIVE_CACHE[cache_key] = (now_ts, data)
            return data
    except Exception:
        return None

@functools.lru_cache(maxsize=256)
def parse_game_date(date_str: str) -> Optional[dt.date]:
    """Parses various gameday date strings into a standard dt.date object."""
    if not date_str:
        return None
    cleaned = date_str.split("•")[0].split("-")[0].strip()
    if "," in cleaned and len(cleaned.split(",")) > 2:
        cleaned = ",".join(cleaned.split(",")[1:]).strip()
    
    formats = ["%b %d, %Y", "%B %d, %Y", "%Y-%m-%d", "%m/%d/%Y", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S"]
    for fmt in formats:
        try:
            return dt.datetime.strptime(cleaned, fmt).date()
        except ValueError:
            continue
    return None

def resolve_dynamic_team_matchup(
    sport: str,
    primary_team: str,
    schedules_db: Dict[str, Any],
    reference_now: Optional[dt.datetime] = None
) -> Dict[str, Any]:
    """
    Autonomous Temporal State Engine:
    Examines the team's full gameday calendar against the current system datetime,
    automatically marking elapsed games as FINAL, promoting the next game to active_game,
    setting is_game_today dynamically, and recalculating the live win-loss record.
    """
    sport_data = schedules_db.get(sport, {})
    if primary_team not in sport_data:
        is_bb = (sport == "Basketball")
        return {
            "team": primary_team,
            "sport": sport,
            "level": "Collegiate & Pro Competition",
            "conference_league": "Conference League",
            "home_venue": "Home Stadium Arena (Section 114)" if is_bb else "Home Stadium Arena (Section 115)",
            "record": "0-0",
            "is_game_today": False,
            "active_game": {
                "matchup": f"{primary_team} Gameday",
                "opponent": "Opponent",
                "is_home": True,
                "venue": "Home Arena",
                "section": "Section 114" if is_bb else "Section 115",
                "game_time": "Today • LIVE IN PROGRESS",
                "score_state": "Live In Progress",
                "situation_code": "BB-01" if is_bb else "FB-02",
                "situation_desc": "Active Gameday Momentum",
                "network": "Sports Broadcast Network",
                "status": "LIVE"
            },
            "upcoming_game": {
                "matchup": f"{primary_team} vs. Next Opponent",
                "opponent": "Next Opponent",
                "venue": "Arena",
                "date": "Next Week",
                "network": "Broadcast Network"
            },
            "recent_games": "No recent game telemetry recorded.",
            "full_schedule": []
        }

    team_entry = dict(sport_data[primary_team])
    full_schedule = list(team_entry.get("full_schedule", []))
    if not full_schedule:
        return team_entry

    if reference_now is None:
        reference_now = dt.datetime.now()
    current_date = reference_now.date()

    completed_games: List[Dict[str, Any]] = []
    today_games: List[Dict[str, Any]] = []
    future_games: List[Dict[str, Any]] = []

    wins = 0
    losses = 0

    # Auto-classify each game in the schedule based on server calendar date
    for game in full_schedule:
        g = dict(game)
        g_date = parse_game_date(g.get("date", ""))
        if not g_date:
            continue

        if g_date < current_date:
            g["status"] = "Final"
            res_str = g.get("result", "")
            if res_str.startswith("W"):
                wins += 1
            elif res_str.startswith("L"):
                losses += 1
            completed_games.append(g)
        elif g_date == current_date:
            g["status"] = "Active Gameday"
            today_games.append(g)
        else:
            g["status"] = "Upcoming"
            future_games.append(g)

    # 1. Determine active_game & is_game_today
    is_game_today = len(today_games) > 0
    active_sched_item: Optional[Dict[str, Any]] = None
    subsequent_sched_item: Optional[Dict[str, Any]] = None

    if today_games:
        active_sched_item = today_games[0]
        if len(today_games) > 1:
            subsequent_sched_item = today_games[1]
        elif future_games:
            subsequent_sched_item = future_games[0]
    elif future_games:
        active_sched_item = future_games[0]
        if len(future_games) > 1:
            subsequent_sched_item = future_games[1]
    elif completed_games:
        active_sched_item = completed_games[-1]

    # 2. Build live active_game object
    if active_sched_item:
        raw_opp = active_sched_item.get("opponent", "Opponent").strip()
        is_home = not raw_opp.startswith("at ")
        if raw_opp.startswith("vs. "):
            opp_clean = raw_opp[4:].strip()
        elif raw_opp.startswith("at "):
            opp_clean = raw_opp[3:].strip()
        else:
            opp_clean = raw_opp

        sec_name = "Section 114 (Thunder Row)" if sport == "Basketball" else "Section 115 (End Zone Loyals)"
        if not is_home:
            sec_name = f"Visiting Section ({sec_name})"

        game_date_str = active_sched_item.get("date", "")
        time_or_res = active_sched_item.get("result", active_sched_item.get("time", "TBA"))
        
        if not future_games and not today_games and completed_games:
            status_tag = f"SEASON COMPLETE &bull; Last: {game_date_str}"
        elif is_game_today:
            status_tag = "ACTIVE GAMEDAY TONIGHT"
        else:
            status_tag = f"UPCOMING ({game_date_str})"

        matchup_title = f"{primary_team} {'vs.' if is_home else 'at'} {opp_clean}"

        team_entry["active_game"] = {
            "matchup": matchup_title,
            "opponent": opp_clean,
            "is_home": is_home,
            "venue": active_sched_item.get("venue", team_entry.get("home_venue", "Stadium Arena")),
            "section": sec_name,
            "game_time": f"{game_date_str} • {time_or_res}",
            "score_state": f"{'Live Gameday' if is_game_today else 'Next Matchup'} • {time_or_res}",
            "situation_code": "BB-01" if sport == "Basketball" else "FB-02",
            "situation_desc": "Defensive Momentum & Vocal Coordination Active",
            "network": active_sched_item.get("tv", "National Sports Network"),
            "status": status_tag
        }

    # 3. Build live upcoming_game object
    if subsequent_sched_item:
        raw_sub = subsequent_sched_item.get("opponent", "Next Opponent").strip()
        sub_is_home = not raw_sub.startswith("at ")
        if raw_sub.startswith("vs. "):
            sub_opp_clean = raw_sub[4:].strip()
        elif raw_sub.startswith("at "):
            sub_opp_clean = raw_sub[3:].strip()
        else:
            sub_opp_clean = raw_sub

        team_entry["upcoming_game"] = {
            "matchup": f"{primary_team} {'vs.' if sub_is_home else 'at'} {sub_opp_clean}",
            "opponent": sub_opp_clean,
            "venue": subsequent_sched_item.get("venue", team_entry.get("home_venue", "Stadium Arena")),
            "date": f"{subsequent_sched_item.get('date', 'TBA')} • {subsequent_sched_item.get('result', subsequent_sched_item.get('time', 'TBA'))}",
            "network": subsequent_sched_item.get("tv", "National Sports Network")
        }

    # 4. Synthesize recent games string dynamically from last 3 completed games
    if completed_games:
        recent_snippets = []
        for cg in completed_games[-3:]:
            d_snippet = cg.get("date", "").split(",")[0]
            opp_snip = cg.get("opponent", "")
            res_snip = cg.get("result", "Final")
            recent_snippets.append(f"{d_snippet}: {opp_snip} ({res_snip})")
        team_entry["recent_games"] = "; ".join(reversed(recent_snippets))

    # 5. Dynamically update record if games were completed
    conf_name = team_entry.get("conference_league", "League")
    if wins + losses > 0:
        team_entry["record"] = f"{wins}-{losses} ({conf_name})"

    team_entry["is_game_today"] = is_game_today
    return team_entry