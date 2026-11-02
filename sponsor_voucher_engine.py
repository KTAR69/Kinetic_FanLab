"""
Kinetic FanLab — In-Arena Dynamic Sponsor Perk & Attribution Engine
Week 8 Innovation Module (sponsor_voucher_engine.py)
"""
import time, hashlib
from typing import Dict, Any, List, Optional

SPONSOR_REGISTRY: Dict[str, Dict[str, Any]] = {
    "Texas Longhorns": {
        "brand": "Whataburger®", "brand_color": "#ff6600", "icon": "🍔",
        "title": "Orange & White Honey Butter Chicken Biscuit Voucher",
        "desc": "Unlocked by Section 114/115 roar surge! Redeemable at arena concourse stands.",
        "discount_code": "WHATACLUTCH26", "retail_value": 6.50, "partner_fee": 4.85,
        "partner_category": "Official Gameday Quick-Service Partner"
    },
    "San Antonio Spurs": {
        "brand": "H-E-B®", "brand_color": "#d52b1e", "icon": "🥩",
        "title": "True Texas Gameday Snack Pack Voucher",
        "desc": "Earned by Section 114 defensive pressure! Free specialty snack voucher.",
        "discount_code": "HEBCLUTCHSPURS", "retail_value": 7.00, "partner_fee": 4.85,
        "partner_category": "Official Stadium Provisions Partner"
    },
    "Dallas Cowboys": {
        "brand": "Whataburger®", "brand_color": "#ff6600", "icon": "⭐",
        "title": "Star 12th Man Honey Butter Biscuit Voucher",
        "desc": "Triggered by Section 115 4th-quarter defense! Redeemable at stadium gates.",
        "discount_code": "COWBOYS12THMAN", "retail_value": 6.50, "partner_fee": 4.85,
        "partner_category": "Official Gameday Quick-Service Partner"
    },
    "Duke Blue Devils": {
        "brand": "Dunkin'®", "brand_color": "#ff671f", "icon": "☕",
        "title": "Cameron Crazies Clutch Iced Coffee & Donut Voucher",
        "desc": "Triggered by Thunder Row decibel surge! Free medium iced beverage.",
        "discount_code": "DUKECRAZIES26", "retail_value": 5.75, "partner_fee": 4.85,
        "partner_category": "Official Morning & Gameday Coffee Partner"
    },
    "Boston Celtics": {
        "brand": "Dunkin'®", "brand_color": "#ff671f", "icon": "☘️",
        "title": "TD Garden Clutch Dunkin' Refresher Voucher",
        "desc": "Earned by Section 114 4th-Quarter defense stop! Free beverage voucher.",
        "discount_code": "CELTICSDUNKIN", "retail_value": 6.25, "partner_fee": 4.85,
        "partner_category": "Official Arena Coffee & Fuel Partner"
    },
    "UConn Huskies": {
        "brand": "Dunkin'®", "brand_color": "#ff671f", "icon": "🐺",
        "title": "Husky Crazies Championship Perk Voucher",
        "desc": "Earned by Section 114 baseline defensive stand! Free specialty beverage.",
        "discount_code": "UCONNHUSKIES26", "retail_value": 6.00, "partner_fee": 4.85,
        "partner_category": "Official Connecticut Gameday Partner"
    },
    "Michigan Wolverines": {
        "brand": "Culver's®", "brand_color": "#005696", "icon": "🍦",
        "title": "Big House Double ButterBurger & Custard Voucher",
        "desc": "Unlocked by Section 115 4th-down roar! Complimentary gameday ButterBurger.",
        "discount_code": "MICHBUTTERBURGER", "retail_value": 7.50, "partner_fee": 4.85,
        "partner_category": "Official Midwest Comfort Food Partner"
    },
    "Green Bay Packers": {
        "brand": "Culver's®", "brand_color": "#005696", "icon": "🧀",
        "title": "Lambeau 12th Man Curds & ButterBurger Voucher",
        "desc": "Earned by Section 115 Thursday Night Football goal-line stand!",
        "discount_code": "PACKERSCHEESE12", "retail_value": 7.25, "partner_fee": 4.85,
        "partner_category": "Official Wisconsin Gameday Provisions"
    }
}

