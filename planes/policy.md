# Policy — Plane Boundary

**Plane Boundary Documentation** — เอกสารขอบเขต ไม่ใช่ที่เก็บ code ([ADR-0001](../decisions/0001-platform-scope.md))

| | |
| --- | --- |
| Implementation | ยังไม่มี repo · `devfactory-core/packages/governance` เป็นของฝั่ง job |
| Contracts | [`policy/v1`](../contracts/policy/v1/) · [`profile/v1`](../contracts/profile/v1/) · `approval/` ⏳ |
| ADR | [0010](../decisions/0010-risk-approval-taxonomy.md) · [0006](../decisions/0006-contract-versioning.md) |

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

## fallback ที่บังคับ

เจอค่าที่ไม่รู้จัก → เลือกทางที่ปลอดภัยกว่าเสมอ · `action_risk` → `critical` · `authority` → `human_command_required`

## สถานะ

`policy/v1` เขียนแล้วและใช้ได้ทันที · `approval/` ติด `external-authority-pending` รอ [issue #6](https://github.com/monthop-gmail/agent-platform/issues/6)
