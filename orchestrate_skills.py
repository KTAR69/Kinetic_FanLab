"""
==============================================================================
Kinetic FanLab — watsonx Orchestrate ADK OpenAPI 3.0 Skill Manifests
Week 5 Milestone (Track 3: Fan-Centric Sports & Entertainment)

Generates official OpenAPI 3.0 skill contracts for the 3 IBM Agent Archetypes:
1. The Invisible Coordinator Skill (/evaluate_game_clock)
2. The Knowledge Synthesizer Skill (/synthesize_momentum)
3. The System Optimizer Skill (/calculate_section_standings)
==============================================================================
"""

import json
import os
from typing import Any, Dict

SKILLS_DIR = "orchestrate_specs"


def get_coordinator_skill_spec() -> Dict[str, Any]:
  """OpenAPI 3.0 specification for Agent 1: The Invisible Coordinator."""
  return {
      "openapi": "3.0.0",
      "info": {
          "title": "Kinetic FanLab — Invisible Coordinator Skill",
          "description": (
              "Coordinates stadium crowd pacing, bleacher stomps, and clutch"
              " multipliers based on live game clock."
          ),
          "version": "1.0.0",
      },
      "servers": [{"url": "https://api.kineticfanlab.com/v1/coordinator"}],
      "paths": {
          "/evaluate_game_clock": {
              "post": {
                  "summary": (
                      "Evaluates game context and returns crowd pacing"
                      " directives"
                  ),
                  "operationId": "evaluateGameClock",
                  "requestBody": {
                      "required": True,
                      "content": {
                          "application/json": {
                              "schema": {
                                  "type": "object",
                                  "required": ["sport", "game_context"],
                                  "properties": {
                                      "sport": {
                                          "type": "string",
                                          "enum": ["Basketball", "Football"],
                                      },
                                      "game_context": {
                                          "type": "string",
                                          "example": (
                                              "Opponent Free Throw 2 (Clutch)"
                                          ),
                                      },
                                      "time_remaining_sec": {
                                          "type": "number",
                                          "example": 10.0,
                                      },
                                  },
                              }
                          }
                      },
                  },
                  "responses": {
                      "200": {
                          "description": (
                              "Calculated pacing directive and multiplier"
                          ),
                          "content": {
                              "application/json": {
                                  "schema": {
                                      "type": "object",
                                      "properties": {
                                          "clutch_active": {"type": "boolean"},
                                          "multiplier": {
                                              "type": "number",
                                              "example": 2.0,
                                          },
                                          "pacing_directive": {
                                              "type": "string"
                                          },
                                          "tactic": {"type": "string"},
                                      },
                                  }
                              }
                          },
                      }
                  },
              }
          }
      },
  }


def get_synthesizer_skill_spec() -> Dict[str, Any]:
  """OpenAPI 3.0 specification for Agent 2: The Knowledge Synthesizer."""
  return {
      "openapi": "3.0.0",
      "info": {
          "title": "Kinetic FanLab — Knowledge Synthesizer Skill",
          "description": (
              "Ingests multimodal acoustic, biometric, and tap telemetry to"
              " compute the contract-exact CMI."
          ),
          "version": "1.0.0",
      },
      "servers": [{"url": "https://api.kineticfanlab.com/v1/synthesizer"}],
      "paths": {
          "/synthesize_momentum": {
              "post": {
                  "summary": (
                      "Computes 0–100 Calculated Momentum Index (CMI) from"
                      " normalized signals"
                  ),
                  "operationId": "synthesizeMomentum",
                  "requestBody": {
                      "required": True,
                      "content": {
                          "application/json": {
                              "schema": {
                                  "type": "object",
                                  "required": [
                                      "decibels",
                                      "heart_rate_bpm",
                                      "taps_per_sec",
                                      "vocal_urgency",
                                  ],
                                  "properties": {
                                      "decibels": {
                                          "type": "number",
                                          "minimum": 60.0,
                                          "maximum": 115.0,
                                      },
                                      "heart_rate_bpm": {
                                          "type": "number",
                                          "minimum": 60.0,
                                          "maximum": 160.0,
                                      },
                                      "taps_per_sec": {
                                          "type": "number",
                                          "minimum": 0.0,
                                          "maximum": 15.0,
                                      },
                                      "vocal_urgency": {
                                          "type": "number",
                                          "minimum": 0.0,
                                          "maximum": 1.0,
                                      },
                                  },
                              }
                          }
                      },
                  },
                  "responses": {
                      "200": {
                          "description": (
                              "Computed CMI score and operational tier"
                          ),
                          "content": {
                              "application/json": {
                                  "schema": {
                                      "type": "object",
                                      "properties": {
                                          "cmi": {
                                              "type": "number",
                                              "example": 81.9,
                                          },
                                          "tier": {
                                              "type": "string",
                                              "enum": [
                                                  "Baseline",
                                                  "Moderate",
                                                  "High",
                                                  "Maximum",
                                              ],
                                          },
                                          "normalized_components": {
                                              "type": "object"
                                          },
                                      },
                                  }
                              }
                          },
                      }
                  },
              }
          }
      },
  }


