#!/usr/bin/env python3
"""
Kinetic FanLab — OpenAPI 3.0.0 Skill Validator
==============================================================================
Standalone script that inspects kinetic_fanlab_skill.json and verifies:
  1.  Document structure: version, info, servers, paths, components
  2.  OpenAPI 3.0.0 strict compliance (required top-level keys, formats)
  3.  watsonx Orchestrate readiness:
       - operationId present on every operation
       - requestBody uses application/json
       - Every operation has at least a 200 and 400 response
       - All $ref targets exist in components/schemas
       - Security scheme is HTTP bearer (IBM Cloud IAM)
  4.  Kinetic FanLab contract checks:
       - CmiRequest contains the 4 required signal fields
       - CmiResponse enum covers exactly: Baseline, Moderate, High, Maximum
       - NarrativeResponse powered_by matches the canonical attribution string

Usage:
    python validate_skill.py [path/to/kinetic_fanlab_skill.json]
    python validate_skill.py                   # defaults to same-dir skill file

Exit codes:
    0 — all checks passed
    1 — one or more validation failures
==============================================================================
"""

import json
import os
import sys
from typing import Any, Dict, List, Tuple

# ---------------------------------------------------------------------------
# Canonical constants
# ---------------------------------------------------------------------------
OPENAPI_VERSION_REQUIRED = "3.0.0"
REQUIRED_TOP_LEVEL_KEYS = {"openapi", "info", "servers", "paths", "components"}
REQUIRED_INFO_KEYS = {"title", "description", "version"}
WXO_REQUIRED_RESPONSE_CODES = {"200", "400"}
EXPECTED_SECURITY_SCHEME_TYPE = "http"
EXPECTED_SECURITY_SCHEME = "bearer"
EXPECTED_BEARER_FORMAT = "IBM Cloud IAM Token"

# Kinetic FanLab contract assertions
CMI_REQUEST_REQUIRED_FIELDS = {"decibels", "heart_rate_bpm", "tap_rate", "vocal_urgency"}
CMI_TIER_ENUM = {"Baseline", "Moderate", "High", "Maximum"}
NARRATIVE_POWERED_BY = "IBM watsonx & Granite Foundation Models"
EXPECTED_OPERATIONS = {"calculateCmi", "evaluatePacing", "generateNarrative"}


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

class ValidationResult:
    """Collects pass/fail results with descriptive messages."""

    def __init__(self):
        self.passed: List[str] = []
        self.failed: List[str] = []

    def ok(self, msg: str) -> None:
        self.passed.append(msg)

    def fail(self, msg: str) -> None:
        self.failed.append(msg)

    def check(self, condition: bool, pass_msg: str, fail_msg: str) -> bool:
        if condition:
            self.ok(pass_msg)
        else:
            self.fail(fail_msg)
        return condition

    @property
    def success(self) -> bool:
        return len(self.failed) == 0

    def print_report(self) -> None:
        print("=" * 85)
        print("  KINETIC FANLAB -- OPENAPI SKILL VALIDATOR")
        print("=" * 85)
        print(f"\n  [PASS] Checks Passed : {len(self.passed)}")
        print(f"  [FAIL] Checks Failed : {len(self.failed)}")
        print()
        if self.passed:
            print("-" * 80)
            print("  PASSED")
            print("-" * 80)
            for msg in self.passed:
                print(f"  [OK]  {msg}")
        if self.failed:
            print()
            print("-" * 80)
            print("  FAILED")
            print("-" * 80)
            for msg in self.failed:
                print(f"  [!!]  {msg}")
        print()
        status = "ALL CHECKS PASSED -- watsonx Orchestrate Ready [OK]" if self.success \
                 else "VALIDATION FAILURES DETECTED -- Review Issues Above [!!]"
        print("=" * 85)
        print(f"  {status}")
        print("  Powered by IBM watsonx & Granite Foundation Models")
        print("=" * 85)


