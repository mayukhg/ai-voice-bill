# VoiceBill — AI Voice Bill Payment

## Why this product (PM decision)

Our white-label parent product was a **bill payments platform**. The mandate was simple: **reach customers where they already are**, not force another app habit. The core pain we owned was **late and missed bill payments** — high cost for end users (fees, service cuts) and for billers (collections, support load).

Usage of **digital voice agents** (smart speakers / conversational assistants) was rising in the same households that already pay bills digitally but still forget. As PM, I chose that channel on purpose: use voice to **surface due bills as ambient reminders**, then **complete payment on the same path** with OTP MFA — extending the existing payments platform into a context where push/email reminders get ignored.

**VoiceBill** is the case study for that decision: two flows (remind → pay), mocked rails for a shippable MVP, and a clear Next step to Alexa while the experience is demoable today.

**Positioning:** *Missed bills → ambient voice reminders + OTP-secured pay → fewer late payments.*

A voice-first bill payment product concept: **reminders for bills due within 7 days**, then **OTP-secured payment** (mock gateway). Built as a **PM portfolio case study** with a Flask/AWS backend scaffold and a self-contained showcase kit (mockup, deck, video).

---

## What’s in this repo

| Layer | Status | Where |
|-------|--------|--------|
| **PM showcase** (mockup, deck, video) | Ready to present | [`showcase/`](showcase/) |
| **Flask API** (reminders, bills, OTP pay, Lex webhook) | Partial / demoable with AWS | [`src/`](src/) |
| **Alexa skill / OAuth / real payment rails** | Roadmap (Next / Later) | Docs only |

Honest note: payments are **mocked**; the Alexa skill is **not** published in this repo. Treat `IMPLEMENTATION_SUMMARY.md` as aspirational — use [`showcase/IMPLEMENTATION_PLAN.md`](showcase/IMPLEMENTATION_PLAN.md) for current status and cuts.

---

## PM showcase (start here)

Self-contained HTML on a **black background** with high-contrast type (white / mint `#5cffb0` / amber `#ffe566`).

| Artifact | Open |
|----------|------|
| Interactive mockup | [showcase/mockup/voicebill-mockup.html](showcase/mockup/voicebill-mockup.html) |
| Explainer deck (← → · `F` fullscreen) | [showcase/deck/voicebill-deck.html](showcase/deck/voicebill-deck.html) |
| Video walkthrough (for recording) | [showcase/demo/voicebill-video.html](showcase/demo/voicebill-video.html) |
| Silent slideshow MP4 | [showcase/video/voicebill-e2e-demo.mp4](showcase/video/voicebill-e2e-demo.mp4) |
| Kit guide + voiced-clip steps | [showcase/README.md](showcase/README.md) |
| Implementation plan | [showcase/IMPLEMENTATION_PLAN.md](showcase/IMPLEMENTATION_PLAN.md) |

```bash
open showcase/mockup/voicebill-mockup.html
open showcase/deck/voicebill-deck.html
open showcase/demo/voicebill-video.html
open showcase/video/voicebill-e2e-demo.mp4
```

### Two product flows (demo)

1. **Flow 1 — Reminders:** “What’s due?” → list bills in the next 7 days → offer to pay  
2. **Flow 2 — Pay + OTP:** “Pay my electricity bill” → SMS OTP → speak code → mock pay → confirmation  

---

## Voiced portfolio clip

Record a **~90–130 second** narrated demo for LinkedIn, your portfolio site, or interview warm-up.

### Quick steps

1. Open [showcase/demo/voicebill-video.html](showcase/demo/voicebill-video.html) in Chrome → **fullscreen**.  
2. **QuickTime** → File → New Screen Recording (or OBS @ 1920×1080) → capture **the browser window only**.  
3. Enable your **microphone**.  
4. Start recording → click **Play demo** → speak the voiceover in sync with on-screen captions.  
5. Stop when the page says **Complete — stop recording**.  
6. Export as `showcase/video/voicebill-e2e-demo-voiced.mp4`.

Full shot list, edit checklist, and thumbnail tips: [showcase/video/VIDEO_SCRIPT.md](showcase/video/VIDEO_SCRIPT.md) and [showcase/README.md](showcase/README.md).

### Voiceover script

