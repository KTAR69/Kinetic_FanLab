"""
==============================================================================
Kinetic FanLab — Interactive NPC Guide Mentors & Onboarding Progression Engine
Week 7 Architecture: Dual-Entry (Rookie Walkthrough vs. Express Entry),
Progressive NPC Unlocking Tree, In-Game Guidance Dialogue, and Capstone NFT Certification.
==============================================================================
"""

from typing import Dict, Any, List, Optional


# ==============================================================================
# NPC MENTOR REGISTRY & DIALOGUE METADATA
# ==============================================================================

NPC_MENTOR_REGISTRY: Dict[str, Dict[str, Any]] = {
    # ------------------ BASKETBALL MENTORS (Section 114 — Thunder Row) ------------------
    "Marcus Vance": {
        "name": "Marcus Vance",
        "sport": "Basketball",
        "role": "Student Section Director",
        "tier": "Tier 4 (Section Director)",
        "sec": "Section 114 (Thunder Row)",
        "avatar_icon": "📣",
        "color": "#f1c21b",
        "is_lead": True,
        "unlock_order": 1,
        "unlock_requirement": "Always Unlocked (Section 114 Lead Guide)",
        "greeting": (
            "Welcome to Thunder Row (Section 114)! I'm Marcus, Section Director. Fandom here isn't passive—we build "
            "an acoustic wall to rattle opposing shooters. Let's get your passport anchored and take your first defensive action!"
        ),
        "hint": (
            "Start by completing your in-seat early check-in or log a few rhythm taps. Once you get active, "
            "our former rookie Jordan Lee will step up to pass the baton!"
        ),
        "post_unlock_cheer": "Glad to have you leading Thunder Row! Keep your row pod locked in on every possession.",
    },
    "Jordan Lee": {
        "name": "Jordan Lee",
        "sport": "Basketball",
        "role": "Rookie Section Member",
        "tier": "Tier 1 (Rookie Member)",
        "sec": "Section 114 (Thunder Row)",
        "avatar_icon": "⚡",
        "color": "#0f62fe",
        "is_lead": False,
        "unlock_order": 2,
        "unlock_requirement": "Log at least 3 Pulse Taps or 1 Seat Check-In/Respect Tap",
        "greeting": (
            "Hey! You made it into Section 114! Marcus can be intense about the noise levels, but you're already tapping "
            "in rhythm. Glad I'm not the newest member in Thunder Row anymore!"
        ),
        "hint": (
            "If you want to master row 1–3 energy, you need to sync with Elena Rostova. She leads our visual waving props "
            "on Screen 3—trigger a Surge Burst (+5) during clutch defense to catch her eye!"
        ),
        "post_unlock_cheer": "Tapping alongside you in Row 4! Let's show the upper decks how Section 114 defends.",
    },
    "Elena Rostova": {
        "name": "Elena Rostova",
        "sport": "Basketball",
        "role": "Prop & Waving Captain",
        "tier": "Tier 2 (Prop Captain)",
        "sec": "Section 114 (Thunder Row)",
        "avatar_icon": "🌊",
        "color": "#8a3ffc",
        "is_lead": False,
        "unlock_order": 3,
        "unlock_requirement": "Trigger a Surge Burst (+5) or sync Section Co-Op Synergy",
        "greeting": (
            "Incredible rhythm! Elena here—I coordinate thundersticks and prop-waving in Section 114. "
            "When the shooter bends his knees, synchronized visual disruption cuts his free-throw accuracy by over 18%!"
        ),
        "hint": (
            "Devon Miller runs our chant tactics. Head over to the 36-Hour Virtual Tailgate (Screen 2) or post a clean "
            "fan callout—if your chant resonates, Devon will bring you into the tactical huddle!"
        ),
        "post_unlock_cheer": "Your waving timing on the knee-bend is spot on! Section 114's defense wall is synchronized.",
    },
    "Devon Miller": {
        "name": "Devon Miller",
        "sport": "Basketball",
        "role": "Vocal Tactician & Chant Starter",
        "tier": "Tier 3 (Vocal Tactician)",
        "sec": "Section 114 (Thunder Row)",
        "avatar_icon": "🎙️",
        "color": "#42be65",
        "is_lead": False,
        "unlock_order": 4,
        "unlock_requirement": "Synthesize/vote on tailgate chants (Screen 2) or post a section callout (Screen 3)",
        "greeting": (
            "Respect! Devon here. Our acoustics don't just happen—we synthesize chants that peak on the release. "
            "With you locked in, Section 114 has all 4 mentors fully engaged!"
        ),
        "hint": (
            "You've connected with Marcus, Jordan, Elena, and me! Head to your Living Trophy Case on Screen 1 "
            "to claim the legendary 'Thunder Row Inner Circle Key' NFT badge!"
        ),
        "post_unlock_cheer": "Section 114's acoustic wall is unstoppable! Full 4-mentor synergy unlocked.",
    },

    # ------------------ FOOTBALL MENTORS (Section 115 — End Zone Loyals) ------------------
    "Sarah Jenkins": {
        "name": "Sarah Jenkins",
        "sport": "Football",
        "role": "10-Year Stadium Veteran",
        "tier": "Tier 5 (Stadium Veteran)",
        "sec": "Section 115 (End Zone Loyals)",
        "avatar_icon": "🛡️",
        "color": "#f1c21b",
        "is_lead": True,
        "unlock_order": 1,
        "unlock_requirement": "Always Unlocked (Section 115 Lead Guide)",
        "greeting": (
            "Welcome to the End Zone Loyals (Section 115)! I'm Sarah, 10-year season ticket holder. When our defense takes "
            "the field, our job is to make the ground shake. Let's get your seat beacon verified and start your season!"
        ),
        "hint": (
            "Check in at your seat or log your first bleacher stomps. Once you take action, "
            "our rookie 12th Man Alex Taylor will welcome you to the row!"
        ),
        "post_unlock_cheer": "Decade-tested defense! Keep Section 115 shaking the crossbar on every 4th down.",
    },
    "Alex Taylor": {
        "name": "Alex Taylor",
        "sport": "Football",
        "role": "General Member & Rookie 12th Man",
        "tier": "Tier 1 (General Member)",
        "sec": "Section 115 (End Zone Loyals)",
        "avatar_icon": "🏈",
        "color": "#0f62fe",
        "is_lead": False,
        "unlock_order": 2,
        "unlock_requirement": "Log at least 3 Pulse Taps or 1 Seat Check-In/Respect Tap",
        "greeting": (
            "Welcome to Section 115! Sarah has been standing in this row for a decade, so seeing new fans jump on "
            "early check-in right away is huge for our 1.25x boost. Glad to have another fresh voice in the end zone!"
        ),
        "hint": (
            "You have to meet Carlos Mendez out in Lot B before kickoff. Check out the 36-hour tailgate on Screen 2—he "
            "rewards fans who participate in pre-game chant strategy and community logistics!"
        ),
        "post_unlock_cheer": "Rookies unite! Our bleacher stomps are already registering on the stadium telemetry.",
    },
    "Carlos Mendez": {
        "name": "Carlos Mendez",
        "sport": "Football",
        "role": "Lot B Tailgate Host",
        "tier": "Tier 4 (Tailgate Host)",
        "sec": "Section 115 (End Zone Loyals)",
        "avatar_icon": "🔥",
        "color": "#fa4d56",
        "is_lead": False,
        "unlock_order": 3,
        "unlock_requirement": "Synthesize/vote on tailgate chants or review Lot B meetups (Screen 2)",
        "greeting": (
            "Smell that brisket? Carlos here, Lot B tailgate host for 40+ games! Gameday starts 36 hours before kickoff. "
            "Great work locking in your tailgate strategy—now we bring that appetite into the stadium!"
        ),
        "hint": (
            "Maya Patel is our biometric and tech superfan in Section 115. She tracks row heart rates and Log SPL decibels. "
            "Export a Proof-of-Momentum card on Screen 4 or push CMI to High Tier to bring her on board!"
        ),
        "post_unlock_cheer": "Lot B is fully behind you! Concession and tailgate perks are rolling in.",
    },
    "Maya Patel": {
        "name": "Maya Patel",
        "sport": "Football",
        "role": "Biometric & Tech Superfan",
        "tier": "Tier 2 (Tech Superfan)",
        "sec": "Section 115 (End Zone Loyals)",
        "avatar_icon": "⌚",
        "color": "#8a3ffc",
        "is_lead": False,
        "unlock_order": 4,
        "unlock_requirement": "Export a Proof-of-Momentum StoryCard (Screen 4) or achieve 80+ CMI",
        "greeting": (
            "Telemetry synced! Maya here. I monitor our 50-seat BLE pod mesh and watch sensors. Your verified surge just "
            "helped anchor our 111 dB acoustic wall. All 4 Section 115 mentors are now united with you!"
        ),
        "hint": (
            "You've bonded with Sarah, Alex, Carlos, and me! Head to your Living Trophy Case on Screen 1 "
            "to unlock the prestigious 'End Zone Loyals Founding Shield' NFT badge!"
        ),
        "post_unlock_cheer": "All biometric nodes aligned! Section 115 holds the gold standard in stadium defense.",
    },
}


