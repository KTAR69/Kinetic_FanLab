# Kinetic FanLab — Streamlit Cloud Deployment Guide
**Week 7 Live Tester URL — Track 3: Fan-Centric Sports & Entertainment**

---

## 1. Pre-Deployment Checklist

- [ ] `python -m py_compile app.py` → 0 errors
- [ ] `python tests/test_week7_onboarding_npc.py` → 12 / 12 PASS
- [ ] `python tests/test_16_agent_production.py` → 44 / 44 PASS
- [ ] `git tag v1.0-week6-complete` exists (rollback point)
- [ ] `data/registered_fans.json` is gitignored (confirmed — never commit fan PII)
- [ ] `.env` is gitignored (confirmed)

---

## 2. Streamlit Cloud Setup

### 2a. Connect the Repository
1. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
2. Repository: `your-github-username/kinetic_fanlab`
3. Branch: `main`
4. Main file path: `app.py`
5. Python version: `3.12`

### 2b. Required Secrets (Settings → Secrets)
Add **all** of the following in the Streamlit Cloud secrets editor.
Every secret is optional — the app degrades gracefully when absent — but
**Granite and Cloudant will be in fallback mode until these are set.**

```toml
# IBM watsonx.ai (Dallas — us-south)
WO_API_KEY             = "your-ibm-cloud-api-key"
WATSONX_APIKEY         = "your-ibm-cloud-api-key"   # alias used by secrets.toml.example
WATSONX_PROJECT_ID     = "7be4956c-c4e8-4775-8559-f076dda7cfea"
WATSONX_URL            = "https://us-south.ml.cloud.ibm.com"
WATSONX_MODEL_ID       = "ibm/granite-4-h-small"

# IBM Cloudant NoSQL
CLOUDANT_APIKEY        = "your-cloudant-api-key"
CLOUDANT_URL           = "https://YOUR_INSTANCE.cloudantnosqldb.appdomain.cloud"
CLOUDANT_DB_NAME       = "kinetic_fanlab_db"

# IBM Cloud Object Storage (COS)
COS_APIKEY             = "your-cos-api-key"
COS_BUCKET_NAME        = "kinetic-fanlab-curated-cmi"
COS_ENDPOINT           = "https://s3.us-south.cloud-object-storage.appdomain.cloud"

# IBM App ID (optional — enables IBMid SSO on the login screen)
APPID_TENANT_ID        = "your-app-id-tenant-id"
APPID_CLIENT_ID        = "your-app-id-client-id"
APPID_CLIENT_SECRET    = "your-app-id-client-secret"
APPID_REGION           = "us-south"
APPID_REDIRECT_URI     = "https://your-app.streamlit.app"
```

### 2c. Verify Credential Key Names
| Module | Reads this secret key | Notes |
|---|---|---|
| `watsonx_live.py` | `WO_API_KEY` or `WATSONX_APIKEY` | Either works; WO_API_KEY is the `.env` name |
| `cloudant_engine.py` | `CLOUDANT_APIKEY`, `CLOUDANT_URL` | |
| `cos_archive.py` | `COS_APIKEY`, `COS_BUCKET_NAME` or `COS_BUCKET` | |
| `ibm_appid_auth.py` | `APPID_TENANT_ID`, `APPID_CLIENT_ID`, `APPID_CLIENT_SECRET` | All optional |
| `governance_factsheet.py` | same as `watsonx_live.py` | |

---

## 3. Health Check

After deploying, append `?debug=health` to your app URL.  
The health panel displays:

| Indicator | What it confirms |
|---|---|
| `WATSONX_LIVE` | Granite API key loaded + SDK present |
| `CLOUDANT_ENGINE_LIVE` | Cloudant URL + API key reachable |
| `COS_ARCHIVE_LIVE` | COS bucket accessible |
| `GOVERNANCE_LIVE` | governance_check module loaded |
| `FACTSHEET_LIVE` | governance_factsheet module loaded |
| `APPID_ENABLED` | IBM App ID credentials present |

---

## 4. Post-Deploy Smoke Test

1. Open app URL → Screen 1 loads with **Guest Fan** state
2. Sign in as Troy (`fan@gmail.com` / your password) → Admin Portal tab visible in Screen 1
3. Navigate to Screen 3 → Pulse Tapper increments CMI → callout posts to sidebar chat
4. Navigate to Screen 4 → Granite narrative synthesizes → `st.toast` appears
5. Navigate to Screen 5 → `@coach` chip sends message → AI Squad responds
6. Admin Portal → **📊 Publish AI Factsheet** button → confirms watsonx.governance connection

---

## 5. Week 8 Live Testing — Tester Onboarding Flow

Share the Streamlit Cloud URL with testers. Each tester:
1. Opens app → Guest state (Screen 1)
2. Signs up with their name, handle, sport, email, password
3. Completes the **Rookie Walkthrough** (NPC mentor Marcus/Sarah greets them)
4. Explores all 5 screens and submits feedback on Screen 1 (scroll to bottom)
5. Troy reviews all feedback in the **Screen 1 Admin Portal → 👑 Feedback tab**

---

## 6. Rollback
```bash
git checkout v1.0-week6-complete
git push origin HEAD:main --force   # only if critically needed
```

---

## 7. IBM Cloud Services Dashboard Links

| Service | Console Link |
|---|---|
| watsonx.ai | https://us-south.ml.cloud.ibm.com |
| watsonx Orchestrate | https://eu-de.assistant.watson.cloud.ibm.com (eu-de-0ec71755) |
| IBM Cloudant | https://cloud.ibm.com/resources (filter: Databases) |
| IBM COS | https://cloud.ibm.com/resources (filter: Storage) |
| IBM App ID | https://cloud.ibm.com/catalog/services/app-id |
| watsonx.governance | https://us-south.ml.cloud.ibm.com/v2/ai_factsheets |
