ทีมครับ งานนี้ให้แยกเป็น repo ใหม่ โดยโฟกัสที่ **Distributed Multi-Agent Gateway** สำหรับเชื่อม ChatGPT กับ Coding Agents หลายชนิดที่รันอยู่บนเครื่อง/Server ต่าง ๆ แม้เครื่องเหล่านั้นจะอยู่หลัง NAT/Firewall

## เป้าหมาย

สร้างระบบ:

ChatGPT → Gateway → Message Broker → Remote Worker → Coding Agent → Git/PR

โดย ChatGPT ทำหน้าที่เป็น Control Plane ส่วน Worker เป็น Execution Plane และ Coding Agent ต่าง ๆ สามารถสลับ/เพิ่มได้ผ่าน Adapter โดยไม่ต้องแก้ Gateway

## Architecture

```text
ChatGPT Custom GPT
        │
        │ HTTPS / OpenAPI
        ▼
┌──────────────────┐
│  Agent Gateway   │
│                  │
│ Task API         │
│ Scheduler        │
│ Task State       │
│ Repo/Workspace   │
└────────┬─────────┘
         │
      MQTT/NATS
         │
   ┌─────┼─────────┐
   ▼     ▼         ▼
Worker A Worker B Worker C
   │       │         │
   ▼       ▼         ▼
OpenCode Claude    Gemini
Aider    Q/Goose   etc.
```

Worker ต้องทำงานแบบ outbound connection เพื่อรองรับเครื่องหลัง NAT/Firewall โดยไม่ต้องเปิด inbound port

## Phase 1 — Gateway Foundation

ทำให้ flow นี้ทำงานก่อน:

```text
POST /tasks
   ↓
task_id
   ↓
Broker
   ↓
Worker
   ↓
Shell command
   ↓
Result
   ↓
GET /tasks/{task_id}
```

สิ่งที่ต้องมี:

* Node.js/TypeScript หรือ FastAPI
* OpenAPI 3
* SQLite WAL
* Task state machine
* MQTT หรือ NATS
* Docker Compose
* Worker registration + heartbeat
* Structured logs
* timeout / retry / cancellation เบื้องต้น

**ต้องมี ShellAdapter เป็นตัวแรก** เพื่อพิสูจน์ architecture โดยไม่ผูกกับ Coding Agent ใด ๆ

## Phase 2 — Adapter Framework

สร้าง interface กลาง:

```text
AgentAdapter
 ├── capabilities()
 ├── health()
 ├── validate()
 ├── execute()
 ├── cancel()
 └── collectResult()
```

เริ่ม implement:

1. Shell
2. OpenCode
3. Claude Code
4. Gemini CLI

จากนั้นค่อยเพิ่ม:

* Aider
* Goose
* OpenHands
* SWE-agent
* Amazon Q
* GitHub Copilot
* DeepSeek/Qwen
* Generic MCP

อย่าพยายาม implement ทุก adapter ใน MVP พร้อมกัน

## Phase 3 — Distributed Worker / Fleet

Worker ต้องประกาศ capability เช่น:

```json
{
  "worker_id": "worker-01",
  "platform": "linux",
  "capabilities": {
    "docker": true,
    "git": true,
    "network": true
  },
  "agents": {
    "opencode": true,
    "claude-code": true,
    "gemini": true
  }
}
```

Gateway สามารถเลือก Worker ที่เหมาะสมกับ Task ได้

แนวคิดสำคัญ:

**Agent ≠ Model**

ควรแยก:

```json
{
  "target": {
    "agent": "opencode",
    "model": "..."
  }
}
```

ไม่ควร hard-code model list ไว้ใน Task schema

และรองรับอนาคต:

```json
{
  "target": {
    "agent": "auto",
    "requirements": {
      "coding": true,
      "docker": true,
      "budget": "free"
    }
  }
}
```

## Phase 4 — Repository / Workspace

อย่าผูกระบบกับ:

```text
/path/to/local/repo
```

เพียงอย่างเดียว

ควรรองรับ:

```text
GitHub repository
      ↓
clone
      ↓
worktree
      ↓
branch
      ↓
Coding Agent
      ↓
git diff
      ↓
commit (optional)
      ↓
push (optional)
```

Task ควรสามารถระบุ repository/ref/branch ได้

## Phase 5 — GitHub Development Loop

เป้าหมายระยะถัดไป:

```text
ChatGPT
   ↓
GitHub Issue
   ↓
Agent Gateway
   ↓
Worker
   ↓
Coding Agent
   ↓
Branch
   ↓
Commit
   ↓
Push
   ↓
Pull Request
   ↓
CI
   ↓
Review
   ↓
Merge
```

ทำให้ระบบสามารถเป็น execution backend ให้ workflow แบบ Dev Factory ได้

## Security / Reliability

ต้องออกแบบตั้งแต่ต้น:

* Worker authentication
* Per-worker credentials
* ไม่ส่ง API keys ผ่าน task payload
* Secret isolation
* Workspace sandbox
* Command timeout
* Process cleanup
* PTY handling สำหรับ CLI ที่ interactive
* ANSI log stripping
* Max log size
* Task idempotency
* Retry policy
* Worker heartbeat
* Graceful cancellation

## Repository Structure

เริ่มต้นประมาณนี้:

```text
agent-gateway/
├── gateway/
│   ├── src/
│   │   ├── api/
│   │   ├── broker/
│   │   ├── db/
│   │   ├── scheduler/
│   │   ├── schemas/
│   │   └── server.ts
│   ├── openapi.yaml
│   └── Dockerfile
│
├── worker/
│   ├── src/
│   │   ├── adapters/
│   │   │   ├── base.ts
│   │   │   ├── shell.ts
│   │   │   ├── opencode.ts
│   │   │   ├── claude_code.ts
│   │   │   └── gemini.ts
│   │   ├── executor/
│   │   ├── workspace/
│   │   ├── broker/
│   │   └── index.ts
│   └── Dockerfile
│
├── docker-compose.yml
├── README.md
└── docs/
```

## Definition of Done สำหรับ MVP

หลัง `docker compose up` ต้องสามารถทดสอบได้ทันที:

```text
ChatGPT/API
    ↓
Gateway
    ↓
MQTT/NATS
    ↓
Worker
    ↓
ShellAdapter
    ↓
Result
```

และสามารถ:

* สร้าง task
* ได้ `task_id`
* poll status
* ดู execution logs
* ดู result
* timeout งาน
* worker disconnect/reconnect ได้
* worker register/heartbeat ได้
* รันหลาย worker ได้
* เพิ่ม Adapter ใหม่โดยไม่แก้ core Gateway
* มี OpenAPI พร้อมใช้กับ ChatGPT Custom Actions

หลัง MVP ผ่านแล้วค่อยต่อ OpenCode / Claude Code / Gemini และ GitHub workflow

**หลักการสำคัญ:** อย่าสร้างระบบที่พยายามเป็น Coding Agent ตัวใหม่ แต่สร้าง **Gateway/Fleet Infrastructure ที่ทำให้ Coding Agents ที่มีอยู่แล้วกลายเป็น interchangeable execution workers** และต้องให้ PoC แรกสามารถรัน/test ได้เร็วด้วย Docker Compose
