# ADR-0024: `tool_calling` เข้า taxonomy — และ scope ที่ประกาศไว้แต่ไม่มีใครผูก

**Status:** Accepted (2026-09-02)
**Date:** 2026-09-02
**Depends on:** [ADR-0009](0009-capability-model.md) · [ADR-0006](0006-contract-versioning.md) · [ADR-0018](0018-policy-result-single-source.md)
**Blocking:** [issue #50](https://github.com/monthop-gmail/agent-platform/issues/50) · `contracts/capability/v1`

## Context

[#50](https://github.com/monthop-gmail/agent-platform/issues/50) ขอสองอย่าง — เพิ่ม `tool_calling` เข้า `CapabilityId` และ **แยกกลุ่มว่าอันไหนเป็นคุณสมบัติของ model อันไหนของ runtime**

ระหว่างลงมือพบว่า **ครึ่งหลังมีอยู่แล้ว** — `capability/v1` มี `$defs.CapabilityScope` ตั้งแต่วันแรก:

```yaml
CapabilityScope:
  description: 3 ระดับที่ห้ามปนกัน (ADR-0009) — capability ตัวเดียวกันอยู่ได้แค่ scope เดียว
  enum:
    - provider   # ความสามารถของ model/agent provider เช่น long_context, vision
    - host       # ความสามารถของ worker ที่รัน เช่น docker, network_egress
    - tool       # ความสามารถที่มาจาก tool ที่ต่ออยู่ เช่น github, browser
```

**การแบ่งกลุ่มจึงไม่ใช่ของใหม่ที่ต้องออกแบบ** — ถ้าเพิ่ม block ใหม่เข้าไปอีกจะกลายเป็นสองที่ที่พูดเรื่องเดียวกัน ซึ่งเป็นสิ่งที่ [ADR-0018](0018-policy-result-single-source.md) เพิ่งเลิกทำ

## แต่กฎที่เขียนไว้ไม่มีอะไรทำให้มันจริง

`scope` ถูกประกาศเป็น field ของ **หนึ่งรายการใน catalog** (`required: [id, scope, action_risk, description]`) — แปลว่า **คนทำ catalog เป็นคนตัดสินว่า capability ตัวนั้นอยู่ scope ไหน**

และไล่ทั้ง repo แล้ว:

* **ไม่มี catalog instance อยู่ที่ไหนเลย** — schema บอกรูปของรายการ แต่ไม่เคยมีใครตีพิมพ์รายการจริง
* `requirement.schema.yaml` ที่ `agent/v1.capability_requirement` ใช้ **ไม่มี scope** — อ้าง `CapabilityId` อย่างเดียว
* `CapabilityScope` ถูกอ้างที่เดียวคือในไฟล์ตัวเอง

```text
กฎบอก:      capability ตัวเดียวกันอยู่ได้แค่ scope เดียว
สัญญาให้:    ทุก catalog เขียน scope ของตัวเองได้อิสระ
        ↓
สอง catalog บอกว่า `mcp` อยู่คนละ scope ได้ โดยไม่มีอะไรผิดสักฝ่าย
และวันนี้ไม่มีใครตอบได้ด้วยซ้ำว่า `github` อยู่ scope ไหน
```

**เป็นแผลตระกูลเดียวกับที่ repo นี้เจอมาแล้วห้าครั้ง — กฎที่บังคับสิ่งที่ไม่มีที่ให้ยึด** ([#22](https://github.com/monthop-gmail/agent-platform/issues/22) · [ADR-0016](0016-recording-which-consent-allowed-access.md) · [ADR-0019](0019-execution-records-its-approval.md) · [ADR-0020](0020-consent-event-vocabulary.md) · [ADR-0022](0022-agent-may-narrow-its-own-scope.md)) — **ครั้งที่หก**

ต่างจากห้าครั้งก่อนตรงที่ครั้งนี้ไม่ได้ขาด *field* แต่ขาด **ค่าที่ field นั้นควรยึด**

## `tool_calling` อยู่ scope ไหน — และทำไมคำถามนี้ตอบยากถ้าไม่มีแผนที่

`tool_calling` = **model นี้ปล่อย tool call ออกมาได้ไหม** ซึ่งเป็นคุณสมบัติของ provider เหมือน `vision` `long_context` `streaming`

ต่างจาก `github` · `browser` · `mcp` ที่เป็น **tool ที่ต่ออยู่** — คนละคำถามกันคนละชั้น:

```text
tool_calling (provider)  →  model พูดภาษา tool call เป็นไหม
github · browser (tool)  →  มี tool อะไรให้เรียกบ้าง
```

model ที่ `tool_calling: false` เรียก `github` ไม่ได้แม้ tool นั้นจะต่ออยู่ · **สองอย่างนี้ไม่ทดแทนกัน** และนี่คือเหตุผลที่ `mcp` ที่มีอยู่แล้วครอบเรื่องนี้ไม่ได้ตามที่ #50 ชี้ไว้

## Options

### A. เพิ่ม `tool_calling` อย่างเดียว — ไม่แตะเรื่อง scope

* ✅ เล็กที่สุด ตอบคำถามที่ถามมาตรง ๆ
* ❌ **คนที่มาเพิ่มค่าถัดไปยังไม่รู้ว่าเติมเข้ากลุ่มไหน** ซึ่งเป็นสิ่งที่ #50 ข้อ 3 ชี้ว่าสำคัญกว่าข้อ 1
* ❌ กฎ *"ตัวเดียวกันอยู่ได้แค่ scope เดียว"* ยังไม่มีอะไรทำให้จริงต่อไป

### B. เพิ่ม `tool_calling` + block จัดกลุ่มใหม่ (`capability_groups`)

* ✅ ตอบ #50 ตรงตามที่ขอ
* ❌ **สร้างที่ที่สองที่พูดเรื่องเดียวกับ `CapabilityScope`** — ADR-0018 เพิ่งเลิกทำแบบนี้ · สองที่ที่ต้องตรงกันคือสองที่ที่จะไม่ตรงกัน

### C. เพิ่ม `tool_calling` + ตีพิมพ์ **แผนที่ id → scope ที่เป็นทางการ** ⭐

ไม่สร้างแนวคิดใหม่ · ใช้ `CapabilityScope` ที่มีอยู่ แล้วเติมสิ่งที่ขาดจริงคือ **ค่าที่ทุก catalog ต้องยึด**

* ✅ ทำให้กฎ *"ตัวเดียวกันอยู่ได้แค่ scope เดียว"* **ตรวจได้เป็นครั้งแรก**
* ✅ ตอบ #50 ข้อ 3 โดยไม่เพิ่มคำศัพท์ใหม่ — กลุ่มที่เขาถามหาคือ `provider` vs `host`/`tool` ที่มีอยู่แล้ว
* ✅ วันนี้ยังไม่มีใครตีพิมพ์ catalog เลย จึง**ไม่มีใครต้องแก้ของที่ทำไปแล้ว**
* ❌ แผนที่นี้ list ค่าซ้ำกับ enum → **drift ได้** ถ้าไม่มีอะไรบังคับ (แก้ด้วย check ข้างล่าง)

### D. ย้าย `scope` ออกจาก catalog entry ไปเป็นของ taxonomy อย่างเดียว

* ✅ ไม่มีทาง drift เพราะมีที่เดียว
* ❌ **breaking** — `scope` เป็น `required` ของ catalog entry ตาม ADR-0006
* ❌ ปิดทางที่ deployment หนึ่งอาจต้องระบุ scope ต่างจากค่ากลางด้วยเหตุผลจริง ซึ่งยังไม่มีหลักฐานว่าไม่มี

## Decision

**C** — เพิ่ม `tool_calling` + ตีพิมพ์แผนที่ `canonical_scope` ที่ทุก catalog ต้องยึด · บังคับด้วย check ไม่ใช่ความตั้งใจ

**Reason:** การแบ่งกลุ่มที่ #50 ขอ **มีอยู่แล้วในชื่อ `CapabilityScope`** — เพิ่มบล็อกใหม่คือการสร้างที่ที่สองที่พูดเรื่องเดียวกัน ซึ่ง ADR-0018 เพิ่งเลิกทำ · สิ่งที่ขาดจริงคือ **ค่าที่ทุก catalog ต้องยึด** ทำให้วันนี้ไม่มีใครตอบได้ว่า `github` อยู่ scope ไหน และกฎ *"ตัวเดียวกันอยู่ได้แค่ scope เดียว"* ไม่มีอะไรทำให้จริง · ปฏิเสธ A เพราะทิ้งข้อที่ #50 บอกเองว่าสำคัญกว่า · ปฏิเสธ D เพราะ breaking และปิดทางที่ยังไม่มีหลักฐานว่าไม่ต้องการ

**Authority:** Monthop Champaruang — Platform Owner / Architecture Authority of `agent-platform`

### แผนที่ที่ตีพิมพ์

| scope | capability |
| --- | --- |
| `provider` — ของ model/agent provider | `vision` · `long_context` · `streaming` · **`tool_calling`** |
| `host` — ของ worker ที่รัน | `code_execution` · `shell` · `filesystem` · `docker` · `network_egress` |
| `tool` — ของ tool ที่ต่ออยู่ | `git` · `github` · `browser` · `mcp` |
| ข้ามชั้น | `autonomous_execution` |

`autonomous_execution` **ไม่ใช่ความสามารถทางเทคนิค** แต่เป็นระดับอำนาจ — จึงไม่เข้ากับสาม scope ที่นิยามไว้ · **บันทึกไว้เป็นข้อยกเว้นที่รู้แล้ว ไม่ยัดเข้ากลุ่มใดกลุ่มหนึ่งเพื่อให้ตารางสวย** · ถ้าจะจัดที่ให้มันจริงต้องเป็น ADR ของตัวเอง เพราะแตะนิยามของ `CapabilityScope` ที่ frozen อยู่ใน ADR-0009

### แผนที่ซ้ำกับ enum — จึงต้องมี check ไม่ใช่แค่ความตั้งใจ

การ list ค่าสองที่คือสิ่งที่ repo นี้ห้ามไว้ทุกที่ · ที่นี่หลีกไม่ได้เพราะ JSON Schema ไม่มีทาง derive enum จาก mapping ได้ · **จึงต้องบังคับด้วย check แทน**:

```text
keys(canonical_scope ทุกกลุ่มรวมกัน)  ==  CapabilityId.enum   ตรงกันเป๊ะ
  ขาด → มีค่าที่ไม่มีใครบอกว่าอยู่ scope ไหน
  เกิน → มีค่าที่ไม่อยู่ใน taxonomy แล้ว
  ซ้ำ  → ละเมิดกฎ "ตัวเดียวกันอยู่ได้แค่ scope เดียว" ตรง ๆ
```

**นี่คือครั้งแรกที่กฎข้อนั้นถูกบังคับด้วยเครื่อง** — และเป็นเหตุผลหลักที่เลือก C แทน A

### ไม่ bump major — `capability/v1` `v1.0.0` → `v1.1.0`

| เกณฑ์ breaking ของ [ADR-0006](0006-contract-versioning.md) | การเปลี่ยนนี้ |
| --- | --- |
| ลบค่าออกจาก enum · เปลี่ยนความหมายของค่าเดิม | ❌ 13 ค่าเดิมไม่ขยับ |
| เพิ่ม required · optional → required | ❌ ไม่มี |
| เข้มขึ้นใน validation | ❌ **ผ่อนอย่างเดียว** — `CapabilityId` รับค่าเพิ่มหนึ่งค่า · `canonical_scope` เป็นบล็อกอธิบาย ไม่ใช่ constraint |

**ตรวจ consumer แล้ว** — `care-agent-platform` เป็นรายเดียวที่ pin `capability/v1` และ manifest ของเขาเขียนกำกับเองว่า *"`capability/v1` — ActionRisk — ผูกกับ capability ไม่ใช่กับ request"* · ค้นโค้ดเขาแล้วไม่มีการใช้ค่า `CapabilityId` เลยสักค่า · **เพิ่มค่าจึงไม่กระทบเขา — ยืนยันจาก manifest และโค้ดจริง ไม่ใช่จากการอนุมานว่า additive แล้วปลอดภัย**

## Consequences

* `agent-builder-dsh-poc` แสดงข้อกำหนด *"ต้องการ model ที่เรียก tool ได้"* ได้เป็นครั้งแรก
* **มีแผนที่ให้ตอบได้ว่า capability แต่ละตัวอยู่ scope ไหน** — วันนี้ไม่มีใครตอบได้
* คนที่มาเพิ่มค่าถัดไป **ถูกบังคับให้ระบุ scope** ไม่งั้น check แดง — ตอบข้อกังวลของ #50 ข้อ 3 โดยตรง
* **ยังไม่มี catalog instance ในระบบเลย** — ADR นี้ไม่ได้สร้างมัน · ใครตีพิมพ์ catalog ต้องใช้ scope ตามแผนที่นี้ ไม่ใช่ตัดสินเอง
* `autonomous_execution` ยังไม่มีบ้านที่แท้จริง — บันทึกไว้ ไม่กลบ
* `llm-gateway` แยก `embedding` เป็น tag ของตัวเองด้วย ซึ่ง taxonomy เรายังไม่มี — **ไม่เพิ่มในใบนี้** เพราะยังไม่มีใครขอและไม่มีหลักฐานว่าแสดงไม่ได้ ต่างจาก `tool_calling` ที่ #50 พิสูจน์แล้วว่าไม่มีทางเลี่ยง

## Sources

[issue #50](https://github.com/monthop-gmail/agent-platform/issues/50) · [issue #46](https://github.com/monthop-gmail/agent-platform/issues/46) ข้อ 2 · [ADR-0009](0009-capability-model.md) `CapabilityScope` และกฎ *unknown = ไม่มี* · [ADR-0018](0018-policy-result-single-source.md) สองที่ที่ต้องตรงกันคือสองที่ที่จะไม่ตรงกัน · [`llm-gateway`](https://github.com/monthop-gmail/llm-gateway) tag `no-tools` และ `INTEGRATION.md` · `care-agent-platform` `platform-contract.yaml`