| Time | Say |
|------|-----|
| 0:00–0:08 | “VoiceBill helps people pay bills through voice — reminders first, then a secure pay path.” |
| 0:08–0:22 | “Here’s the companion view. Maya has three unpaid bills. Electricity is due in five days.” |
| 0:22–0:45 | “She asks Alexa what’s due. VoiceBill reads back the urgent bills and offers to pay.” |
| 0:45–1:10 | “When she chooses to pay electricity, we don’t move money yet — we send a one-time code to her phone.” |
| 1:10–1:35 | “She speaks the code. Only then we process payment — mocked in this demo — and confirm out loud.” |
| 1:35–2:00 | “Remaining bills update. The metric I’d watch is paid-by-due-date rate. Alexa skill and real rails are next — this MVP proves the experience.” |

**Do not claim** a live Alexa Store skill. Say payments are mocked and Alexa is on the roadmap.

### Regenerate silent MP4 from screenshots

```bash
cd showcase
./video/make-video.sh   # needs ffmpeg + Python Pillow
```

---

## Backend (Flask API)

### Stack

- Python 3.9+ · Flask · boto3  
- AWS: Lex (fulfillment webhook), Polly, DynamoDB, SNS  
- Intended voice client: Amazon Alexa (not packaged in-repo yet)

### Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/health` | Liveness |
| `GET` | `/api/v1/reminders/<user_id>` | Due-bill reminders |
| `GET` | `/api/v1/reminders/<user_id>/audio/<bill_id>` | Polly MP3 for one bill |
| `GET` | `/api/v1/bills/<user_id>` | Unpaid bills |
| `POST` | `/api/v1/payments/initiate` | Start pay → send OTP |
| `POST` | `/api/v1/payments/verify` | Verify OTP → mock pay |
| `POST` | `/api/v1/lex/fulfillment` | Lex webhook |

### Run locally

```bash
pip install -r requirements.txt
cp .env.example .env   # add AWS credentials + table names
python src/app.py      # http://localhost:5000
```

```bash
curl http://localhost:5000/health
curl http://localhost:5000/api/v1/reminders/test_user_123
```

Seed sample bills (needs live DynamoDB): `python scripts/sample_data.py`

Docker:

```bash
docker build -t ai-voice-bill .
docker run -p 5000:5000 --env-file .env ai-voice-bill
```

More detail: [API_DOCUMENTATION.md](API_DOCUMENTATION.md) · [DEPLOYMENT.md](DEPLOYMENT.md) · [LEX_BOT_CONFIGURATION.md](LEX_BOT_CONFIGURATION.md)

---

## Project structure

```
ai-voice-bill-2/
├── showcase/                      # PM portfolio kit
│   ├── mockup/voicebill-mockup.html
│   ├── deck/voicebill-deck.html
│   ├── demo/voicebill-video.html
│   ├── video/voicebill-e2e-demo.mp4
│   ├── video/VIDEO_SCRIPT.md
│   ├── video/make-video.sh
│   ├── assets/screenshots/
│   ├── IMPLEMENTATION_PLAN.md
│   └── README.md
├── src/
│   ├── app.py                     # Flask routes
│   ├── config.py
│   ├── aws_services/              # Polly, Lex, DynamoDB, SNS
│   ├── services/                  # Reminder + payment (OTP)
│   └── utils/
├── scripts/sample_data.py
├── requirements.txt
├── Dockerfile
├── REQUIREMENTS.md
├── ARCHITECTURE.md
└── README.md
```

---

## Roadmap

| Horizon | Focus |
|---------|--------|
| **Now** | Showcase kit, Flask demo path, mock OTP pay |
| **Next** | Alexa skill + account linking, Lex session fix (`pending_bill_id`) |
| **Later** | Proactive reminders, preferences, real payment gateway |

Alexa publish checklist: [ALEXA_SKILL_REQUIREMENTS_SUMMARY.md](ALEXA_SKILL_REQUIREMENTS_SUMMARY.md)

---

## Interview one-liner

> I scoped VoiceBill as voice-first bill pay, cut ruthlessly for an MVP, and shipped a demoable reminder-to-OTP-pay experience with a clear path to Alexa.

---

## Documentation index

- [showcase/README.md](showcase/README.md) — kit + voiced clip  
- [showcase/IMPLEMENTATION_PLAN.md](showcase/IMPLEMENTATION_PLAN.md) — phases & decisions  
- [REQUIREMENTS.md](REQUIREMENTS.md) — product requirements  
- [ARCHITECTURE.md](ARCHITECTURE.md) — system design  
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) — API reference  
- [DEPLOYMENT.md](DEPLOYMENT.md) — deploy notes  
- [LEX_BOT_CONFIGURATION.md](LEX_BOT_CONFIGURATION.md) — Lex setup  

## License

MIT (see repository license file if present).
