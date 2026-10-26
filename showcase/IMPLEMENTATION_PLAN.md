# VoiceBill — PM Showcase Implementation Plan

**Objective:** Package this project as a product-manager portfolio piece: clear narrative, interactive mockup, explainer deck with screenshots, and a recordable end-to-end demo video — not a production Alexa launch.

**Product name (showcase):** VoiceBill  
**Positioning line:** *Missed bills → ambient voice reminders + OTP-secured pay → fewer late payments.*

---

## 1. Showcase structure (what you will present)

| Beat | Time | Artifact |
|------|------|----------|
| 1. Problem | 30s | Deck slides 1–3 |
| 2. Insight & solution | 45s | Deck slides 4–6 |
| 3. MVP & tradeoffs | 45s | Deck slides 7–9 |
| 4. Live product demo | 3–4 min | Mockup + walkthrough video |
| 5. Metrics, risks, roadmap | 45s | Deck slides 10–13 |
| 6. Q&A | open | Decision log in this plan |

**Total interview story:** ~6–8 minutes + Q&A.

---

## 2. Deliverables (this folder)

| Deliverable | Path | Status |
|-------------|------|--------|
| This implementation plan | `showcase/IMPLEMENTATION_PLAN.md` | Done |
| Interactive HTML mockup (self-contained, black UI) | `showcase/mockup/voicebill-mockup.html` | Done |
| Explainer deck (self-contained, black UI) | `showcase/deck/voicebill-deck.html` | Done |
| Screenshots (dark theme) | `showcase/assets/screenshots/` | Done |
| E2E video walkthrough (self-contained, black UI) | `showcase/demo/voicebill-video.html` | Done |
| Video script + shot list | `showcase/video/VIDEO_SCRIPT.md` | Done |
| Rendered MP4 | `showcase/video/voicebill-e2e-demo.mp4` | Done (regenerate via `video/make-video.sh`) |

Open locally:

```bash
open showcase/mockup/voicebill-mockup.html
open showcase/deck/voicebill-deck.html
open showcase/demo/voicebill-video.html
open showcase/video/voicebill-e2e-demo.mp4
```

**Visual system:** pure black background (`#000`), white body text, mint accent `#5cffb0`, amber `#ffe566` for emphasis — high contrast for screen recording and decks.

---

## 3. Phased plan

### Phase A — Narrative lock (½ day)

**Goal:** One honest story; no overclaiming.

- [x] Define MVP: reminder list → pay initiate → OTP → paid (mock gateway)
- [x] Explicit cuts: Alexa skill, OAuth, proactive events, real payment rails, web app
- [ ] Rewrite root `IMPLEMENTATION_SUMMARY.md` status section to match reality (optional follow-up)
- [x] Decision log (below)

**Exit criteria:** You can say the positioning line and three cuts without notes.

### Phase B — HTML mockup (1 day) ✅ in repo

**Goal:** Visual product people can click through without AWS.

Screens in mockup:

1. **Landing** — brand-led hero (VoiceBill)
2. **Home / due bills** — companion console mirroring Alexa state
3. **Voice session** — transcript + speaker for Flow 1 & 2
4. **OTP challenge** — MFA step
5. **Payment confirmed** — success + receipt

**Exit criteria:** Full Flow 1 + Flow 2 clickable without backend.

### Phase C — Explainer deck + screenshots (1 day)

**Goal:** In-depth deck that embeds *actual* mockup screenshots (and optional API stills).

Slide outline:

1. Title / role framing  
2. Problem  
3. Who / JTBD  
4. Insight  
5. Solution overview (2 flows)  
6. User journey (Flow 1) + screenshot  
7. User journey (Flow 2) + screenshot  
8. Security model (OTP MFA) + screenshot  
9. Architecture (honest: Flask + AWS; Alexa = roadmap)  
10. MVP vs later  
11. Success metrics & funnel  
12. Risks & dependencies  
13. Roadmap Now / Next / Later  
14. Demo CTA  

**Screenshot capture (run once after mockup exists):**

