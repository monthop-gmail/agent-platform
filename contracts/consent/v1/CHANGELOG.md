# consent/v1

## v1.0.0 — 2026-08-19

ตั้งต้นตาม [ADR-0012](../../../decisions/0012-consent-contract.md) (option A + D1) จาก [issue #15](https://github.com/monthop-gmail/agent-platform/issues/15) ที่ `care-agent-platform` เสนอ

* **semantics และ wire schema เป็นของ `agent-platform` ทั้งคู่** — ไม่มี `derived_from` เพราะไม่ derive จาก repo ไหน · ต่างจาก `approval/v1` และ `event/v1`
* โครงตั้งต้นจาก implementation จริงของ `care-agent-platform` (`contracts/consent/v1` + [ADR-0007](https://github.com/monthop-gmail/care-agent-platform/blob/main/decisions/0007-consent-and-data-access.md)) ที่เก็บให้ domain-free ไว้แต่แรก
* ยก `consent_rules` ทั้ง 5 ข้อจากร่างมาครบ + เพิ่มข้อที่หกว่าต้องผ่านทั้ง `policy/v1` และ consent

### ปิดช่องว่างจากร่างเดิม 4 จุด

| ช่องว่าง | ปิดด้วย |
| --- | --- |
| ร่างมีแค่ `revoked_at` ไม่บันทึกว่าใครถอน | `revoked_by` + `revoked_reason` เป็น **required เมื่อมี `revoked_at`** ผ่าน `dependentRequired` |
| `expires_at: null` กำกวม | ระบุว่า `null` = **ไม่มีวันหมดอายุ** ไม่ใช่ "ยังไม่ได้กำหนด" · ไม่มีสถานะที่สาม |
| ไม่มีเหตุผลของการเพิกถอน | `revoked_reason` required คู่กับ `revoked_by` |
| `purpose` เป็น string เดี่ยว — หลายวัตถุประสงค์ในใบเดียวได้ไหม | **บังคับหนึ่ง grant = หนึ่ง purpose** แยกใบถ้ามีหลายวัตถุประสงค์ |

### เพิ่มนอกร่าง (บันทึกไว้ให้ชัดว่าไม่ได้อยู่ในคำขอ)

* `authority_basis` (optional) — เมื่อ `granted_by` ไม่ใช่เจ้าของข้อมูลเอง ให้บันทึกว่าให้แทนโดยอำนาจอะไร · ถ้าไม่มี audit จะตอบไม่ได้ว่าทำไมคนนั้นให้แทนได้
* **ไม่มี field `status` โดยเจตนา** — สถานะคำนวณจาก `revoked_at` และ `expires_at` · field ที่เก็บสถานะซ้ำจะ drift จากความจริง
* กฎว่า scope ที่ consumer ไม่รู้จัก = **ไม่ได้รับอนุญาต** ตามหลัก fallback ที่ปลอดภัยของ [`contracts/README.md`](../../README.md)

### ยังไม่ทำในรอบนี้

`policy/v1` `Decision` เพิ่ม optional `consent_id` — แยกเป็นการเปลี่ยนอีกครั้ง เพื่อให้ `consent/v1` ยืนได้เองก่อน
