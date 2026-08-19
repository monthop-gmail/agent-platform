# Policy — Plane Boundary

**Plane Boundary Documentation** — เอกสารขอบเขต ไม่ใช่ที่เก็บ code ([ADR-0001](../decisions/0001-platform-scope.md))

| | |
| --- | --- |
| Implementation | ยังไม่มี repo · `devfactory-core/packages/governance` เป็นของฝั่ง job |
| Contracts | [`policy/v1`](../contracts/policy/v1/) · [`profile/v1`](../contracts/profile/v1/) · [`approval/v1`](../contracts/approval/v1/) · [`consent/v1`](../contracts/consent/v1/) |
| ADR | [0010](../decisions/0010-risk-approval-taxonomy.md) · [0006](../decisions/0006-contract-versioning.md) · [0013](../decisions/0013-approval-supersedes-chain.md) |

## รับผิดชอบ

ตอบคำถามเดียว: **"การกระทำนี้ทำได้ไหม และต้องให้ใครอนุมัติ"**

```text
action_risk (static จาก tool/capability)
      ↓
policy evaluation  ← tenant · workspace · role · agent · profile · เวลา · budget
      ↓
effect: allow | deny
authority: auto | notify | approval_required | human_command_required
constraint: none | rate_limited | budget_exceeded | quota_exhausted
```

## Policy ≠ Consent ≠ Approval

สาม contract ในตระกูลเดียวกันที่ตอบคำถามคนละข้อ — การเข้าถึงข้อมูลบุคคลต้องผ่านทั้งสามที่เกี่ยวข้อง ผ่านอันเดียวไม่พอ

| | ตอบคำถาม | contract |
| --- | --- | --- |
| **Policy** | identity นี้ทำ action นี้ได้ไหม | `policy/v1` |
| **Consent** | **กับข้อมูลของคนไหน** | `consent/v1` |
| **Approval** | ใครอนุมัติให้ทำครั้งนี้ | `approval/v1` ⏳ |

ตัวอย่างที่ทำให้เห็นว่าแยกกันจริง: ลูกสาวมีสิทธิ์ `medication.read` (policy ผ่าน) แต่อ่านได้เฉพาะยาของแม่ตัวเอง ไม่ใช่ของผู้ป่วยทุกคนใน tenant (consent จำกัด)

🔒 **ความสัมพันธ์ไม่ให้สิทธิ์อะไรโดยอัตโนมัติ** — ญาติ ผู้ดูแล หรือทีมเดียวกัน ไม่ได้ทำให้เข้าถึงได้ ต้องมี grant ที่ชัดเจน

## Policy ≠ Approval

แยกกันตั้งแต่ contract ([extraction §2](../architecture/devfactory-core-rfc-extraction.md)):

| | คืออะไร | อยู่ที่ |
| --- | --- | --- |
| **Policy** | ผลประเมินของเครื่อง — "ต้องขออนุมัติไหม" | `contracts/policy/v1` ✅ |
| **Approval** | คำตัดสินของผู้มีอำนาจ — `APPROVE` / `REJECT` / `REQUIRE_CHANGES` | `contracts/approval/` ⏳ pending |

การยัด `rate_limited` เข้าไปเป็น "decision ที่ต้องมี authority" ไม่มีความหมาย จึงไม่รวมเป็น enum เดียว

## ห้ามทำ

* **hard-code mapping `action_risk → authority`** — ต้องเป็น config ต่อ tenant/profile ([ADR-0010](../decisions/0010-risk-approval-taxonomy.md)) เพราะ tenant หนึ่งให้ high = `approval_required` อีก tenant ให้ high = `human_command_required`
* ให้ execution ประเมิน policy ของตัวเอง
* นำ decision ที่ `expires_at` ผ่านแล้วกลับมาใช้ซ้ำ
* **แก้ approval ที่บันทึกไปแล้ว** — เปลี่ยนใจ = ใบใหม่ที่มี `supersedes_approval_id` ชี้ใบเดิม · ใบเดิมยังคงอยู่ ([ADR-0013](../decisions/0013-approval-supersedes-chain.md))

## fallback ที่บังคับ

เจอค่าที่ไม่รู้จัก → เลือกทางที่ปลอดภัยกว่าเสมอ · `action_risk` → `critical` · `authority` → `human_command_required`

## สถานะ

`policy/v1` และ [`approval/v1`](../contracts/approval/v1/) เขียนแล้วทั้งคู่ · semantics ของ approval (decision vocabulary + guarantees) เป็นของ `devfactory-core` แก้ที่นี่ไม่ได้ ([ADR-0006](../decisions/0006-contract-versioning.md))

`approval/v1` v1.1.0 เพิ่ม `supersedes_approval_id` เพื่อให้ guarantee ข้อ *"การเปลี่ยนใจคือ approval ใบใหม่ที่อ้างใบเดิม"* ทำตามได้จริง — เป็น field ระดับ platform ที่เพิ่มผ่าน ADR ที่นี่ได้เอง ไม่ใช่การแตะ semantics ([ADR-0013](../decisions/0013-approval-supersedes-chain.md))
