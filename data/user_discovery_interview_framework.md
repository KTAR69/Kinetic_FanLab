# Kinetic FanLab — User Discovery Interview Framework & Feature Value Matrix
## 1. Purpose of User Discovery Interviews
Following enterprise product discovery standards, every feature in Kinetic FanLab must justify its **Cloud Compute & Battery Cost** against **Verified Fan Demand**.

## 2. Core Discovery Interview Questions (Non-Leading)
1. **In-Seat Behavior:** *"Walk me through the last tense 4th-quarter moment you attended live—what were you doing with your phone, your voice, and the fans around you?"*
2. **Acoustic Validation vs. Privacy:** *"If your section's decibel roar helped force a missed kick or free throw, how would you want that measured—and what would make you uncomfortable about microphone permissions?"*
3. **Feature Trade-Off (The $100 Budget Test):** *"If you had 100 points to spend across (a) Section Decibel Roar Leaderboard, (b) Distraction Tapper, (c) Shareable Post-Play Proof Card, and (d) Seat Neighbor Respect Taps, how would you allocate them?"*
4. **Reward Motivation:** *"Which reward would actually get you in your seat 30 minutes early: a 1.25x leaderboard multiplier, a digital NFT badge, or a 20% concession/merch voucher?"*

## 3. Feature Value-to-Cost Decision Rules
- **KEEP_CORE_EDGE:** High fan demand (`>= 8.0/10`) + near-zero cloud cost (`<= $0.001/seat`).
- **KEEP_EVENT_GATED:** High fan demand (`>= 8.0/10`) + moderate LLM cost (`<= $0.015/seat`) gated strictly to clutch moments.
- **DEPRECATED_BY_DESIGN:** Low fan demand (`< 5.0/10`) or high cloud cost (`> $0.05/seat`)—such as raw cloud audio streaming, which is replaced by local 4-byte SPL floats.
