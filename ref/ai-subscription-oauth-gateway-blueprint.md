ได้จร้า รอบนี้ผมอัปเดตจากข้อมูลที่ค้นสด ณ **17 ส.ค. 2026** แล้ว และมีจุดหนึ่งที่ต้องแก้จากคำตอบก่อนหน้า: **OpenClaw ตอนนี้ไม่ได้สร้าง Gemini CLI OAuth profile เอง** — Google path หลักคือ API key/Vertex AI; OAuth ที่มีอยู่จาก Gemini CLI อาจถูกใช้ได้ในบาง runtime แต่ไม่ใช่ setup/recovery path ของ OpenClaw เอง ([OpenClaw][1])

ส่วน **Hermes** ตอนนี้น่าสนใจขึ้นมาก เพราะ **Nous Portal OAuth เดียวสามารถครอบคลุม 300+ agentic models** รวม Claude, GPT, Gemini, DeepSeek, Qwen, Kimi, GLM, MiniMax, Grok ฯลฯ ตามเอกสารปัจจุบันของ Hermes ([GitHub][2])

ผมจัดเป็นเอกสารส่งทีมให้เลย:

# AI Subscription OAuth Gateway

## Claw / Hermes / Coding Agent Integration Blueprint

**Status:** Updated 17 Aug 2026
**Purpose:** สร้างชั้นกลางสำหรับเชื่อม AI Agent / Coding Agent หลายตระกูลเข้ากับบัญชี AI Subscription และ API Provider โดยไม่ผูกระบบกับ agent ตัวใดตัวหนึ่ง

---

# 1. Executive Summary

เป้าหมายของงานนี้คือสร้าง **AI Agent Gateway / Subscription Auth Layer** ที่สามารถรองรับ agent runtime หลายประเภท เช่น

* OpenClaw
* Hermes Agent
* OpenAI Codex CLI
* Claude Code
* Gemini CLI
* Qwen Code
* GitHub Copilot CLI
* vendor-native coding agents อื่น ๆ

โดยแยก 3 เรื่องออกจากกันอย่างชัดเจน:

```text
User Identity
     │
     ▼
Subscription / OAuth Credential
     │
     ▼
Provider Adapter
     │
     ▼
Agent Runtime
     │
     ▼
Model / Tool
```

แนวคิดหลักคือ **อย่าทำให้ OAuth เป็นส่วนหนึ่งของ Agent**

แต่ให้ Agent ใช้ credential ผ่านมาตรฐานกลางที่ gateway จัดการ

---

# 2. Current OAuth / Subscription Landscape

## Tier A — Native subscription OAuth

### OpenAI / ChatGPT

OpenAI มีเส้นทาง **ChatGPT/Codex subscription authentication** สำหรับ Codex CLI

OpenClaw ปัจจุบันใช้ provider ID `openai` รองรับทั้ง API-key authentication และ ChatGPT/Codex subscription authentication ([OpenClaw][3])

ดังนั้น architecture ควรถือว่า:

```text
ChatGPT Subscription
        │
        ▼
   Codex OAuth
        │
        ▼
OpenAI/Codex Runtime
```

เป็น credential class แยกจาก:

```text
OPENAI_API_KEY
```

---

## Tier B — Anthropic / Claude

Claude Code รองรับการ login ด้วย Claude.ai account สำหรับ individual users และยังรองรับ Teams / Enterprise / Console / Bedrock / Vertex / Foundry ตาม environment ([Claude][4])

ดังนั้นระบบต้องแยก:

```text
Claude.ai subscription
Claude Code authentication
Anthropic API key
Cloud-provider authentication
```

ออกจากกัน

**ห้ามสมมติว่า Claude OAuth token = Anthropic API key**

---

## Tier C — Google / Gemini

จุดสำคัญจาก OpenClaw เวอร์ชันปัจจุบัน:

```text
OpenClaw
 ├── Google AI Studio API key
 ├── Vertex AI
 └── Gemini CLI runtime
       └── existing Gemini CLI OAuth profile
```