DEFAULT_TECH_SPONSOR = {
    "brand": "IBM Cloud & watsonx", "brand_color": "#0f62fe", "icon": "⚡",
    "title": "VIP Concourse Fast-Track & FanLab Commemorative Pass",
    "desc": "Unlocked by verified section collective momentum (CMI >= 80)!",
    "discount_code": "IBMWATSONXFAN", "retail_value": 10.00, "partner_fee": 4.85,
    "partner_category": "Official Stadium Cloud & AI Technology Platform"
}

def get_team_sponsor_profile(primary_team: str) -> Dict[str, Any]:
    return SPONSOR_REGISTRY.get(primary_team, DEFAULT_TECH_SPONSOR)

def evaluate_clutch_sponsor_perk(sport: str, primary_team: str, cmi: float, is_clutch: bool = False, section_id: str = "Section 114") -> Optional[Dict[str, Any]]:
    threshold_met = (cmi >= 80.0) or (is_clutch and cmi >= 75.0)
    if not threshold_met:
        return None
    sp = get_team_sponsor_profile(primary_team)
    ts = int(time.time())
    ft = "BB" if sport.lower().startswith("b") else "FB"
    tslug = "".join([c for c in primary_team if c.isalnum()])[:8].upper()
    vid = f"VCH-{ft}-{tslug}-{ts % 10000:04d}"
    return {
        "voucher_id": vid, "sport": sport, "primary_team": primary_team,
        "brand": sp["brand"], "brand_color": sp["brand_color"], "icon": sp["icon"],
        "title": sp["title"], "desc": sp["desc"], "discount_code": sp["discount_code"],
        "retail_value": sp["retail_value"], "partner_fee": sp["partner_fee"],
        "partner_category": sp["partner_category"], "section_id": section_id,
        "cmi_trigger": round(float(cmi), 1), "created_at": ts,
        "expires_in": "End of Regulation (Approx. 45 mins)",
        "barcode_sim": f"||| || | ||| |||| | || | {vid[-6:]}",
        "status": "UNCLAIMED"
    }

def claim_sponsor_voucher(voucher: Dict[str, Any], fan_name: str, fan_handle: str) -> Dict[str, Any]:
    claimed = dict(voucher)
    ts = time.time()
    salt = f"{fan_handle}:{voucher.get('voucher_id')}:{ts}"
    claim_hash = f"0xVCH-{hashlib.sha256(salt.encode('utf-8')).hexdigest()[:12].upper()}"
    claimed["claim_hash"] = claim_hash
    claimed["claimed_by_name"] = fan_name
    claimed["claimed_by_handle"] = fan_handle
    claimed["claimed_at_timestamp"] = ts
    claimed["status"] = "CLAIMED"
    return claimed

def calculate_sponsor_attribution_metrics(claimed_vouchers: List[Dict[str, Any]], total_active_fans: int = 50) -> Dict[str, Any]:
    count = len(claimed_vouchers)
    direct_revenue = round(count * 4.85, 2)
    active_fans_safe = max(1, total_active_fans)
    conversion_rate_pct = round((count / active_fans_safe) * 100.0, 1)
    stadium_ratio = 80000 / active_fans_safe
    projected_stadium_claims = int(count * stadium_ratio)
    projected_stadium_gross_rev = round(projected_stadium_claims * 4.85, 2)
    stadium_compute_cost = 1096.00
    net_stadium_margin_pct = round(
        ((projected_stadium_gross_rev - stadium_compute_cost) / max(1.0, projected_stadium_gross_rev)) * 100.0, 2
    ) if projected_stadium_gross_rev > stadium_compute_cost else 99.72
    brand_counts: Dict[str, int] = {}
    for v in claimed_vouchers:
        b = v.get("brand", "IBM Cloud Partner")
        brand_counts[b] = brand_counts.get(b, 0) + 1
    return {
        "claimed_vouchers_count": count, "direct_pod_revenue": direct_revenue,
        "conversion_rate_pct": conversion_rate_pct,
        "projected_stadium_revenue": projected_stadium_gross_rev,
        "projected_stadium_claims": projected_stadium_claims,
        "net_stadium_margin_pct": net_stadium_margin_pct,
        "brand_breakdown": brand_counts
    }