# ==============================================================================
# PROGRESSION TRACKER & UNLOCK EVALUATION ENGINE
# ==============================================================================

def get_initial_npc_state(sport: str = "Basketball") -> Dict[str, Any]:
    """Returns clean initial onboarding state for a new fan member."""
    is_bball = "basket" in sport.lower()
    return {
        "onboarding_mode": "Rookie Tour",  # "Rookie Tour" or "Express Entry"
        "custom_member_name": "Rookie Fan",
        "custom_member_handle": "@fan_rookie",
        "custom_member_hash": "0xROOKIE-sec114-001" if is_bball else "0xROOKIE-sec115-001",
        "unlocked_npcs": ["Marcus Vance"] if is_bball else ["Sarah Jenkins"],
        "viewed_npc_dialogues": ["Marcus Vance"] if is_bball else ["Sarah Jenkins"],
        "active_npc_guide": "Marcus Vance" if is_bball else "Sarah Jenkins",
        "capstone_nft_unlocked": False,
        "actions_taken": {
            "early_checkin": False,
            "pulse_taps_count": 0,
            "respect_taps_sent": 0,
            "surge_burst_triggered": False,
            "chant_action_taken": False,
            "storycard_exported": False,
        },
    }


def evaluate_npc_unlocks(
    sport: str,
    current_unlocked: List[str],
    early_checkin: bool,
    tap_count: int,
    respect_count: int,
    chant_action: bool,
    storycard_exported: bool,
    cmi: float,
) -> Dict[str, Any]:
    """
    Evaluates trigger conditions and unlocks mentors dynamically without cloud cost:
    - Basketball: Marcus (always) -> Jordan (taps >= 3 or checkin or respect) -> Elena (taps >= 10 or burst) -> Devon (chants or CMI >= 75)
    - Football: Sarah (always) -> Alex (taps >= 3 or checkin or respect) -> Carlos (chants or tailgate) -> Maya (storycard or CMI >= 80)
    """
    is_bball = "basket" in sport.lower()
    lead_name = "Marcus Vance" if is_bball else "Sarah Jenkins"
    rookie_name = "Jordan Lee" if is_bball else "Alex Taylor"
    specialist_name = "Elena Rostova" if is_bball else "Carlos Mendez"
    veteran_name = "Devon Miller" if is_bball else "Maya Patel"

    unlocked = set(current_unlocked)
    unlocked.add(lead_name)  # Always unlocked

    newly_unlocked = []

    # 1. Low-barrier unlock (Jordan Lee / Alex Taylor)
    has_low_barrier = (tap_count >= 3) or early_checkin or (respect_count >= 1)
    if has_low_barrier and rookie_name not in unlocked:
        unlocked.add(rookie_name)
        newly_unlocked.append(rookie_name)

    # 2. Mid-tier unlock (Elena Rostova / Carlos Mendez)
    if is_bball:
        has_elena = (tap_count >= 10) or (cmi >= 65.0 and tap_count >= 5) or (rookie_name in unlocked and tap_count >= 8)
        if has_elena and specialist_name not in unlocked:
            unlocked.add(specialist_name)
            newly_unlocked.append(specialist_name)
    else:
        # Carlos Mendez: ONLY unlocks via tailgate chant participation (Screen 2)
        has_carlos = chant_action
        if has_carlos and specialist_name not in unlocked:
            unlocked.add(specialist_name)
            newly_unlocked.append(specialist_name)

    # 3. Final specialist unlock (Devon Miller / Maya Patel)
    if is_bball:
        has_devon = (specialist_name in unlocked) and (chant_action or (cmi >= 75.0 and tap_count >= 12))
        if has_devon and veteran_name not in unlocked:
            unlocked.add(veteran_name)
            newly_unlocked.append(veteran_name)
    else:
        # Maya Patel: requires StoryCard export on Screen 4 or high CMI with active taps & chants
        has_maya = (specialist_name in unlocked) and (storycard_exported or (cmi >= 85.0 and tap_count >= 12 and chant_action))
        if has_maya and veteran_name not in unlocked:
            unlocked.add(veteran_name)
            newly_unlocked.append(veteran_name)

    # Check Capstone All-4 Unlock
    all_four = [lead_name, rookie_name, specialist_name, veteran_name]
    capstone_ready = all(name in unlocked for name in all_four)

    return {
        "unlocked_npcs": [n for n in all_four if n in unlocked],
        "newly_unlocked": newly_unlocked,
        "capstone_ready": capstone_ready,
        "total_unlocked": len([n for n in all_four if n in unlocked]),
        "total_available": 4,
    }


