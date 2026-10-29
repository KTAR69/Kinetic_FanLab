"""
==============================================================================
Kinetic FanLab — IBM Cloudant NoSQL Engine & Offline Circuit Breaker
Week 5 Milestone & User Validation Extension (Track 3: Fan-Centric Sports)

Dedicated enterprise module:
1. Fan Passports (permanent hashes, tiers, wearable anchors)
2. CMI Telemetry Snapshots (35/25/20/20 component breakdown)
3. Reality Delta StoryCards (Granite narratives & Defense Belt awards)
4. Tester Validation Feedback (User testing surveys, CMI ratings, verbatim feedback)
Features disk-backed caching and offline circuit-breaker recovery.
==============================================================================
"""

import os
import json
import time
import threading
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()

CLOUDANT_URL = os.getenv("CLOUDANT_URL")
CLOUDANT_APIKEY = os.getenv("CLOUDANT_APIKEY")
DB_NAME = os.getenv("CLOUDANT_DB_NAME", "kinetic_fanlab_db")
CACHE_FILE = "cloudant_engine_cache.json"

_lock = threading.Lock()

class CloudantEngineClient:
    """Production Cloudant client with automatic offline disk cache fallback."""

    def __init__(self):
        self.client = None
        self.is_connected = False
        self._init_connection()
        self._init_local_cache()
        # Fix #4: replay any ops queued while Cloudant was offline in a prior session.
        if self.is_connected:
            self._flush_uncommitted_queue()

    def _init_connection(self):
        if not CLOUDANT_URL or not CLOUDANT_APIKEY:
            return

        try:
            from ibmcloudant.cloudant_v1 import CloudantV1
            from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
            authenticator = IAMAuthenticator(CLOUDANT_APIKEY)
            self.client = CloudantV1(authenticator=authenticator)
            self.client.set_service_url(CLOUDANT_URL)
            self.is_connected = True
        except Exception:
            self.is_connected = False

    def _init_local_cache(self):
        with _lock:
            if not os.path.exists(CACHE_FILE):
                initial_cache = {
                    "fan_passports": {},
                    "cmi_telemetry": [],
                    "storycards": [],
                    "tester_feedback": [],
                    "uncommitted_queue": []
                }
                with open(CACHE_FILE, "w", encoding="utf-8") as f:
                    json.dump(initial_cache, f, indent=2)

    def _read_cache(self) -> Dict[str, Any]:
        with _lock:
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "tester_feedback" not in data:
                        data["tester_feedback"] = []
                    return data
            except Exception:
                return {
                    "fan_passports": {},
                    "cmi_telemetry": [],
                    "storycards": [],
                    "tester_feedback": [],
                    "uncommitted_queue": []
                }

    def _write_cache(self, data: Dict[str, Any]):
        with _lock:
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

    def _flush_uncommitted_queue(self):
        """Replays queued write ops that accumulated while Cloudant was offline.

        Each entry in uncommitted_queue carries an ``op`` key that maps to the
        corresponding in-memory record already written to the local cache.  We
        simply re-POST those records to Cloudant and clear the queue on success.
        """
        if not (self.is_connected and self.client):
            return
        try:
            cache = self._read_cache()
            queue = cache.get("uncommitted_queue", [])
            if not queue:
                return

            flushed_ids: set = set()
            for entry in queue:
                op = entry.get("op", "")
                doc_id = entry.get("id", "")
                if not doc_id:
                    continue
                try:
                    if op == "save_passport":
                        # Locate the document in fan_passports by member_hash extracted from doc_id
                        member_hash = doc_id.replace("passport:", "")
                        doc = cache.get("fan_passports", {}).get(member_hash)
                    elif op == "save_feedback":
                        doc = next(
                            (d for d in cache.get("tester_feedback", []) if d.get("_id") == doc_id),
                            None,
                        )
                    else:
                        doc = None

                    if doc:
                        self.client.post_document(db=DB_NAME, document=doc).get_result()
                        flushed_ids.add(doc_id)
                except Exception:
                    pass  # leave un-flushed items in the queue for the next restart

            # Remove only successfully flushed entries
            cache["uncommitted_queue"] = [
                e for e in queue if e.get("id") not in flushed_ids
            ]
            self._write_cache(cache)
        except Exception:
            pass  # never crash startup due to a queue flush failure

    # --- DOCUMENT REPOSITORY METHODS ---

    def save_fan_passport(
        self,
        member_name: str,
        member_hash: str,
        section_id: str,
        sport: str,
        role: str,
        tier: int,
        device_anchor: str,
        early_multiplier: float = 1.0
    ) -> Dict[str, Any]:
        """Saves or updates a permanent fan passport record."""
        doc_id = f"passport:{member_hash}"
        doc = {
            "_id": doc_id,
            "type": "fan_passport",
            "member_name": member_name,
            "member_hash": member_hash,
            "section_id": section_id,
            "sport": sport,
            "role": role,
            "tier": tier,
            "device_anchor": device_anchor,
            "early_multiplier": early_multiplier,
            "updated_at": time.time()
        }

        cache = self._read_cache()
        cache["fan_passports"][member_hash] = doc
        cache["uncommitted_queue"].append({"op": "save_passport", "id": doc_id, "timestamp": time.time()})
        self._write_cache(cache)

        return {"status": "SUCCESS", "doc_id": doc_id, "source": "LOCAL_CACHE"}

    def save_telemetry_snapshot(
        self,
        section_id: str,
        sport: str,
        cmi: float,
        tier: str,
        db: float,
        hr: float,
        taps: float,
        vu: float,
        fan_count: int = 50
    ) -> Dict[str, Any]:
        """Records a contract-exact CMI telemetry time-series snapshot."""
        doc_id = f"cmi:{sport.lower()}:{section_id.lower().replace(' ', '')}:{int(time.time()*1000)}"
        doc = {
            "_id": doc_id,
            "type": "cmi_telemetry",
            "section_id": section_id,
            "sport": sport,
            "cmi": cmi,
            "tier": tier,
            "components": {
                "acoustic_db": db,
                "heart_rate_bpm": hr,
                "taps_per_sec": taps,
                "vocal_urgency": vu
            },
            "fan_count": fan_count,
            "timestamp": time.time()
        }

        cache = self._read_cache()
        cache["cmi_telemetry"].append(doc)
        if len(cache["cmi_telemetry"]) > 200:
            cache["cmi_telemetry"] = cache["cmi_telemetry"][-200:]
        self._write_cache(cache)

        return {"status": "SUCCESS", "doc_id": doc_id, "cmi": cmi}

    def save_storycard(
        self,
        headline: str,
        winning_section: str,
        outcome: str,
        pre_cmi: float,
        peak_cmi: float,
        granite_narrative: str
    ) -> Dict[str, Any]:
        """Records an official proof-of-momentum StoryCard and Granite narrative."""
        doc_id = f"storycard:{winning_section.lower().replace(' ', '')}:{int(time.time())}"
        surge = round(peak_cmi - pre_cmi, 1)
        doc = {
            "_id": doc_id,
            "type": "reality_delta_card",
            "headline": headline,
            "winning_section": winning_section,
            "outcome": outcome,
            "pre_cmi": pre_cmi,
            "peak_cmi": peak_cmi,
            "surge": surge,
            "defense_belt_awarded": True,
            "granite_narrative": granite_narrative,
            "timestamp": time.time()
        }

        cache = self._read_cache()
        cache["storycards"].append(doc)
        self._write_cache(cache)

        return {"status": "SUCCESS", "doc_id": doc_id, "headline": headline}

    def get_recent_storycards(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieves recent StoryCards."""
        cache = self._read_cache()
        return cache.get("storycards", [])[-limit:]

    def save_tester_feedback(
        self,
        tester_name: str,
        tester_handle: str,
        tester_role: str,
        cmi_rating: int,
        features_tested: List[str],
        favorite_feature: str,
        improvement_feedback: str,
        sport: str = "Basketball"
    ) -> Dict[str, Any]:
        """Saves tester validation feedback to local cache and Cloudant database."""
        clean_handle = (tester_handle or "tester").replace("@", "").lower().strip()
        doc_id = f"feedback:{clean_handle}:{int(time.time())}"
        doc = {
            "_id": doc_id,
            "type": "tester_feedback",
            "tester_name": tester_name.strip() or "Anonymous Fan",
            "tester_handle": tester_handle.strip() or "@anonymous",
            "tester_role": tester_role,
            "cmi_rating": int(cmi_rating),
            "features_tested": features_tested,
            "favorite_feature": favorite_feature.strip(),
            "improvement_feedback": improvement_feedback.strip(),
            "sport": sport,
            "timestamp": time.time(),
            "formatted_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        }

        cache = self._read_cache()
        if "tester_feedback" not in cache:
            cache["tester_feedback"] = []
        cache["tester_feedback"].append(doc)
        cache["uncommitted_queue"].append({"op": "save_feedback", "id": doc_id, "timestamp": time.time()})
        self._write_cache(cache)

        if self.is_connected and self.client:
            try:
                self.client.post_document(db=DB_NAME, document=doc).get_result()
                return {"status": "SUCCESS", "doc_id": doc_id, "source": "CLOUDANT_LIVE"}
            except Exception:
                pass

        return {"status": "SUCCESS", "doc_id": doc_id, "source": "LOCAL_CACHE"}

    def get_all_tester_feedback(self) -> List[Dict[str, Any]]:
        """Retrieves all submitted tester validation feedback records."""
        cache = self._read_cache()
        return cache.get("tester_feedback", [])

# Global Singleton Client
_engine_instance = CloudantEngineClient()

def save_fan_passport(*args, **kwargs):
    return _engine_instance.save_fan_passport(*args, **kwargs)

def save_telemetry_snapshot(*args, **kwargs):
    return _engine_instance.save_telemetry_snapshot(*args, **kwargs)

def save_storycard(*args, **kwargs):
    return _engine_instance.save_storycard(*args, **kwargs)

def get_recent_storycards(*args, **kwargs):
    return _engine_instance.get_recent_storycards(*args, **kwargs)

def save_tester_feedback(*args, **kwargs):
    return _engine_instance.save_tester_feedback(*args, **kwargs)

def get_all_tester_feedback(*args, **kwargs):
    return _engine_instance.get_all_tester_feedback(*args, **kwargs)