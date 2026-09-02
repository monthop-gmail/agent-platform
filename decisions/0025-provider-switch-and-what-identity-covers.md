# ADR-0025: ย้าย provider กลางรอบ — identity ครอบ "ชุดที่แช่แข็ง" ส่วนตัวที่ใช้จริงเป็นของ execution

**Status:** Accepted (2026-09-02)
**Date:** 2026-09-02
**Depends on:** [ADR-0023](0023-frozen-bindings-and-identity.md) · [ADR-0009](0009-capability-model.md) · [ADR-0010](0010-risk-approval-taxonomy.md)
**Blocking:** [issue #52](https://github.com/monthop-gmail/agent-platform/issues/52) · `contracts/execution/v1`

## Context

[ADR-0023](0023-frozen-bindings-and-identity.md) ข้อ 3 บอกว่า *"identity ของสิ่งที่ build ต้องครอบ binding"* — [#52](https://github.com/monthop-gmail/agent-platform/issues/52) ชี้ว่าประโยคนั้นยังไม่พอ เพราะ `CompiledAgent` ไม่ได้แช่แข็ง binding ตัวเดียว แต่แช่แข็ง **ทั้งโซ่**:

```ts
model:          ModelBinding      // ตัวที่ตั้งใจใช้
modelFallbacks: ModelBinding[]    // ที่เหลือตามลำดับ
```

adapter ย้ายไปตัวถัดไปเมื่อโดน 429/5xx ซ้ำ ๆ **แล้วอยู่กับตัวใหม่ต่อ ไม่ย้อนกลับ** → run สองครั้งจาก package ใบเดียวกัน **identity เท่ากันเป๊ะ แต่รันด้วยคนละ model**

**ไม่ใช่กรณีสมมติ** — เขาชน 429/502/503 **ห้าครั้งใน 8 attempt** กับ endpoint ฟรีจริง

## คำตอบของคำถามหลัก

> identity ควรครอบ **"ชุดที่อนุญาต"** หรือ **"ตัวที่ใช้จริง"**

**ชุดที่อนุญาต** — และเหตุผลไม่ใช่ความสะดวก แต่เป็นเรื่องที่เป็นไปได้:

```text
identity ของสิ่งที่ build ครอบได้แค่สิ่งที่รู้ตอน build
ถ้าต้องครอบตัวที่ใช้จริง → รู้ได้ก็ต่อเมื่อรันจบ
                        → artifact จะไม่มี identity จนกว่าจะถูกใช้
                        → ซึ่งทำลายเหตุผลทั้งหมดที่ต้องมี identity
```

**ADR-0023 ไม่ผิด แต่เขียนไม่ครบ** — คำว่า *binding* ที่นั่นหมายถึง **ผลการ resolve ทั้งชุดที่ถูกแช่แข็ง** ไม่ใช่ตัวที่ถูกเลือกตอนรัน · ต้องเขียนให้ชัด เพราะ #52 อ่านแล้วตีความได้สองทางจริง

ผลที่ตามมาทันทีสำหรับผู้ขอ: **`manifestChecksum` ต้องครอบ `modelFallbacks` ด้วย และครอบ *ลำดับ* ของมัน** — สลับลำดับ = พฤติกรรมต่างกันภายใต้ 429 เดียวกัน

## แล้วตัวที่ใช้จริงอยู่ที่ไหน — และตรงนี้คือช่องว่างจริงในสัญญาเรา

`execution/v1` มี `provider_id` เป็น **string ตัวเดียว**:

> `null` = native runtime · มีค่า = external agent provider

execution ที่ย้าย provider กลางรอบจึงบันทึกได้แค่ตัวเดียว **ทั้งที่ครึ่งหลังรันด้วยอีกตัว** — record ที่อ่านแล้วได้ความจริงไม่ครบ ซึ่งเป็นแผลเดียวกับที่ [ADR-0013](0013-approval-supersedes-chain.md) · [ADR-0016](0016-recording-which-consent-allowed-access.md) · [ADR-0019](0019-execution-records-its-approval.md) ปิดไปแล้วสามครั้ง

และ `attempt` / `max_attempts` บอกแค่**จำนวนครั้ง** ไม่ได้บอกว่า *ลองใหม่กับตัวเดิม* หรือ *ย้ายไปตัวอื่น* — คนละเรื่องกันสิ้นเชิงในแง่ audit และ cost

## Options

### A. ห้ามย้าย provider กลางรอบ — ให้เป็นหน้าที่ของ router เท่านั้น

* ✅ `provider_id` ตัวเดียวยังถูกต้อง ไม่ต้องแก้อะไร
* ❌ **บังคับ implementation** ทั้งที่สัญญานี้เป็นเจ้าของ *บันทึก* ไม่ใช่ *วิธีทำ* — `CompiledAgent` รันบน runtime 5 ตัวที่ไม่มี router ของ platform อยู่ในสาย
* ❌ ทำให้ผู้ขอต้องเลือกระหว่าง *ไม่ ship* กับ *สร้าง router เอง* ซึ่งไม่ใช่คำถามที่เขาถาม
* ❌ การย้ายเมื่อ endpoint ไม่ว่างเป็นพฤติกรรมที่ทำให้รายงานยังตรงกับความจริง — ห้ามมันคือการเลือกให้ระบบล้มเหลวเงียบ ๆ แทน

### B. identity ครอบทั้งโซ่ + `execution/v1` บันทึกการย้ายไว้ ⭐

* ✅ ตอบคำถามหลักโดยไม่บังคับว่าใครต้องเป็นคนย้าย — **platform เป็นเจ้าของสิ่งที่ต้องบันทึก ไม่ใช่วิธีทำ** ตรงกับที่ตอบทุกใบที่ผ่านมา
* ✅ ปิดช่อง `provider_id` ตัวเดียวที่ทำให้ record บอกความจริงไม่ครบ
* ✅ additive — `execution/v1` ยังไม่มีใครผลิต payload (ตรวจ `devfactory-core` แล้วเขา pin แต่ job state machine อยู่คนละชั้น)
* ❌ ไม่ได้แก้เรื่อง cost attribution ให้จบในใบเดียว (ดูข้างล่าง — ตั้งใจ)

### C. บันทึกที่ `event/v1` อย่างเดียว ไม่แตะ `execution/v1`

* ✅ ผู้ขอบันทึกเป็น event อยู่แล้วและ *"trace ระดับ event ตรงกับความจริง"*
* ❌ **execution record อ่านคนเดียวยังบอกความจริงไม่ครบ** ต้องมี event store อยู่ด้วยเสมอ — เหตุผลเดียวกับที่ ADR-0013 และ ADR-0019 ปฏิเสธทางนี้ไปแล้วสองครั้ง
* ❌ vocabulary ของ `event/v1` เป็นของ `devfactory-core` — ผู้ขอเลี่ยงไม่ขอ `EventType` ใหม่ในใบนี้ด้วยเหตุผลนั้นเอง และถูกแล้ว

### D. นิยาม `ModelBinding` chain เป็น contract กลาง

* ❌ ตกเกณฑ์ [ADR-0012](0012-consent-contract.md) ข้อ 2 และ 4 — consumer รายเดียว และรูปของ build artifact เป็นของ repo ที่ build ตามที่ ADR-0023 ตัดสินไปแล้ว

## Decision

**B** — identity ครอบทั้งชุดที่แช่แข็ง · ตัวที่ใช้จริงเป็นสถานะของ execution และต้องบันทึกไว้ที่ `provider_switches`

**Reason:** identity ของสิ่งที่ build ครอบได้แค่สิ่งที่รู้ตอน build — ถ้าต้องครอบตัวที่ใช้จริง artifact จะไม่มี identity จนกว่าจะถูกใช้ ซึ่งทำลายเหตุผลทั้งหมดที่ต้องมีมัน · ADR-0023 จึงไม่ผิด แค่ต้องเขียนให้ชัดว่า *binding* = ทั้งชุดที่แช่แข็ง · ส่วนตัวที่ใช้จริงเป็น **สถานะของ execution** และ `provider_id` ตัวเดียววันนี้ทำให้ record บอกความจริงไม่ครบ ซึ่งเป็นแผลเดียวกับที่ปิดไปแล้วสามครั้ง · ปฏิเสธ A เพราะเป็นการบังคับ implementation ในสัญญาที่เป็นเจ้าของบันทึกไม่ใช่วิธีทำ · ปฏิเสธ C เพราะ execution record ต้องอ่านคนเดียวรู้เรื่อง

**Authority:** Monthop Champaruang — Platform Owner / Architecture Authority of `agent-platform`

### สิ่งที่เปลี่ยน

| ไฟล์ | เปลี่ยนอะไร |
| --- | --- |
| `execution/v1` | เพิ่ม `provider_switches` (optional array) — `{from, to, at, reason}` · และเขียนกำกับ `provider_id` ว่าหมายถึง **ตัวที่มีผลล่าสุด** ไม่ใช่ตัวเดียวที่เคยใช้ |
| `model/v1` `platform_rules` | ขยายความว่า *binding* ที่ต้องอยู่ใน identity หมายถึง **ทั้งชุดที่แช่แข็งรวมลำดับ** |

`from` เป็น optional เพราะการย้ายครั้งแรกอาจไม่มีตัวก่อนหน้าที่ระบุได้ · `reason` ผูกกับ `error/v1` `Category` ที่มีอยู่แล้ว ไม่ตั้ง enum ใหม่

### ⚠️ cost attribution — ตอบเป็นกฎ ยังไม่สร้าง field

คำถามข้อ 3 ของ #52 ถูกต้อง: run เดียวข้าม provider มี `usage` จากหลายเจ้าที่ราคาต่อ token คนละอัตรา · `budget.max_cost_usd_per_execution` รวมกันแล้ว**คิดผิด**

แต่**ยังไม่มี consumer รายไหนคำนวณ cost จริงสักราย** — การออกแบบรูปของ per-provider usage ตอนนี้คือการเดารูปให้กับงานที่ยังไม่มีใครทำ ซึ่ง repo นี้ปฏิเสธมาตลอด ([`embedding`](https://github.com/monthop-gmail/agent-platform/issues/50) ก็ด้วยเหตุผลเดียวกัน)

**สิ่งที่ทำได้และควรทำตอนนี้คือเขียนกฎว่าอย่าคิดผิด:**

> `usage` ของ execution ที่มี `provider_switches` **ใช้คิด cost ตรง ๆ ไม่ได้** เพราะรวม token จากหลายอัตราเข้าด้วยกัน · ผู้ที่ต้องคิด cost ต้องแยกตาม provider เอง และเมื่อมี consumer ที่ทำจริงค่อยเคาะรูปกลาง

การเขียนกฎโดยยังไม่มี field **ดีกว่าการมี field ที่ไม่มีใครใช้แล้วเดารูปผิด** — และดีกว่าการเงียบ ซึ่งจะทำให้คนแรกที่คิด cost คิดผิดโดยไม่มีอะไรเตือน

### ไม่ bump major — `execution/v1` `v1.1.0` → `v1.2.0`

optional field ใหม่ · `required` ยัง 5 ตัวเท่าเดิม · ไม่มีการเข้มขึ้น · `provider_id` ไม่เปลี่ยน type และไม่เปลี่ยนความหมายสำหรับ execution ที่ไม่เคยย้าย

`model/v1` เปลี่ยนแค่ถ้อยคำใน `platform_rules` → `v1.1.0` → **`v1.2.0`**

## Consequences

* `agent-builder-dsh-poc` รู้ว่า `manifestChecksum` ต้องครอบ `modelFallbacks` **รวมลำดับ** — และรู้ว่าตัวที่ใช้จริงไม่ใช่หน้าที่ของ identity
* **execution record อ่านคนเดียวแล้วรู้ว่าเคยย้าย provider ไหม** — ไม่ต้องมี event store อยู่ด้วย
* platform **ไม่ได้ตัดสินว่าใครเป็นคนย้าย** — router หรือ adapter ก็ได้ · สิ่งที่บังคับคือถ้าย้ายแล้วต้องบันทึก
* **drift check ตรวจข้อนี้ไม่ได้** — ว่าผู้ผลิตบันทึกการย้ายจริงไหม พิสูจน์ได้จาก payload จริงของ consumer เท่านั้น
* ยังไม่ปิด และมีเหตุผลกำกับ:
  * **cost attribution ข้าม provider** — รูปกลางรอ consumer ที่คิด cost จริง
  * **[#53](https://github.com/monthop-gmail/agent-platform/issues/53)** `profile.tools.allow` กับ namespace ของ tool — คนละเรื่อง แต่ผู้ขอรายเดียวกันจะชนทั้งสองเมื่อ pin

## Sources

[issue #52](https://github.com/monthop-gmail/agent-platform/issues/52) · [ADR-0023](0023-frozen-bindings-and-identity.md) เงื่อนไขข้อ 3 · [ADR-0013](0013-approval-supersedes-chain.md) และ [ADR-0019](0019-execution-records-its-approval.md) เหตุผลที่ record ต้องอ่านคนเดียวรู้เรื่อง · `execution/v1` `provider_id` `attempt` `max_attempts` · `model/v1` `$defs.Usage` · `profile/v1` `budget.max_cost_usd_per_execution`
