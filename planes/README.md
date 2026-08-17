# Planes

**Plane Boundary Documentation** — เอกสารระบุขอบเขต ความรับผิดชอบ และ**สิ่งที่ห้ามทำ**ของแต่ละ plane

> ⚠️ ที่นี่ไม่ใช่ที่เก็บ code และไม่ใช่ที่รอ code — implementation อยู่ใน repo ลูกที่ระบุไว้ที่หัวของแต่ละไฟล์ ([ADR-0001](../decisions/0001-platform-scope.md))

โฟลเดอร์นี้เดิมชื่อ module dirs 10 ตัวที่ root — ย้ายมาตาม [module mapping](../architecture/module-mapping.md) เมื่อ `contracts/` v1 นิ่งแล้ว

## 11 plane

| Plane | หน้าที่ | Implementation | Contract |
| --- | --- | --- | --- |
| [`gateway`](gateway.md) | ทางเข้า **inbound** — auth, policy check, audit | `agent-gateway` ❌ | ยังไม่มี |
| [`runtime`](runtime.md) | agent loop, state, lifecycle — native + external | `agent-backend-os` ❌ / agent provider | ✅ `execution/v1` |
| [`harness`](harness.md) | execution policy — บังคับลำดับขั้นในหนึ่งงาน | `ai-web-harness` 🚧 | ✅ `profile/v1` |
| [`evals`](evals.md) | สนามทดสอบ — scenario, evaluator, regression | `navi-security-agent` ❌ | ยังไม่มี format กลาง |
| [`tools`](tools.md) | catalog ของ tool + MCP registration | ❌ | ✅ `tool/v1` `mcp/v1` |
| [`policy`](policy.md) | ทำได้ไหม ต้องให้ใครอนุมัติ | ❌ | ✅ `policy/v1` `approval/v1` |
| [`knowledge`](knowledge.md) | ingest, retrieval, citation, ACL | `enterprise-knowledge` ❌ | ใช้ `tool/v1` |
| [`workflow`](workflow.md) | orchestration ข้ามขั้น ข้าม agent | ❌ | ✅ `execution/v1` |
| [`sandbox`](sandbox.md) | ที่ที่ command รันจริง + isolation | ❌ | ใช้ `capability/v1` |
| [`observability`](observability.md) | trace, audit, cost, replay | ❌ | ✅ `event/v1` |
| [`backend-os`](backend-os.md) | data plane + connector + บ้านของ native runtime | `agent-backend-os` ❌ | ใช้ `identity/v1` |

✅ contract พร้อม · 🚧 scaffold · ❌ ยังไม่มี repo

## หลักที่ทุก plane ต้องเคารพ

จาก `devfactory-core` RFC-0004 · [ADR-0003](../decisions/0003-agent-gateway-boundary.md) · [ADR-0005](../decisions/0005-agent-runtime-boundary.md) — สามแหล่งที่เห็นตรงกัน:

```text
execution ไม่ตัดสิน governance เอง
execution ไม่แตะ backend resource ตรง ๆ
execution ไม่ถือ provider credential เอง
orchestration ไม่แก้ artifact เอง
```

external agent provider อยู่ใต้กฎเดียวกัน — ไม่มีสิทธิ์พิเศษเพราะเป็นของ vendor

## เส้นแบ่งที่คนสับสนบ่อย

| คู่ที่มักปนกัน | เส้นแบ่ง |
| --- | --- |
| `harness` vs `evals` | policy ที่รันใน production **vs** test rig ที่รันตอน CI |
| `harness` vs `workflow` | lifetime ของ request เดียว **vs** durable ข้าม process |
| `runtime` vs `sandbox` | ตัดสินว่าจะรันอะไร **vs** ที่ที่มันรัน |
| `tools` vs `policy` | มี tool อะไรบ้าง **vs** ใครใช้ได้ |
| `policy` vs `approval` | ผลประเมินของเครื่อง **vs** คำตัดสินของผู้มีอำนาจ |
| `gateway` (inbound) | ไม่ใช่ `model-gateway` (outbound) และไม่ใช่ `agent-fleet` (fan-out) |

## ที่เปลี่ยนจากโครงเดิม

| เดิม | ตอนนี้ |
| --- | --- |
| `agent-harness/` | แยกเป็น `harness` + `evals` — คำเดียวเคยใช้เรียกสองของ |
| `tool-registry/` | `tools` — registry เป็น implementation ส่วน contract คือ `tool/v1` + `mcp/v1` |
| `policy-engine/` | `policy` — engine เป็น implementation |
| `agent-gateway/` | `gateway` — และจำกัดความหมายไว้ที่ inbound เท่านั้น |

ไม่มี plane ไหนถูกลบ — ทั้ง 10 ตัวเดิมยังอยู่ครบ เพิ่ม `evals` เป็นตัวที่ 11 จากการ split