OpenClaw **ไม่ได้สร้าง Gemini CLI OAuth หรือ Antigravity OAuth profile เอง** แต่ credential ที่มีอยู่แล้วจาก Gemini CLI อาจใช้งานกับ runtime ที่รองรับได้ ([OpenClaw][1])

ดังนั้น gateway ห้ามออกแบบโดยสมมติว่า:

```text
Google OAuth = OpenClaw OAuth
```

ต้องมี adapter แยกตาม runtime

---

# 3. Hermes เป็นกรณีพิเศษ

Hermes มี architecture ที่น่าสนใจมากกว่าแค่ multi-provider

เอกสารปัจจุบันของ Hermes ระบุว่า:

```text
Nous Portal OAuth
        │
        ▼
300+ agentic models
        │
 ┌──────┼───────────────┐
 ▼      ▼       ▼       ▼
Claude  GPT    Gemini   Qwen
DeepSeek Kimi  GLM     MiniMax
Grok    ...
```

และยังรวม Tool Gateway เช่น web search, image generation, TTS และ browser automation ด้วย ([GitHub][2])

ดังนั้น Nous Portal ควรถือเป็น:

> **Subscription Aggregator / Provider Gateway**

ไม่ใช่เพียง model provider ตัวหนึ่ง

---

# 4. Provider Matrix

| Provider           |    Subscription OAuth | API Key | Agent / Runtime                  |
| ------------------ | --------------------: | ------: | -------------------------------- |
| OpenAI / ChatGPT   |               ✅ Codex |       ✅ | Codex, OpenClaw, Hermes          |
| Anthropic / Claude | ✅ Claude account flow |       ✅ | Claude Code, Hermes, OpenClaw    |
| Google Gemini      |  ⚠️ runtime-dependent |       ✅ | Gemini CLI, Hermes, OpenClaw     |
| GitHub Copilot     |                     ✅ |       — | Copilot CLI / integrations       |
| Qwen               |   ✅ OAuth/Coding Plan |       ✅ | Qwen Code / Hermes / OpenClaw    |
| xAI / Grok         |          ✅ OAuth path |       ✅ | Hermes / OpenClaw                |
| MiniMax            |                     ✅ |       ✅ | Hermes / OpenClaw                |
| Nous Portal        |               ✅ OAuth |       — | Hermes                           |
| DeepSeek           |                     — |       ✅ | Hermes / OpenClaw                |
| Kimi               |    provider-dependent |       ✅ | Hermes / OpenClaw                |
| GLM / Z.AI         |    provider-dependent |       ✅ | Hermes / OpenClaw                |
| OpenRouter         |                     — |       ✅ | OpenClaw / Hermes / other agents |

**หมายเหตุ:** เครื่องหมาย OAuth หมายถึง authentication/subscription flow ที่ runtime/provider รองรับ ไม่ได้หมายความว่า token สามารถนำไปใช้กับ runtime อื่นได้โดยตรง

---

# 5. Architecture ที่ควรสร้าง

## 5.1 Credential Plane

สร้าง abstraction:

```text
Credential
├── oauth
├── api_key
├── device_code
├── service_account
└── external_cli_credential
```

แต่ละ credential มี:

```text
provider
auth_type
account
scopes
access_token
refresh_token
expires_at
source_runtime
capabilities
```

---

# 6. OAuth Adapter

ไม่ควรเขียน OAuth รวมเป็นก้อนเดียว

สร้าง adapter:

```text
providers/
├── openai-codex/
├── anthropic/
├── google-gemini-cli/
├── github-copilot/
├── qwen/
├── xai/
├── minimax/
└── nous-portal/
```

แต่ละ adapter implement interface เดียวกัน:

```text
authenticate()
refresh()
logout()
validate()
list_models()
get_capabilities()
export_credential()
```

---

# 7. Runtime Adapter

แยกจาก provider

```text
runtimes/
├── openclaw/
├── hermes/
├── codex/
├── claude-code/
├── gemini-cli/
├── qwen-code/
└── copilot-cli/
```

ตัวอย่าง:

```text
OpenAI Codex OAuth
        │
        ├── Codex CLI
        ├── OpenClaw
        └── Hermes

Claude credential
        │
        ├── Claude Code
        ├── Hermes
        └── OpenClaw
```

แต่ **ไม่ assume compatibility**

Runtime adapter ต้องประกาศ:

```text
supports(provider)
supports(auth_type)
supports(subscription)
supports(model)
```

---

# 8. Capability Registry

นี่คือส่วนสำคัญที่ควรทำตั้งแต่แรก

ตัวอย่าง:

```yaml
provider: openai
auth:
  - oauth
  - api_key

runtime:
  - codex
  - openclaw
  - hermes

capabilities:
  coding: true
  tools: true
  streaming: true
  subscription: true
```

อีกตัว:

```yaml
provider: google
auth:
  - api_key
  - existing_gemini_cli_oauth

runtime:
  - gemini-cli
  - hermes
  - openclaw

capabilities:
  coding: true
  tools: true
```

ทำให้ gateway ไม่ต้อง hard-code logic กระจายเต็มระบบ

---

# 9. Subscription Account Registry

ระบบควรเก็บบัญชีแบบ:

```text
accounts
├── openai
│   ├── account-A
│   └── account-B
├── anthropic
├── google
├── github
├── qwen
├── xai
└── nous
```

แต่ credential จริงควรเก็บใน secure storage

```text
Gateway DB
    │
    ├── metadata
    │
    └── credential reference
              │
              ▼
       Secret Store
```

ห้ามเก็บ refresh token แบบ plaintext ใน database

---

# 10. Agent Selection

Gateway ควรเลือก agent จาก capability ไม่ใช่ชื่อ model อย่างเดียว

ตัวอย่าง:

```text
Task:
"แก้ bug ใน GitHub repository"

Required:
- coding
- git
- shell
- repository access

Candidates:

Codex
Claude Code
Hermes
OpenClaw
Qwen Code
Copilot CLI
```

จากนั้นเลือกตาม:

```text
subscription
availability
capability
cost
quota
latency
context
tool support
```

---

# 11. Routing Layer

สร้าง policy:

```text
Task
 │
 ▼
Task Classifier
 │
 ├── coding
 ├── research
 ├── browser
 ├── planning
 └── automation
 │
 ▼
Capability Router
 │
 ▼
Available Subscription
 │
 ▼
Agent Runtime
 │
 ▼
Model
```

ตัวอย่าง:

```text
Coding task
    ↓
Codex / Claude Code / Qwen Code

Browser automation
    ↓
Hermes / OpenClaw

Long research
    ↓
Hermes + Nous Portal

GitHub workflow
    ↓
Copilot / Codex / Claude Code
```

---

# 12. Local Gateway API

ให้ agent อื่นเรียก gateway ผ่าน API เดียว:

```http
GET /v1/providers
GET /v1/accounts
GET /v1/models
GET /v1/capabilities

POST /v1/auth/{provider}/login
POST /v1/auth/{provider}/refresh
POST /v1/auth/{provider}/logout

POST /v1/runs
GET  /v1/runs/{id}
```

และสำหรับ compatibility:

```text
OpenAI-compatible endpoint

/v1/chat/completions
/v1/responses
/v1/models
```

แต่ต้องระวังว่า **OpenAI-compatible API ไม่ได้แปลว่า subscription OAuth ทุกชนิดสามารถถูกนำมา proxy ได้อย่างถูกต้องตาม provider policy**

จึงต้องมี policy enforcement

---

# 13. Security Model

Credential layer ต้องเป็น security boundary

```text
Agent
  │
  │ request capability
  ▼
Gateway
  │
  ├── Auth
  ├── Policy
  ├── Credential
  ├── Quota
  └── Audit
  │
  ▼
Provider
```

ต้องมี:

* encrypted credentials
* refresh-token isolation
* token expiry handling
* scope validation
* account isolation
* audit log
* rate limit
* quota tracking
* revoke
* emergency credential disable

---

# 14. สิ่งที่ "ห้าม" ทำ

## ห้าม 1

เอา OAuth token ของ provider หนึ่งไปส่งให้ provider อื่น