def _resolve_ref(ref: str, spec: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Resolve a JSON $ref like '#/components/schemas/CmiRequest' against the spec.
    Returns (found: bool, description: str).
    """
    if not ref.startswith("#/"):
        return False, f"External $ref not supported: {ref}"
    parts = ref.lstrip("#/").split("/")
    node = spec
    for part in parts:
        if not isinstance(node, dict) or part not in node:
            return False, f"$ref target not found: {ref}"
        node = node[part]
    return True, ref


# ---------------------------------------------------------------------------
# Validation sections
# ---------------------------------------------------------------------------

def validate_top_level_structure(spec: Dict[str, Any], r: ValidationResult) -> None:
    """Section 1: Top-level required keys and OpenAPI version."""
    present = set(spec.keys())
    missing = REQUIRED_TOP_LEVEL_KEYS - present
    r.check(not missing,
            "Top-level keys present: openapi, info, servers, paths, components",
            f"Missing top-level keys: {missing}")

    version = spec.get("openapi", "")
    r.check(version == OPENAPI_VERSION_REQUIRED,
            f"openapi version == '{OPENAPI_VERSION_REQUIRED}'",
            f"openapi version is '{version}', expected '{OPENAPI_VERSION_REQUIRED}'")

    info = spec.get("info", {})
    missing_info = REQUIRED_INFO_KEYS - set(info.keys())
    r.check(not missing_info,
            "info block contains title, description, version",
            f"info block missing: {missing_info}")

    servers = spec.get("servers", [])
    r.check(isinstance(servers, list) and len(servers) >= 1,
            "servers array has at least one entry",
            "servers array is empty or absent")


def validate_operations(spec: Dict[str, Any], r: ValidationResult) -> None:
    """Section 2: Every path operation has operationId, requestBody, and required responses."""
    paths = spec.get("paths", {})
    found_operation_ids = set()

    for path, path_item in paths.items():
        for method, operation in path_item.items():
            if method.startswith("x-") or not isinstance(operation, dict):
                continue

            op_id = operation.get("operationId", "")
            r.check(bool(op_id),
                    f"{method.upper()} {path}: operationId present ('{op_id}')",
                    f"{method.upper()} {path}: missing operationId (required by watsonx Orchestrate)")
            found_operation_ids.add(op_id)

            # requestBody must use application/json
            req_body = operation.get("requestBody", {})
            content = req_body.get("content", {})
            r.check("application/json" in content,
                    f"{op_id}: requestBody uses application/json",
                    f"{op_id}: requestBody missing application/json content type")

            # Required response codes
            responses = operation.get("responses", {})
            for code in WXO_REQUIRED_RESPONSE_CODES:
                r.check(code in responses,
                        f"{op_id}: response {code} defined",
                        f"{op_id}: missing required response code {code}")

    # Verify all expected operations are present
    missing_ops = EXPECTED_OPERATIONS - found_operation_ids
    r.check(not missing_ops,
            f"All expected operationIds present: {EXPECTED_OPERATIONS}",
            f"Missing expected operationIds: {missing_ops}")


def validate_refs(spec: Dict[str, Any], r: ValidationResult) -> None:
    """Section 3: All $ref targets resolve within components/schemas."""
    refs_checked: set = set()

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            if "$ref" in node:
                ref = node["$ref"]
                if ref not in refs_checked:
                    refs_checked.add(ref)
                    found, msg = _resolve_ref(ref, spec)
                    r.check(found,
                            f"$ref resolved: {ref}",
                            f"Unresolvable $ref: {ref}")
            else:
                for v in node.values():
                    walk(v)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(spec.get("paths", {}))


def validate_security(spec: Dict[str, Any], r: ValidationResult) -> None:
    """Section 4: Security scheme is IBM Cloud IAM bearer token."""
    schemes = spec.get("components", {}).get("securitySchemes", {})
    r.check(bool(schemes),
            "securitySchemes block is defined",
            "securitySchemes block is missing")

    iam_scheme = schemes.get("IBMCloudIAM", {})
    r.check(iam_scheme.get("type") == EXPECTED_SECURITY_SCHEME_TYPE,
            f"IBMCloudIAM.type == '{EXPECTED_SECURITY_SCHEME_TYPE}'",
            f"IBMCloudIAM.type is '{iam_scheme.get('type')}', expected '{EXPECTED_SECURITY_SCHEME_TYPE}'")
    r.check(iam_scheme.get("scheme") == EXPECTED_SECURITY_SCHEME,
            f"IBMCloudIAM.scheme == '{EXPECTED_SECURITY_SCHEME}'",
            f"IBMCloudIAM.scheme is '{iam_scheme.get('scheme')}', expected '{EXPECTED_SECURITY_SCHEME}'")
    r.check(iam_scheme.get("bearerFormat") == EXPECTED_BEARER_FORMAT,
            f"IBMCloudIAM.bearerFormat == '{EXPECTED_BEARER_FORMAT}'",
            f"IBMCloudIAM.bearerFormat is '{iam_scheme.get('bearerFormat')}'")

    global_security = spec.get("security", [])
    r.check(isinstance(global_security, list) and len(global_security) > 0,
            "Global security block references IBMCloudIAM",
            "Global security block is missing or empty")


def validate_kinetic_contracts(spec: Dict[str, Any], r: ValidationResult) -> None:
    """Section 5: Kinetic FanLab contract assertions on schema definitions."""
    schemas = spec.get("components", {}).get("schemas", {})

    # CmiRequest: required signal fields
    cmi_req = schemas.get("CmiRequest", {})
    required_fields = set(cmi_req.get("required", []))
    properties = set(cmi_req.get("properties", {}).keys())
    combined = required_fields | properties
    missing_fields = CMI_REQUEST_REQUIRED_FIELDS - combined
    r.check(not missing_fields,
            f"CmiRequest contains all required signal fields: {CMI_REQUEST_REQUIRED_FIELDS}",
            f"CmiRequest missing signal fields: {missing_fields}")

    # CmiResponse: operational_tier enum must exactly match expected values
    cmi_resp = schemas.get("CmiResponse", {})
    tier_prop = cmi_resp.get("properties", {}).get("operational_tier", {})
    tier_enum = set(tier_prop.get("enum", []))
    r.check(tier_enum == CMI_TIER_ENUM,
            f"CmiResponse.operational_tier enum == {CMI_TIER_ENUM}",
            f"CmiResponse.operational_tier enum mismatch: got {tier_enum}")

    # NarrativeResponse: powered_by description references canonical string
    narr_resp = schemas.get("NarrativeResponse", {})
    powered_by_desc = narr_resp.get("properties", {}).get("powered_by", {}).get("description", "")
    r.check(NARRATIVE_POWERED_BY in powered_by_desc,
            f"NarrativeResponse.powered_by references '{NARRATIVE_POWERED_BY}'",
            f"NarrativeResponse.powered_by description is '{powered_by_desc}'")

    # Sport enum must include exactly Basketball and Football
    sport_enum_found = False
    for schema_name in ["PacingRequest", "NarrativeRequest"]:
        schema = schemas.get(schema_name, {})
        sport_prop = schema.get("properties", {}).get("sport", {})
        sport_enum = set(sport_prop.get("enum", []))
        if sport_enum:
            sport_enum_found = True
            r.check({"Basketball", "Football"}.issubset(sport_enum),
                    f"{schema_name}.sport enum includes Basketball and Football",
                    f"{schema_name}.sport enum is '{sport_enum}'")
    if not sport_enum_found:
        r.fail("Could not locate sport enum in PacingRequest or NarrativeRequest")

    # Verify numeric range constraints on vocal_urgency (0–1) and tap_rate (0–15)
    vu_prop = cmi_req.get("properties", {}).get("vocal_urgency", {})
    r.check(vu_prop.get("minimum") == 0.0 and vu_prop.get("maximum") == 1.0,
            "CmiRequest.vocal_urgency range constrained to 0.0–1.0",
            f"CmiRequest.vocal_urgency range: min={vu_prop.get('minimum')}, max={vu_prop.get('maximum')}")

    tap_prop = cmi_req.get("properties", {}).get("tap_rate", {})
    r.check(tap_prop.get("minimum") == 0.0 and tap_prop.get("maximum") == 15.0,
            "CmiRequest.tap_rate range constrained to 0.0–15.0",
            f"CmiRequest.tap_rate range: min={tap_prop.get('minimum')}, max={tap_prop.get('maximum')}")


# ---------------------------------------------------------------------------
# Main entrypoint
# ---------------------------------------------------------------------------

def validate(skill_path: str) -> bool:
    """Load and fully validate the OpenAPI skill file. Returns True if all checks pass."""
    if not os.path.isfile(skill_path):
        print(f"ERROR: File not found: {skill_path}")
        return False

    with open(skill_path, "r", encoding="utf-8") as fh:
        try:
            spec: Dict[str, Any] = json.load(fh)
        except json.JSONDecodeError as exc:
            print(f"ERROR: Invalid JSON — {exc}")
            return False

    print(f"\n  Validating: {os.path.abspath(skill_path)}\n")

    r = ValidationResult()
    validate_top_level_structure(spec, r)
    validate_operations(spec, r)
    validate_refs(spec, r)
    validate_security(spec, r)
    validate_kinetic_contracts(spec, r)

    r.print_report()
    return r.success


if __name__ == "__main__":
    default_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kinetic_fanlab_skill.json")
    target = sys.argv[1] if len(sys.argv) > 1 else default_path
    ok = validate(target)
    sys.exit(0 if ok else 1)
