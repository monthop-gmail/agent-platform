# consent/v1

## v1.1.0 — 2026-08-21

เพิ่ม optional `conditions` ตาม [ADR-0014](../../../decisions/0014-consent-access-time-conditions.md) (option B) จาก [issue #25](https://github.com/monthop-gmail/agent-platform/issues/25) ที่ `care-agent-platform` เปิดตอนทำ multi-organization (M6)

**ปัญหา:** ใบยินยอมตอบได้ว่ายังใช้ได้ไหมจาก `revoked_at` และ `expires_at` เท่านั้น ซึ่งทั้งคู่ต้องมีคนหรือเวลามาทำให้เกิด — ใบที่ผูกกับข้อเท็จจริงที่เปลี่ยนได้เอง (หมอที่ลาออกจากโรงพยาบาลที่ครอบครัวยินยอมให้) **ยังใช้ได้ตามสัญญา** ทั้งที่เงื่อนไขที่ยินยอมไม่เป็นจริงแล้ว

* `$defs.Condition` — `kind` (required · ชุดเปิด · `^[a-z][a-z0-9_]{2,63}$` แบบเดียวกับ `event/v1` `EventTypeName`) + `params` (optional object · โดเมนเป็นเจ้าของ) · **`additionalProperties: false` ที่ตัวเงื่อนไข**
* `conditions` — array, `minItems: 1` · **ไม่มี field = ไม่มีเงื่อนไข · `[]` ใช้ไม่ได้** (หลักเดียวกับ `expires_at: null`)
* `consent_rules` เพิ่ม 5 ข้อ — ตรวจทุกครั้งที่ใช้ · `kind` ไม่รู้จัก = ไม่อนุญาต · ตัวตรวจ error = ไม่อนุญาต · ออกใบที่ตรวจไม่ได้ไม่ได้ตั้งแต่แรก · narrow ได้อย่างเดียว
* `platform_rules` เพิ่มว่าใบที่มี `conditions` **ไม่ self-contained** ห้าม cache ผล valid ตามอายุใบ · และ `conditions` เข้ากฎ immutable เดียวกับ `scope`/`purpose`

### ทำไม `kind` + `params` ไม่ใช่ field โดเมนเรียงข้าง `kind`

ชั้นนอกสงวนไว้ให้ platform เพิ่ม field กลางทีหลังได้แบบ additive โดยไม่ชนคำของโดเมนที่มีคนใช้ไปแล้ว · ตรงกับที่ `event/v1` (`metadata`) และ `policy/v1` (`constraint`) ทำมาก่อน · `care-agent-platform` ที่ ship รูปแบน ๆ ไปแล้วต้อง migrate หนึ่งชั้น

### ไม่ breaking — payload ที่ valid กับ `v1.0.0` ยัง valid ทุกใบ

`additionalProperties: false` อยู่ที่ **ตัว `Condition` เท่านั้น** ซึ่งเป็น object ที่เพิ่งเกิด · ตัว grant ยังเปิดเหมือนเดิม · `required` ยัง 8 ตัวเท่าเดิม

### ยังไม่ทำในรอบนี้

* `event/v1` บันทึกว่าเงื่อนไขถูกประเมินแล้วและผ่าน — จำเป็นสำหรับ audit ย้อนหลัง แต่ผูกกับ [issue #23](https://github.com/monthop-gmail/agent-platform/issues/23) ไม่ควรตัดสินแยกกัน
* `policy/v1` `Decision` เพิ่ม optional `consent_id` — ค้างจาก `v1.0.0`

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