def get_optimizer_skill_spec() -> Dict[str, Any]:
  """OpenAPI 3.0 specification for Agent 3: The System Optimizer."""
  return {
      "openapi": "3.0.0",
      "info": {
          "title": "Kinetic FanLab — System Optimizer Skill",
          "description": (
              "Calculates per-capita section standings, issues Chaser Alerts,"
              " and synthesizes post-play Reality Delta narratives."
          ),
          "version": "1.0.0",
      },
      "servers": [{"url": "https://api.kineticfanlab.com/v1/optimizer"}],
      "paths": {
          "/calculate_section_standings": {
              "post": {
                  "summary": (
                      "Normalizes raw section scores by checked-in fan volume"
                  ),
                  "operationId": "calculateSectionStandings",
                  "requestBody": {
                      "required": True,
                      "content": {
                          "application/json": {
                              "schema": {
                                  "type": "object",
                                  "required": ["section_batches"],
                                  "properties": {
                                      "section_batches": {
                                          "type": "array",
                                          "items": {
                                              "type": "object",
                                              "required": [
                                                  "name",
                                                  "cmi",
                                                  "checked_in_fans",
                                              ],
                                              "properties": {
                                                  "name": {"type": "string"},
                                                  "cmi": {"type": "number"},
                                                  "checked_in_fans": {
                                                      "type": "integer"
                                                  },
                                                  "early_multiplier": {
                                                      "type": "number"
                                                  },
                                              },
                                          },
                                      }
                                  },
                              }
                          }
                      },
                  },
                  "responses": {
                      "200": {
                          "description": (
                              "Ranked standings and dynamic Chaser Alert"
                          ),
                          "content": {
                              "application/json": {
                                  "schema": {
                                      "type": "object",
                                      "properties": {
                                          "leader": {"type": "string"},
                                          "standings": {"type": "array"},
                                          "chaser_alert": {"type": "string"},
                                      },
                                  }
                              }
                          },
                      }
                  },
              }
          }
      },
  }


def export_all_skill_manifests():
  """Exports all 3 OpenAPI JSON specs into orchestrate_specs/ directory."""
  os.makedirs(SKILLS_DIR, exist_ok=True)
  specs = {
      "coordinator_skill.json": get_coordinator_skill_spec(),
      "synthesizer_skill.json": get_synthesizer_skill_spec(),
      "optimizer_skill.json": get_optimizer_skill_spec(),
  }
  for filename, spec in specs.items():
    filepath = os.path.join(SKILLS_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
      json.dump(spec, f, indent=2)
  return list(specs.keys())


if __name__ == "__main__":
  created = export_all_skill_manifests()
  print(f"Exported {len(created)} OpenAPI 3.0 skill manifests to {SKILLS_DIR}/")