def get_capstone_nft_badge(sport: str) -> Dict[str, Any]:
    """Returns the unique Capstone NFT badge unlocked when engaging with all mentors."""
    is_bball = "basket" in sport.lower()
    if is_bball:
        return {
            "title": "Thunder Row Inner Circle Key",
            "rarity": "Legendary",
            "color": "#f1c21b",
            "icon": "🗝️",
            "desc": "Conferred by Marcus Vance, Jordan Lee, Elena Rostova, and Devon Miller. Proves complete mastery of Section 114's 6th Man defense.",
            "perk": "Permanent 1.30x Section Synergy Multiplier & VIP Post-Game Press Box Pass",
            "hash_seed": "0xNFT-BB-THUNDER-ROW-INNER-CIRCLE",
        }
    else:
        return {
            "title": "End Zone Loyals Founding Shield",
            "rarity": "Legendary",
            "color": "#f1c21b",
            "icon": "🛡️",
            "desc": "Conferred by Sarah Jenkins, Alex Taylor, Carlos Mendez, and Maya Patel. Proves verified 12th Man initiation across Lot B and Section 115.",
            "perk": "Reserved VIP Lot B Tailgate Spot & 20% Permanent Official Team Store Discount",
            "hash_seed": "0xNFT-FB-ENDZONE-LOYALS-FOUNDING-SHIELD",
        }