```text
Claude OAuth
   ↓
OpenAI API
```

ไม่ทำ

## ห้าม 2

สมมติว่า OAuth ทุกตัวเป็นมาตรฐานเดียวกัน

```text
OAuth = OAuth = OAuth
```

ไม่จริง

แต่ละ vendor มี entitlement, scope, audience, token exchange และ runtime policy ของตัวเอง

## ห้าม 3

ทำ gateway เป็น universal token proxy ตั้งแต่ MVP

ควรเริ่มจาก:

```text
credential broker
+
runtime launcher
+
capability registry
```

ก่อน

---

# 15. MVP

## Phase 1 — Inventory

สร้าง registry ของ:

```text
OpenAI Codex
Claude Code
Gemini CLI
Qwen Code
Hermes
OpenClaw
GitHub Copilot
Nous Portal
```

ทำ compatibility matrix

---

## Phase 2 — Credential Broker

Implement:

```text
OAuth Credential Store
Provider Adapter
Token Refresh
Credential Validation
Account Registry
```

เริ่ม 3 provider:

```text
OpenAI Codex
Anthropic / Claude
Nous Portal
```

---

## Phase 3 — Runtime Adapter

เริ่ม:

```text
Codex
Claude Code
Hermes
OpenClaw
```

สามารถตรวจสอบ:

```text
which runtime
which account
which provider
which model
which capabilities
```

---

## Phase 4 — Capability Router

สร้าง:

```text
Task → Capability → Runtime → Provider → Model
```

พร้อม fallback:

```text
Claude Code
   ↓ unavailable
Codex
   ↓ unavailable
Qwen Code
```

---

## Phase 5 — GitHub Workflow

เชื่อมกับ workflow ที่เรากำลังใช้อยู่:

```text
Human
  ↓
GitHub Issue
  ↓
Gateway
  ↓
Agent
  ↓
Code
  ↓
Tests
  ↓
PR
  ↓
Human review
  ↓
Merge
```

นี่จะเป็นจุดที่ระบบเริ่มมีประโยชน์จริงกับ DevFactory / AI Web Harness

---

# 16. Target Architecture

สุดท้ายต้องการให้เป็น:

```text
                       ┌──────────────────┐
                       │      HUMAN       │
                       └────────┬─────────┘
                                │
                         GitHub Issue
                                │
                                ▼
                    ┌──────────────────────┐
                    │   AI AGENT GATEWAY   │
                    │                      │
                    │ Auth / Policy        │
                    │ Capability Registry  │
                    │ Router               │
                    │ Audit / Quota        │
                    └──────────┬───────────┘
                               │
             ┌─────────────────┼──────────────────┐
             │                 │                  │
             ▼                 ▼                  ▼
        ┌─────────┐       ┌─────────┐       ┌─────────┐
        │  Codex  │       │ Claude  │       │ Hermes  │
        │   CLI   │       │  Code   │       │         │
        └────┬────┘       └────┬────┘       └────┬────┘
             │                 │                  │
             └─────────────────┼──────────────────┘
                               │
                    ┌──────────┴──────────┐
                    │ Provider Adapters   │
                    └──────────┬──────────┘
                               │
       ┌────────────┬──────────┼──────────┬────────────┐
       ▼            ▼          ▼          ▼            ▼
    OpenAI       Anthropic   Google     Qwen        Nous
    Codex        Claude      Gemini     OAuth       Portal
```

---

# 17. Relationship กับ AI Web Harness

ระบบนี้ไม่ควรแทนที่ `ai-web-harness`

ให้แบ่งหน้าที่:

```text
ai-web-harness
       │
       │ orchestration / workflow
       ▼
AI Agent Gateway
       │
       │ authentication / routing
       ▼
Agent Runtime
       │
       ├── Codex
       ├── Claude Code
       ├── Hermes
       ├── OpenClaw
       ├── Gemini CLI
       └── Qwen Code
```

ดังนั้น:

**Harness = ทำงานอย่างไร**

**Gateway = ใช้ agent/account ไหน**

