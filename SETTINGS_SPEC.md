# Kinetic FanLab — Account Settings & Future-Proof Stadium Specifications

This specification outlines the architecture of the **⚙️ Account Settings & Connected Accounts** hub implemented on Screen 1, detailing connected social media integrations, hardware telemetry anchors, in-arena preferences, and proactive features for future stadium deployments.

---

## 1. Connected Social Media Channels
* **𝕏 (Twitter):** User's personal handle (e.g., `@owltar`). Automatically pre-populates one-click viral share intents for both the **Proof-of-Momentum StoryCard** (Screen 4) and the **Living Trophy Showcase** (Screen 1).
* **📸 Instagram:** Handle or profile link (e.g., `@owltar_fanlab`). Formats customized 1-tap copy captions formatted with verified hashtag metadata (`#KineticFanLab`, `#IBM`, `#Web3Sports`, `#FanPassport`).
* **▶️ YouTube:** Channel URL or handle (e.g., `@W3bHippo`). Connects the user's sports creator identity to verified in-arena crowd acoustic logs.
* **🎵 TikTok:** Short-form creator tag (e.g., `@owltar_energy`). Pre-formats video captions linking verified decibel peaks to creator video tags.
* **💬 Discord / Telegram:** Fan handle (e.g., `owltar#1234`) for row-level coordination and section strategist sync.

---

## 2. Wearable Sensor & Edge Bleed Calibration
* **Hardware Device Anchors:**
  * Apple Watch Ultra 2 (ECG/Log SPL dB)
  * Apple Watch Series 9 / SE
  * Garmin Fenix 7X (Stress / Heart Rate BPM)
  * Google Pixel Watch 2
  * Samsung Galaxy Watch 6 Pro
  * Fitbit Charge 6
  * Smartphone Microphone & Accelerometer (Edge BLE fallback)
* **BLE Mesh Beacon Proximity Calibration:**
  * Slider ranging from `-90 dBm` (far stadium perimeter) to `-25 dBm` (direct row seat contact).
  * Default `-54 dBm` calibrates exact seat proximity within the 50-seat row cluster.
* **Acoustic PA Speaker Bleed Cancellation:**
  * Real-time `-3.5 dB` logarithmic filtering to eliminate stadium loudspeaker artificial inflation.

---

## 3. Gameday Notification & Pacing Controls
* **⚡ In-Arena Clutch Vibration & Visual Haptics:** Fires synchronized device screen pulses and wearable haptic taps during 2.0x clutch defensive windows (free-throw routine & 0:03 field goal snap).
* **🎪 36-Hour Virtual Tailgate & Meetup Strategy Alerts:** Proactive notifications when defensive chant synthesis and meetup RSVP commons open 36h before game time.
* **⚠️ Section Rivalry Standings & Chaser Alerts:** Real-time push alert when the chasing section closes within single digits on per-capita points.
* **🏆 Stadium Jumbotron & Leaderboard Display:** Toggle to display or anonymize the fan's handle and tier on the stadium jumbotron and public leaderboards.

---

## 4. Privacy, Governance & EEOC Dialect Protection
* **🔒 EEOC Dialect & Regional Accent Privacy Shield (DIR = 0.953):** Enforces edge sanitization of voice callouts so regional dialects (Texas/Southern, Tejano bilingual blend, AAVE, Northeastern) score with mathematical fairness before reaching the central momentum index.
* **Biometric Data Retention Policies:**
  1. *Gameday Session Only (Default):* Raw acoustic and heart rate signals discarded immediately after CMI calculation ($0.00 cloud storage cost).
  2. *30-Day Encrypted Aggregate:* Synchronized passport aggregates stored in IBM Cloudant NoSQL with AES-256 encryption.
  3. *Seasonal COS S3 Archive:* Post-game box scores committed to IBM Cloud Object Storage with SHA-256 tamper-evident integrity receipts.

---

## 5. Community Meetup Consistency & Future NFT Accolades
* **Community Loyalty Streak:** Every verified meetup RSVP on Screen 2 (Student Plaza Rally, Campus Walk Crew, Lot B Mega-Tailgate, Stadium Express Shuttle) logs +1 event into the member's permanent profile.
* **Future Community Accolade Badges:**
  * **🏀 Basketball:** `Plaza Rally Vanguard` (Requires 3 verified meetups).
  * **🏈 Football:** `Lot B Tailgate Legend` (Requires 3 verified meetups).
  * Automatically unlocks permanent perks: VIP pre-game tailgate vouchers, priority express gate wristbands, and concession discounts.