```bash
# Open mockup, walk states, save PNGs into showcase/assets/screenshots/
# Recommended filenames (deck expects these):
#   01-landing.png
#   02-due-bills.png
#   03-voice-reminders.png
#   04-pay-initiate.png
#   05-otp.png
#   06-confirmed.png
#   07-architecture.png  (deck diagram slide is fine if no PNG)
```

Optional API stills (if AWS configured): curl reminders/initiate/verify → terminal screenshots as `api-*.png`.

**Exit criteria:** Deck opens offline; every journey slide has a real image.

### Phase D — End-to-end video (½–1 day)

**Goal:** 90–150 second silent-friendly video with captions (portfolio + LinkedIn).

1. Open `showcase/demo/walkthrough.html` → Play  
2. Screen-record (QuickTime / OBS) at 1920×1080  
3. Follow `showcase/video/VIDEO_SCRIPT.md` voiceover  
4. Export `showcase/video/voicebill-e2e-demo.mp4`  
5. Drop thumbnail + link on deck final slide  

**Exit criteria:** Video shows landing → due bills → voice pay → OTP → confirmed in one take.

### Phase E — Interview kit (½ day)

- [ ] 60-second elevator version of the story  
- [ ] Printed/PDF export of deck (File → Print → PDF from browser)  
- [ ] GitHub README blurb pointing to `showcase/`  
- [ ] Practice Q&A from decision log  

---

## 4. Decision log (PM tradeoffs to defend)

| Decision | Choice | Why |
|----------|--------|-----|
| Primary interface | Alexa / voice (mockup simulates) | Ambient reminders beat another app notification |
| Showcase UI | HTML mockup, not production Alexa | Finishable, screenshotable, no skill cert risk |
| Payments | Mock gateway | Proves UX + MFA; rails are commodity later |
| Auth in demo | Assumed linked account | OAuth is Phase Next; don’t block story |
| Scope cut | No proactive Alexa events in MVP | On-demand “what’s due?” still proves value |
| Backend | Keep existing Flask services | Shows build partnered with eng reality |

---

## 5. Success metrics (for the *product*, as you’d ship)

| Metric | Target | How you’d measure |
|--------|--------|-------------------|
| Missed payments | −40% vs control | Paid-by-due-date rate |
| Reminder → pay start | ≥25% | Event funnel |
| OTP success rate | ≥90% | verify success / initiate |
| Time to pay (voice) | &lt; 2 min | Session duration |
| CSAT (skill) | ≥4.5/5 | In-skill survey / app store |

Funnel for deck: **Reminder heard → Intent to pay → OTP sent → OTP ok → Paid**.

---

## 6. Roadmap (say this out loud)

| Horizon | Items |
|---------|--------|
| **Now (showcase)** | Mockup, deck, video, Flask API demo path |
| **Next** | Alexa skill + account linking + Lex session fix (`pending_bill_id`) |
| **Later** | Proactive reminders, preferences, real payment gateway, history intents |

---

## 7. Effort & calendar (suggested)

| Day | Focus |
|-----|--------|
| Day 1 | Phase A + B polish (mockup copy, motion) |
| Day 2 | Phase C screenshots + deck QA |
| Day 3 | Phase D record/edit video + Phase E practice |

**Total:** ~2–3 focused days for a interview-ready kit.

---

## 8. What *not* to build for this objective

- Full ASK skill / OAuth server  
- Real card rails  
- Separate React SPA “product”  
- IaC / load tests / rate limiting  

Those belong in roadmap slides, not this sprint.

---

## 9. How to use in an interview

1. Open deck → tell problem → insight → MVP cuts  
2. Switch to mockup *or* play the MP4  
3. Return to metrics + roadmap  
4. If technical interviewer: show `src/app.py` endpoints and admit Alexa is Next  

**One-liner:**  
*“I scoped VoiceBill as a voice-first bill pay product, cut ruthlessly for an MVP, and shipped a demoable reminder-to-OTP-pay experience with a clear path to Alexa.”*
