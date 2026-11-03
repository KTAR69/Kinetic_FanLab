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
import hashlib
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()

CLOUDANT_URL = os.getenv("CLOUDANT_URL")
CLOUDANT_APIKEY = os.getenv("CLOUDANT_APIKEY")
DB_NAME = os.getenv("CLOUDANT_DB_NAME", "kinetic_fanlab_db")
CLOUDANT_DB_NAME = DB_NAME
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(_BASE_DIR, "cloudant_engine_cache.json")
FEEDBACK_FILE = os.path.join(_BASE_DIR, "data", "member_feedback.json")

_lock = threading.RLock()

class CloudantEngineClient:
    """Production Cloudant client with automatic offline disk cache fallback."""

    def __init__(self):
        self.client = None
        self.is_connected = False
        self._mem_cache: Optional[Dict[str, Any]] = None
        self._mem_vouchers: Optional[List[Dict[str, Any]]] = None
        self._init_connection()
        self._init_local_cache()
        if self.is_connected:
            self._flush_uncommitted_queue()

    def _flush_uncommitted_queue(self):
        """Flushes any offline-queued operations to live IBM Cloudant with decoupled 3-phase lock release."""
        if not self.is_connected or not self.client:
            return
        
        # Phase 1: Read queue and snapshot documents under lock, then immediately release
        with _lock:
            cache = self._read_cache()
            queue = list(cache.get("uncommitted_queue", []))
            if not queue:
                return
            
            docs_map = {}
            for item in queue:
                op = item.get("op")
                doc_id = item.get("id")
                if op == "save_passport":
                    for p in cache.get("fan_passports", {}).values():
                        if p.get("_id") == doc_id:
                            docs_map[doc_id] = p
                            break
                elif op == "save_feedback":
                    for fb in cache.get("tester_feedback", []):
                        if fb.get("_id") == doc_id:
                            docs_map[doc_id] = fb
                            break
                elif op == "save_voucher":
                    for vch in cache.get("sponsor_vouchers", []):
                        if vch.get("_id") == doc_id:
                            docs_map[doc_id] = vch
                            break
                elif op == "save_user":
                    for u in cache.get("user_accounts", {}).values():
                        if u.get("_id") == doc_id:
                            docs_map[doc_id] = u
                            break

        # Phase 2: Perform network I/O OUTSIDE lock so other threads are never blocked
        remaining = []
        for item in queue:
            doc_id = item.get("id")
            doc_to_post = docs_map.get(doc_id)
            if doc_to_post:
                try:
                    self.client.post_document(db=DB_NAME, document=doc_to_post)
                except Exception:
                    remaining.append(item)

        # Phase 3: Update uncommitted queue under lock
        with _lock:
            fresh_cache = self._read_cache()
            fresh_cache["uncommitted_queue"] = remaining
            self._write_cache(fresh_cache)

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
            try:
                self.client.post_index(
                    db=DB_NAME,
                    index={"fields": ["type"]},
                    ddoc="kfl-type-idx",
                    name="by-type",
                    type="json"
                )
            except Exception:
                pass
        except Exception:
            self.is_connected = False

    def _init_local_cache(self):
        with _lock:
            if not os.path.exists(CACHE_FILE):
                initial_cache = {
                    "fan_passports": {},
                    "user_accounts": {},
                    "cmi_telemetry": [],
                    "storycards": [],
                    "tester_feedback": [],
                    "sponsor_vouchers": [],
                    "uncommitted_queue": []
                }
                with open(CACHE_FILE, "w", encoding="utf-8") as f:
                    json.dump(initial_cache, f, indent=2)

    def _read_cache(self) -> Dict[str, Any]:
        with _lock:
            if self._mem_cache is not None:
                return self._mem_cache
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "tester_feedback" not in data:
                        data["tester_feedback"] = []
                    if "sponsor_vouchers" not in data:
                        data["sponsor_vouchers"] = []
                    if "user_accounts" not in data:
                        data["user_accounts"] = {}
                    self._mem_cache = data
                    return data
            except Exception:
                self._mem_cache = {
                    "fan_passports": {},
                    "user_accounts": {},
                    "cmi_telemetry": [],
                    "storycards": [],
                    "tester_feedback": [],
                    "sponsor_vouchers": [],
                    "uncommitted_queue": []
                }
                return self._mem_cache

    def _write_cache(self, data: Dict[str, Any]):
        with _lock:
            self._mem_cache = data
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f)

    # --- DOCUMENT REPOSITORY METHODS ---

    def save_user_account(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Saves a registered user account to local cache, persistent JSON file, and IBM Cloudant NoSQL."""
        email = (user_data.get("email") or "").strip().lower()
        if not email:
            return {"status": "ERROR", "message": "Email required"}

        doc_id = f"user:{email}"
        doc = dict(user_data)
        doc["_id"] = doc_id
        doc["type"] = "user_account"
        doc["updated_at"] = time.time()

        # 1. Update in-memory & CACHE_FILE under lock
        with _lock:
            cache = self._read_cache()
            if "user_accounts" not in cache:
                cache["user_accounts"] = {}
            cache["user_accounts"][email] = doc
            cache["uncommitted_queue"].append({"op": "save_user", "id": doc_id, "timestamp": time.time()})
            self._write_cache(cache)

        # 2. Write to persistent registered_fans.json on disk
        try:
            users_file = os.path.join(_BASE_DIR, "data", "registered_fans.json")
            os.makedirs(os.path.dirname(users_file), exist_ok=True)
            current_users = {}
            if os.path.exists(users_file):
                with open(users_file, "r", encoding="utf-8") as f:
                    current_users = json.load(f)
            if not isinstance(current_users, dict):
                current_users = {}
            current_users[email] = doc
            with open(users_file, "w", encoding="utf-8") as f:
                json.dump(current_users, f, indent=2)
        except Exception as _ue:
            print(f"[save_user_account] warning saving to disk: {_ue}")

        # 3. Commit to live IBM Cloudant if connected
        if self.is_connected and self.client:
            try:
                try:
                    existing = self.client.get_document(db=DB_NAME, doc_id=doc_id).get_result()
                    if "_rev" in existing:
                        doc["_rev"] = existing["_rev"]
                except Exception:
                    pass
                self.client.post_document(db=DB_NAME, document=doc).get_result()
                return {"status": "SUCCESS", "doc_id": doc_id, "source": "CLOUDANT_LIVE"}
            except Exception as _ce:
                print(f"[save_user_account] Cloudant live post error: {_ce}")

        return {"status": "SUCCESS", "doc_id": doc_id, "source": "LOCAL_CACHE"}

    def get_user_account(self, email: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single user account by email across Cloudant live, persistent storage, and cache."""
        clean_email = email.strip().lower()
        doc_id = f"user:{clean_email}"

        # 1. Check live IBM Cloudant if connected
        if self.is_connected and self.client:
            try:
                doc = self.client.get_document(db=DB_NAME, doc_id=doc_id).get_result()
                if doc and isinstance(doc, dict):
                    return doc
            except Exception:
                pass

        # 2. Check persistent disk registered_fans.json
        users_file = os.path.join(_BASE_DIR, "data", "registered_fans.json")
        if os.path.exists(users_file):
            try:
                with open(users_file, "r", encoding="utf-8") as f:
                    u_dict = json.load(f)
                    if isinstance(u_dict, dict) and clean_email in u_dict:
                        return u_dict[clean_email]
            except Exception:
                pass

        # 3. Check CACHE_FILE
        cache = self._read_cache()
        if "user_accounts" in cache and clean_email in cache["user_accounts"]:
            return cache["user_accounts"][clean_email]

        return None

    def get_all_user_accounts(self) -> Dict[str, Any]:
        """Retrieves all registered user accounts across Cloudant live, persistent storage, and cache."""
        users_map = {}

        # 1. Read from persistent registered_fans.json on disk
        users_file = os.path.join(_BASE_DIR, "data", "registered_fans.json")
        if os.path.exists(users_file):
            try:
                with open(users_file, "r", encoding="utf-8") as f:
                    u_dict = json.load(f)
                    if isinstance(u_dict, dict):
                        users_map.update(u_dict)
            except Exception:
                pass

        # 2. Read from CACHE_FILE
        cache = self._read_cache()
        for email, doc in cache.get("user_accounts", {}).items():
            if email not in users_map:
                users_map[email] = doc

        # 3. Query live IBM Cloudant if available
        if self.is_connected and self.client:
            try:
                cloud_res = self.client.post_find(
                    db=DB_NAME,
                    selector={"type": "user_account"},
                    limit=500
                ).get_result()
                for doc in cloud_res.get("docs", []):
                    em = doc.get("email") or doc.get("_id", "").replace("user:", "")
                    if em:
                        users_map[em] = doc
            except Exception:
                pass

        return users_map

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
        """Saves tester validation feedback to local cache, persistent JSON file, and Cloudant database."""
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

        # 1. Update in-memory & CACHE_FILE
        cache = self._read_cache()
        if "tester_feedback" not in cache:
            cache["tester_feedback"] = []
        cache["tester_feedback"].append(doc)
        cache["uncommitted_queue"].append({"op": "save_feedback", "id": doc_id, "timestamp": time.time()})
        self._write_cache(cache)

        # 2. Persist to FEEDBACK_FILE (data/member_feedback.json)
        try:
            os.makedirs(os.path.dirname(FEEDBACK_FILE), exist_ok=True)
            existing_fb = []
            if os.path.exists(FEEDBACK_FILE):
                with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
                    existing_fb = json.load(f)
            if not isinstance(existing_fb, list):
                existing_fb = []
            existing_fb.append(doc)
            with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
                json.dump(existing_fb, f, indent=2)
        except Exception as _fe:
            print(f"[save_tester_feedback] warning saving to FEEDBACK_FILE: {_fe}")

        # 3. Commit to live IBM Cloudant if connected
        if self.is_connected and self.client:
            try:
                self.client.post_document(db=DB_NAME, document=doc).get_result()
                return {"status": "SUCCESS", "doc_id": doc_id, "source": "CLOUDANT_LIVE"}
            except Exception:
                pass

        return {"status": "SUCCESS", "doc_id": doc_id, "source": "LOCAL_CACHE"}

    def get_all_tester_feedback(self) -> List[Dict[str, Any]]:
        """Retrieves all submitted tester validation feedback records across Cloudant, persistent storage, and cache."""
        records = []
        seen_ids = set()

        # 1. Read from persistent FEEDBACK_FILE (data/member_feedback.json)
        if os.path.exists(FEEDBACK_FILE):
            try:
                with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
                    f_docs = json.load(f)
                    if isinstance(f_docs, list):
                        for d in f_docs:
                            if isinstance(d, dict) and d.get("_id") and d["_id"] not in seen_ids:
                                seen_ids.add(d["_id"])
                                records.append(d)
            except Exception:
                pass

        # 2. Read from CACHE_FILE (cloudant_engine_cache.json)
        cache = self._read_cache()
        for d in cache.get("tester_feedback", []):
            if isinstance(d, dict) and d.get("_id") and d["_id"] not in seen_ids:
                seen_ids.add(d["_id"])
                records.append(d)

        # 3. Query live IBM Cloudant if available
        if self.is_connected and self.client:
            try:
                cloud_res = self.client.post_find(
                    db=DB_NAME,
                    selector={"type": "tester_feedback"},
                    limit=500
                ).get_result()
                for d in cloud_res.get("docs", []):
                    if isinstance(d, dict) and d.get("_id") and d["_id"] not in seen_ids:
                        seen_ids.add(d["_id"])
                        records.append(d)
            except Exception:
                pass

        return records

    def save_sponsor_voucher(
        self,
        voucher_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Saves an authenticated sponsor voucher record to local cache, persistent JSON file, and Cloudant database."""
        v_hash = voucher_data.get("claim_hash", f"0xVCH-{int(time.time())}")
        doc_id = f"voucher:{v_hash}"
        salt = f"{v_hash}:{voucher_data.get('claimed_by_handle')}:{voucher_data.get('discount_code')}"
        doc = {
            "_id": doc_id,
            "type": "sponsor_voucher",
            "claim_hash": v_hash,
            "brand": voucher_data.get("brand", "Partner"),
            "discount_code": voucher_data.get("discount_code", "CLUTCH26"),
            "retail_value": voucher_data.get("retail_value", 6.50),
            "partner_fee": voucher_data.get("partner_fee", 4.85),
            "claimed_by_name": voucher_data.get("claimed_by_name", "Anonymous"),
            "claimed_by_handle": voucher_data.get("claimed_by_handle", "@anonymous"),
            "seat": voucher_data.get("seat", "Section 114"),
            "trigger_cmi": voucher_data.get("trigger_cmi", 80.0),
            "sport": voucher_data.get("sport", "Basketball"),
            "team": voucher_data.get("team", "Texas Longhorns"),
            "timestamp": voucher_data.get("claimed_at_timestamp", time.time()),
            "formatted_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "integrity_sha256": hashlib.sha256(salt.encode("utf-8")).hexdigest()
        }

        # 1. Post to live Cloudant if connected
        cloud_success = False
        cloud_res = None
        if self.is_connected and self.client:
            try:
                cloud_res = self.client.post_document(db=DB_NAME, document=doc).get_result()
                cloud_success = True
            except Exception:
                cloud_success = False

        # 2. Atomic update to memory cache, queue, and persistent disk under lock
        # IMPORTANT: self.client.post_document() is called ABOVE (lines 411-416), OUTSIDE this lock.
        # Do NOT move network I/O inside this with _lock: block — it would block all concurrent sessions.
        with _lock:
            cache = self._read_cache()
            if "sponsor_vouchers" not in cache:
                cache["sponsor_vouchers"] = []

            existing = False
            for idx, v in enumerate(cache["sponsor_vouchers"]):
                if v.get("claim_hash") == v_hash:
                    cache["sponsor_vouchers"][idx] = doc
                    existing = True
                    break
            if not existing:
                cache["sponsor_vouchers"].append(doc)

            if not cloud_success:
                cache["uncommitted_queue"].append({
                    "op": "save_voucher",
                    "id": doc_id,
                    "timestamp": time.time()
                })
            # Rolling cap: prevent unbounded offline queue and voucher cache bloat
            if len(cache.get("uncommitted_queue", [])) > 100:
                cache["uncommitted_queue"] = cache["uncommitted_queue"][-100:]
            if len(cache.get("sponsor_vouchers", [])) > 100:
                cache["sponsor_vouchers"] = cache["sponsor_vouchers"][-100:]

            self._write_cache(cache)

            # Write to persistent disk data/claimed_vouchers.json
            vch_disk_path = os.path.join(_BASE_DIR, "data", "claimed_vouchers.json")
            try:
                os.makedirs(os.path.dirname(vch_disk_path), exist_ok=True)
                if self._mem_vouchers is None:
                    v_list = []
                    if os.path.exists(vch_disk_path):
                        try:
                            with open(vch_disk_path, "r", encoding="utf-8") as f:
                                v_list = json.load(f)
                                if not isinstance(v_list, list):
                                    v_list = []
                        except Exception:
                            v_list = []
                    self._mem_vouchers = v_list
                self._mem_vouchers = [v for v in self._mem_vouchers if v.get("claim_hash") != v_hash]
                self._mem_vouchers.append(doc)
                if len(self._mem_vouchers) > 100:
                    self._mem_vouchers = self._mem_vouchers[-100:]
                with open(vch_disk_path, "w", encoding="utf-8") as f:
                    json.dump(self._mem_vouchers, f)
            except Exception:
                pass

        if cloud_success and cloud_res:
            return {
                "status": "SUCCESS",
                "source": "LIVE_CLOUDANT",
                "id": cloud_res.get("id"),
                "rev": cloud_res.get("rev"),
                "doc": doc
            }
        return {
            "status": "SUCCESS",
            "source": "LOCAL_CACHE",
            "id": doc_id,
            "doc": doc
        }

    def get_all_sponsor_vouchers(self) -> List[Dict[str, Any]]:
        """Retrieves all authenticated sponsor voucher documents across live Cloudant, local JSON, and cache."""
        records = []
        seen_hashes = set()

        with _lock:
            if self._mem_vouchers is not None:
                for d in self._mem_vouchers:
                    if isinstance(d, dict) and d.get("claim_hash") and d["claim_hash"] not in seen_hashes:
                        seen_hashes.add(d["claim_hash"])
                        records.append(d)
            else:
                vch_disk_path = os.path.join(_BASE_DIR, "data", "claimed_vouchers.json")
                if os.path.exists(vch_disk_path):
                    try:
                        with open(vch_disk_path, "r", encoding="utf-8") as f:
                            v_docs = json.load(f)
                            if isinstance(v_docs, list):
                                for d in v_docs:
                                    if isinstance(d, dict) and d.get("claim_hash") and d["claim_hash"] not in seen_hashes:
                                        seen_hashes.add(d["claim_hash"])
                                        records.append(d)
                    except Exception:
                        pass

            cache = self._read_cache()
            for d in cache.get("sponsor_vouchers", []):
                if isinstance(d, dict) and d.get("claim_hash") and d["claim_hash"] not in seen_hashes:
                    seen_hashes.add(d["claim_hash"])
                    records.append(d)

        if self.is_connected and self.client:
            try:
                cloud_res = self.client.post_find(
                    db=DB_NAME,
                    selector={"type": "sponsor_voucher"},
                    limit=500
                ).get_result()
                for d in cloud_res.get("docs", []):
                    if isinstance(d, dict) and d.get("claim_hash") and d["claim_hash"] not in seen_hashes:
                        seen_hashes.add(d["claim_hash"])
                        records.append(d)
            except Exception:
                pass

        return records

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

def save_sponsor_voucher(*args, **kwargs):
    return _engine_instance.save_sponsor_voucher(*args, **kwargs)

def get_all_sponsor_vouchers(*args, **kwargs):
    return _engine_instance.get_all_sponsor_vouchers(*args, **kwargs)

def save_user_account(*args, **kwargs):
    return _engine_instance.save_user_account(*args, **kwargs)

def get_user_account(*args, **kwargs):
    return _engine_instance.get_user_account(*args, **kwargs)

def get_all_user_accounts(*args, **kwargs):
    return _engine_instance.get_all_user_accounts(*args, **kwargs)