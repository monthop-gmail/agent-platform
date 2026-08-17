# ref/ — บันทึกดิบ

เอกสารในโฟลเดอร์นี้เป็น **raw notes ตามเวลา** เก็บไว้ตามต้นฉบับ ไม่แก้ไข

> ⚠️ **ไม่ผูกพัน** — ไฟล์ในนี้ขัดกันเองหลายจุด (ชื่อ core repo 4 เวอร์ชัน, `agent-gateway` 3 ความหมาย, stack 4 ชุด) ข้อตกลงจริงอยู่ที่ [`../decisions/`](../decisions/) ถ้าขัดกัน → ADR ที่ Accepted ชนะ

## สารบัญ

### ตัดสินใจเรื่องชื่อและขอบเขต

| ไฟล์ | เนื้อหา |
| --- | --- |
| [`repo-naming-agent-platform.md`](repo-naming-agent-platform.md) | เหตุผลที่เลือกชื่อ `agent-platform` + ตัวเลือกอื่น 6 ชื่อ |
| [`naming-convention-ecosystem.md`](naming-convention-ecosystem.md) | naming convention ทั้ง ecosystem + ลิสต์ "7 core repos" |

### Blueprint ระดับระบบ

| ไฟล์ | ระบบ | stack ที่เสนอ |
| --- | --- | --- |
| [`enterprise-agent-backend-os-blueprint.md`](enterprise-agent-backend-os-blueprint.md) | Backend OS สำหรับ agent (M0–M7) | Cloudflare Workers / DO / D1 / R2 |
| [`enterprise-agent-knowledge-platform-blueprint.md`](enterprise-agent-knowledge-platform-blueprint.md) | Knowledge platform + RAG (M1–M7) | Python / FastAPI / Postgres / Qdrant / Neo4j |
| [`navi-security-agent-blueprint.md`](navi-security-agent-blueprint.md) | AI Security Agent คู่กับ `navi-ims` (Phase 0–5, M0–M12) | FastAPI/Node · Redis · Postgres |
| [`ai-subscription-oauth-gateway-blueprint.md`](ai-subscription-oauth-gateway-blueprint.md) | Subscription/OAuth gateway **ขาออก** (M1–M6) | — |
| [`distributed-multi-agent-gateway-blueprint.md`](distributed-multi-agent-gateway-blueprint.md) | Task dispatcher + worker fleet หลัง NAT (Phase 1–5) | Node/TS หรือ FastAPI · MQTT/NATS · SQLite |

### รีวิวและแผนของ repo นี้

| ไฟล์ | เนื้อหา |
| --- | --- |
| [`agent-platform-contract-review.md`](agent-platform-contract-review.md) | รีวิวโครง repo นี้ (7.5/10) + ตาราง P0/P1/P2 + เสนอ `contracts/` |
| [`agent-platform-decisions-first-plan.md`](agent-platform-decisions-first-plan.md) | แผน Phase 0–5 ที่กำลังทำตามอยู่ + ADR 8 ตัว + DoD ของ repo นี้ |
| [`agent-platform-adr-review.md`](agent-platform-adr-review.md) | รีวิวหลังทำ Phase 0–1 (8.8/10) + **5 จุดที่ต้องแก้ก่อน Accept ADR** — เพิ่ม `contracts/capability/`, แยก provider entity/registry, ทบทวน runtime loop, กติกา conformance, นิยาม `modules/` |
| [`agent-platform-adr-review-2.md`](agent-platform-adr-review-2.md) | รีวิวรอบสอง (9.1/10) — **approve architecture direction** · เหลือ 3 งานก่อนเปิด `contracts/`: README consistency, capability first-class, conformance เป็นข้อกำหนด + เสนอ canonical architecture diagram |
| [`agent-platform-adr-review-3.md`](agent-platform-adr-review-3.md) | รีวิวรอบสาม (9.5/10) — **architecture review ผ่าน** · สั่งหยุดเพิ่ม ADR แล้วเข้า Decision Gate + **มีตัวเลือกที่แนะนำครบทั้ง 10 ADR** |
| [`agent-platform-pr11-review.md`](agent-platform-pr11-review.md) | รีวิว PR #11 (9.7/10) — **ผ่าน architecture review** · approve การไม่เขียน `approval/` + `event/` ว่าเป็น *governance-preserving omission* · สั่งหยุดออกแบบ แล้วไปทดสอบ contract กับ repo ลูกจริง |
| [`agent-platform-adr-decisions.md`](agent-platform-adr-decisions.md) | **ชุด Decision ที่เคาะจาก Platform Owner** ครบ 10 ADR + Authority · แยกสถานะ ADR-0006 เป็น versioning `ACCEPTED` / ownership `PENDING` (ติด devfactory-core) และแผนเดินต่อโดยไม่รอ #6 |

### repo ที่มีอยู่จริงแล้ว

| ไฟล์ | เนื้อหา |
| --- | --- |
| [`existing-repos.md`](existing-repos.md) | inventory ของ `devfactory-core` · `navi-ims` · `ai-web-harness` (สำรวจจาก remote จริง — ไม่ใช่ raw) |

## ข้อขัดแย้งที่รู้แล้ว

จุดเหล่านี้มี ADR รออยู่แล้ว ไม่ต้องพยายามอ่านให้ตรงกัน:

| ขัดกันเรื่อง | อยู่ใน ADR |
| --- | --- |
| ชื่อ core repo 4 เวอร์ชัน | [0002](../decisions/0002-core-repository-naming.md) |
| `agent-gateway` = inbound / outbound / fan-out | [0003](../decisions/0003-agent-gateway-boundary.md) |
| LLM Adapter vs Runtime Adapter vs AgentAdapter | [0004](../decisions/0004-agent-vs-model-provider.md) |
| platform สร้าง runtime เองไหม (backend-os §6 vs knowledge §5) | [0005](../decisions/0005-agent-runtime-boundary.md) |
| tenant model 2/3/5 ชั้น | [0007](../decisions/0007-multi-tenancy.md) |
| Cloudflare vs Python vs Node | [0008](../decisions/0008-reference-stack.md) |
| risk level `LOW/MEDIUM/HIGH/CRITICAL` คนละความหมาย (backend-os §9 vs navi Phase 4) | [0010](../decisions/0010-risk-approval-taxonomy.md) |
| capability มี 4 รูปแบบ (oauth-gateway §7/§8 vs distributed-gateway Phase 3) | [0009](../decisions/0009-capability-model.md) |

## หมายเหตุ

* `ai-web-harness/ref/` ใช้ naming แบบ `YYYY-MM-DD-<topic>-raw.md` ซึ่งดีกว่าที่นี่ (รู้ลำดับเวลา + รู้ว่าอันไหน raw) — ยังไม่ได้ rename ตาม เพราะจะทำให้ link ที่ส่งทีมไปแล้วเสีย
* รูป 6 รูปใน `navi-security-agent-blueprint.md` เป็น external link ไป `images.openai.com` ซึ่งอาจหมดอายุ
