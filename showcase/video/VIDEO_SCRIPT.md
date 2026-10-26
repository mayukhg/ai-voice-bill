# VoiceBill — End-to-End Demo Video Script

**Output file:** `showcase/video/voicebill-e2e-demo.mp4`  
**Length:** 90–130 seconds  
**Format:** 1920×1080, 30fps, H.264, soft background music optional (low)  
**Source UI:** `showcase/demo/voicebill-video.html` (black background, high-contrast — preferred) or `showcase/mockup/voicebill-mockup.html`  
**Pre-built reel:** `showcase/video/voicebill-e2e-demo.mp4` (regenerate with `./video/make-video.sh`)  

---

## Recording setup (macOS)

1. Open walkthrough in Chrome (full screen, hide bookmarks bar).
2. QuickTime Player → File → New Screen Recording → record the browser window only.
3. Click **Play demo** on the walkthrough; stop when caption says “stop recording.”
4. Or use OBS: Display capture, 1920×1080 canvas, same flow.

**Do not** show personal desktop clutter; use a clean profile / focus mode.

---

## Shot list & voiceover

| Time | On screen | Voiceover (say this) |
|------|-----------|----------------------|
| 0:00–0:08 | Landing · VoiceBill brand | “VoiceBill helps people pay bills through voice — reminders first, then a secure pay path.” |
| 0:08–0:22 | Due bills list | “Here’s the companion view. Maya has three unpaid bills. Electricity is due in five days.” |
| 0:22–0:45 | Voice · Flow 1 | “She asks Alexa what’s due. VoiceBill reads back the urgent bills and offers to pay.” |
| 0:45–1:10 | Voice pay → OTP | “When she chooses to pay electricity, we don’t move money yet — we send a one-time code to her phone.” |
| 1:10–1:35 | OTP → Confirmed | “She speaks the code. Only then we process payment — mocked in this demo — and confirm out loud.” |
| 1:35–2:00 | Bills aftermath + end card | “Remaining bills update. The product metric I’d watch is paid-by-due-date rate. Alexa skill and real rails are next on the roadmap — this MVP proves the experience.” |

**End card (5s):**  
`VoiceBill · PM case study`  
`mockup + Flask API · Alexa on roadmap`

---

## Captions

Burn in or add YouTube/LinkedIn captions from the voiceover column. Keep lines ≤ 42 characters where possible.

---

## Thumbnail

Use `showcase/assets/screenshots/01-landing.png` cropped to 1280×720 with title overlay: **VoiceBill — voice bill pay MVP**.

---

## Checklist before you call it done

- [ ] No dead air &gt; 2s without VO or caption change  
- [ ] OTP and confirmation both visible ≥ 3s  
- [ ] Honest: no claim of live Alexa store skill  
- [ ] File saved at `showcase/video/voicebill-e2e-demo.mp4`  
- [ ] Linked from deck final slide / portfolio README  

---

## Optional B-roll (if AWS demo works)

Terminal curls for `/reminders` and `/payments/initiate` — max 10 seconds total, labeled “Backend API.”