**Runtime = ใครเป็นคนทำงาน**

**Provider = model/service ไหนอยู่ข้างหลัง**

---

# 18. Recommended Repository Structure

```text
ai-agent-gateway/
├── docs/
│   ├── architecture.md
│   ├── oauth.md
│   ├── provider-matrix.md
│   └── runtime-matrix.md
│
├── packages/
│   ├── core/
│   ├── credential-broker/
│   ├── capability-registry/
│   ├── router/
│   └── audit/
│
├── providers/
│   ├── openai-codex/
│   ├── anthropic/
│   ├── google/
│   ├── qwen/
│   ├── xai/
│   ├── minimax/
│   └── nous/
│
├── runtimes/
│   ├── codex/
│   ├── claude-code/
│   ├── gemini-cli/
│   ├── qwen-code/
│   ├── hermes/
│   └── openclaw/
│
├── adapters/
├── gateway/
├── tests/
├── docker-compose.yml
└── README.md
```

---

# 19. First Milestones

### M1 — Provider & Runtime Inventory

Deliver:

* provider matrix
* OAuth matrix
* capability matrix
* compatibility matrix

### M2 — Credential Broker

Deliver:

* account registry
* encrypted credential store
* OAuth lifecycle
* token refresh
* revoke

### M3 — First Runtime Adapters

Deliver:

* Codex
* Claude Code
* Hermes
* OpenClaw

### M4 — Router

Deliver:

```text
task → capability → runtime → provider
```

### M5 — GitHub Agent Loop

Deliver:

```text
Issue
→ Agent
→ branch
→ implementation
→ test
→ PR
→ review
```

### M6 — Docker Compose PoC

ต้องสามารถ:

```bash
docker compose up
```

แล้วเปิด gateway ได้ทันที พร้อม mock/test providers

---

# 20. Success Criteria

PoC ถือว่าสำเร็จเมื่อสามารถทำ workflow นี้ได้:

```text
GitHub Issue
     ↓
AI Agent Gateway
     ↓
เลือก subscription ที่มีอยู่
     ↓
เลือก Agent Runtime
     ↓
Agent ทำงาน
     ↓
แก้ code
     ↓
run test
     ↓
สร้าง PR
     ↓
Human review
```

โดย **ไม่ต้องให้ application รู้รายละเอียด OAuth ของแต่ละ vendor**

---

# 21. Strategic Direction

อย่าออกแบบระบบนี้เป็น:

> "API Gateway สำหรับ LLM"

แต่ให้ออกแบบเป็น:

> **Subscription-aware Agent Gateway**

เพราะความแตกต่างสำคัญของยุค 2026 คือผู้ใช้ไม่ได้มีเพียง API keys แต่มี:

```text
ChatGPT Subscription
Claude Subscription
Google Subscription
GitHub Copilot
Qwen Coding Plan
Grok / xAI
Nous Subscription
...
```

และแต่ละ subscription สามารถให้ความสามารถกับ **agent runtime** ต่างกัน

ดังนั้น abstraction ที่เราต้องการคือ:

```text
                SUBSCRIPTION
                     │
                     ▼
                CREDENTIAL
                     │
                     ▼
                 PROVIDER
                     │
                     ▼
                CAPABILITY
                     │
                     ▼
                  RUNTIME
                     │
                     ▼
                   AGENT
                     │
                     ▼
                   TASK
```

นี่คือ layer ที่ควรสร้างให้เป็น foundation ของ **Multi-Agent Gateway + AI Web Harness + DevFactory** ต่อไป

[1]: https://docs.openclaw.ai/concepts/model-providers?utm_source=chatgpt.com "Model providers"
[2]: https://github.com/NousResearch/hermes-agent/blob/main/website/docs/integrations/providers.md?utm_source=chatgpt.com "hermes-agent/website/docs/integrations/providers.md ..."
[3]: https://docs.openclaw.ai/providers/openai?utm_source=chatgpt.com "OpenAI - OpenClaw"
[4]: https://code.claude.com/docs/en/authentication?utm_source=chatgpt.com "Authentication - Claude Code Docs"
