# contracts/approval — ⏳ `external-authority-pending`

**ยังไม่เขียน schema** — ไม่ใช่เพราะยังไม่พร้อม แต่เพราะ **ยังไม่มีสิทธิ์**

## ทำไม

contract นี้จะมาจาก [`devfactory-core/rfcs/0002-governance-decision-contract.md`](https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/0002-governance-decision-contract.md) ซึ่ง:

* มีสถานะ `Draft`
* `GOVERNANCE.md` ของ repo นั้นระบุว่า **Architecture Owner ของมัน** มีอำนาจตัดสินสุดท้าย

[ADR-0006](../../decisions/0006-contract-versioning.md) ตัดสินว่าส่วน ownership ยัง `Pending external confirmation` — การเขียน schema ที่ประกาศตัวเป็น canonical version ของ RFC-0002 ตอนนี้คือการยึดอำนาจของอีก repo โดยพลการ ซึ่งขัดกับ governance ที่ ADR ชุดนี้ตั้งขึ้นเอง

ติดตามที่ [issue #6](https://github.com/monthop-gmail/agent-platform/issues/6)

## สิ่งที่จะอยู่ในนี้เมื่อได้รับการยืนยัน

จาก RFC-0002 (ใช้ได้ตามเดิม):

```text
decision: APPROVE | REJECT | REQUIRE_CHANGES
required: decision · reason · timestamp · authority
guarantees: immutable · every APPROVE auditable · no execution without APPROVE
```

ที่ platform ต้องเพิ่ม (จาก [extraction §2](../../architecture/devfactory-core-rfc-extraction.md)):

```text
tenant_id · workspace_id · execution_id · agent_id
action_risk · policy_id · expires_at · escalation_target
```

## เส้นแบ่งที่ตัดสินแล้ว

`approval` ≠ `policy` — [`contracts/policy/v1`](../policy/v1/) เขียนแล้วและใช้ได้ทันที

```text
action_risk (static)
      ↓
policy → authority: approval_required     ← contracts/policy/v1  ✅ พร้อมใช้
      ↓
approval request → APPROVE | REJECT | ...  ← ที่นี่  ⏳ pending
```

การยัด `rate-limit` และ `budget-limit` เข้าไปเป็น "decision" ที่ต้องมี `authority` ไม่มีความหมาย จึงแยกเป็นสอง contract ตั้งแต่ต้น
