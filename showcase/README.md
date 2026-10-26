# VoiceBill Showcase Kit

Self-contained PM portfolio artifacts. **Black backgrounds · white / mint / amber type for high contrast.**

Product name in the kit: **VoiceBill**  
Positioning: *Missed bills → ambient voice reminders + OTP-secured pay → fewer late payments.*

---

## Open these

| Artifact | File | Notes |
|----------|------|--------|
| **Frontend mockup** | [mockup/voicebill-mockup.html](mockup/voicebill-mockup.html) | Self-contained · click through Flow 1 & 2 |
| **Explainer deck** | [deck/voicebill-deck.html](deck/voicebill-deck.html) | 14 slides · ← → · `F` fullscreen |
| **Video walkthrough** | [demo/voicebill-video.html](demo/voicebill-video.html) | Autoplay captions · record this |
| **Silent slideshow MP4** | [video/voicebill-e2e-demo.mp4](video/voicebill-e2e-demo.mp4) | From screenshots · regenerate below |
| **Implementation plan** | [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) | Phases, MVP cuts, decision log |
| **Voiceover script** | [video/VIDEO_SCRIPT.md](video/VIDEO_SCRIPT.md) | Shot list + VO lines |

```bash
open showcase/mockup/voicebill-mockup.html
open showcase/deck/voicebill-deck.html
open showcase/demo/voicebill-video.html
open showcase/video/voicebill-e2e-demo.mp4
```

---

## Voiced portfolio clip (recommended)

Aim for a **90–130 second** screen recording with your voiceover. This is what you put on LinkedIn / portfolio / interview warm-up.

### What you’ll produce

1. Screen recording of `demo/voicebill-video.html` (black UI + captions)  
2. Your voice reading the script below (or from [VIDEO_SCRIPT.md](video/VIDEO_SCRIPT.md))  
3. Optional: soft music under −20 dB  
4. Export: `video/voicebill-e2e-demo-voiced.mp4` (keep the silent reel too if you want)

### Setup (macOS)

1. Close unrelated windows; use a clean browser profile if possible.  
2. Open Chrome → `showcase/demo/voicebill-video.html` → fullscreen (`⌃⌘F` or green button). Hide bookmarks bar.  
3. Open **QuickTime Player** → **File → New Screen Recording** (or OBS at 1920×1080).  
4. Select **the browser window only** (not the whole desktop).  
5. Enable microphone for voiceover (record VO live, or dub later in iMovie/Descript).  
6. Start recording → click **Play demo** in the page → speak with the captions.  
7. Stop when the UI says **Complete — stop recording** (~2:10).  

### Voiceover (say this)

| Time | On screen | Say |
|------|-----------|-----|
| 0:00–0:08 | Landing | “VoiceBill helps people pay bills through voice — reminders first, then a secure pay path.” |
| 0:08–0:22 | Due bills | “Here’s the companion view. Maya has three unpaid bills. Electricity is due in five days.” |
| 0:22–0:45 | Flow 1 | “She asks Alexa what’s due. VoiceBill reads back the urgent bills and offers to pay.” |
| 0:45–1:10 | Pay initiate | “When she chooses to pay electricity, we don’t move money yet — we send a one-time code to her phone.” |
| 1:10–1:35 | OTP → Paid | “She speaks the code. Only then we process payment — mocked in this demo — and confirm out loud.” |
| 1:35–2:00 | Aftermath | “Remaining bills update. The metric I’d watch is paid-by-due-date rate. Alexa skill and real rails are next — this MVP proves the experience.” |

**End line (optional):** “VoiceBill — PM case study. Mockup plus Flask API; Alexa on the roadmap.”

### Honest framing (say this if asked)

- Payments are **mocked** (by design for the MVP).  
- The Alexa skill is **roadmap / Next**, not a published skill.  
- Backend Flask API for reminders + OTP exists under `src/`.

### Edit & publish checklist

- [ ] No dead air &gt; 2s without VO or caption change  
- [ ] OTP and confirmation each visible ≥ 3s  
- [ ] Captions match VO (YouTube auto-captions or burned-in)  
- [ ] Thumbnail: crop `assets/screenshots/01-landing.png` → “VoiceBill — voice bill pay MVP”  
- [ ] Do **not** claim a live Alexa Store skill  
- [ ] Link the clip from your portfolio and the deck’s final slide  

### Regenerate silent slideshow MP4

```bash
cd showcase
./video/make-video.sh
```

Requires `ffmpeg` and Python + Pillow.

---

## Interview flow (6–8 min)

1. **Deck** — problem → insight → MVP cuts → metrics → roadmap  
2. **Clip or live mockup** — reminder → OTP → paid  
3. **Optional eng deep-dive** — `src/app.py` endpoints; Alexa = Next  

One-liner:  
*“I scoped VoiceBill as voice-first bill pay, cut ruthlessly for an MVP, and shipped a demoable reminder-to-OTP-pay experience with a clear path to Alexa.”*
