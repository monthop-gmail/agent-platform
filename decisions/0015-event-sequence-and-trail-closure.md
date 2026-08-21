# ADR-0015: `event/v1` — ลำดับของ event และ trail ที่ถูกตัดท้าย

**Status:** Accepted (2026-08-21)
**Date:** 2026-08-21
**Depends on:** [ADR-0006](0006-contract-versioning.md) · [ADR-0011](0011-conformance-automation.md)
**Blocking:** [issue #23](https://github.com/monthop-gmail/agent-platform/issues/23) · `contracts/event/v1/event.schema.yaml`

## Context

consumer สองรายชนปัญหาที่ดูเหมือนอันเดียวกัน แล้วเสนอรูปที่**เข้ากันไม่ได้** — นี่เป็นครั้งแรกที่มีข้อขัดแย้งข้าม consumer จริง ๆ ไม่ใช่คำขอเพิ่ม field

| ราย | อาการ | รูปที่ขอ | ราคา |
| --- | --- | --- | --- |
| [`devfactory-core`](https://github.com/monthop-gmail/devfactory-core) | trail ที่ถูกตัดท้ายอ่านได้เหมือน trail ที่สมบูรณ์ | `sequence` **contiguous ต่อ subject** เริ่มที่ 1 ห้ามข้าม | ต้อง serialize การเขียนต่อ subject |
| [`care-agent-platform`](https://github.com/monthop-gmail/care-agent-platform) | `occurred_at` เท่ากันเป๊ะบน Postgres → เรียงไม่ได้ · `JOB_COMPLETED` โผล่ก่อน transition ของตัวเอง | `sequence` **monotonic ไม่ต้อง contiguous** | แทบไม่มี |

`care-agent-platform` ชี้ถูกแล้วว่าเป็น **การรับประกันคนละตัวสองอัน** ที่บังเอิญใช้ field เดียวกันได้ และเตือนว่า contiguous มีราคาที่คนที่ต้องการแค่ "เรียงถูก" ไม่ควรต้องจ่าย — ต้องล็อกแถวต่อ subject · ช่องว่างเกิดเองได้จาก transaction ที่ rollback ทำให้ "ช่องว่าง = ใบหาย" กลายเป็นสัญญาณลวง · และ producer หลายตัวต่อ subject เดียวกันจะกลายเป็นข้อบังคับให้มี coordinator กลาง

## ข้อค้นพบที่เปลี่ยนคำตอบ — contiguous ไม่ได้ตอบคำถามที่ `devfactory-core` ถาม

ก่อนจะเลือกระหว่างสองรูป ต้องตรวจก่อนว่ารูปที่ขอ **แก้ปัญหาที่ยกมาได้จริงไหม** · มันแก้ไม่ได้

`sequence` ต่อ subject เป็นตัวจับ **ช่องว่างกลางทาง** ไม่ใช่ตัวจับ **ปลายที่ขาด**:

```text
ความจริง:      1 2 3 4 5
ผู้อ่านได้:     1 2 _ 4 5   →  ✅ จับได้ ใบ 3 หาย
ผู้อ่านได้:     1 2 3       →  ❌ จบที่ 3 หรือ 4,5 หาย — แยกไม่ออก
```

เลข sequence ที่ติดมากับ event **ไม่มีทางบอกว่าใบสุดท้ายควรเป็นเลขอะไร** เพราะคำตอบนั้นไม่ได้อยู่ในใบไหนเลย — ต้องมาจากคำแถลงที่อยู่นอกลำดับ (ใบปิดท้าย หรือ checkpoint) เท่านั้น

และ `devfactory-core` **มีตัวจับช่องว่างกลางทางอยู่แล้ว** — issue เขียนเองว่า replay ให้ `STATE_TRANSITION` ใบถัดไปยืนยันใบก่อนหน้าด้วย from→to ถ้าไม่ต่อกันแปลว่ามีใบหาย · contiguous sequence จึงเพิ่มการตรวจให้เฉพาะ event ที่ไม่ใช่ transition และ **ไม่แตะช่องที่เขาบอกว่าเป็นปัญหาเลย**

นี่เป็น failure mode เดียวกับที่ repo นี้เจอมาสามครั้ง ([#17](https://github.com/monthop-gmail/agent-platform/issues/17) · [PR #18](https://github.com/monthop-gmail/agent-platform/pull/18) · false-✅ ของ `drift_check`): **กลไกที่ดูเหมือนตอบคำถาม แต่จริง ๆ ตอบคำถามที่แคบกว่า** แล้วผลิตความมั่นใจปลอม — ถ้ารับ option contiguous ไปตรง ๆ เราจะ ship สิ่งที่ผู้ขอเชื่อว่าปิดช่องแล้วทั้งที่ยังเปิดอยู่ พร้อมราคาการ serialize ที่ทุกคนต้องจ่าย

`care-agent-platform` เห็นครึ่งหนึ่งของเรื่องนี้แล้วตอนปฏิเสธ `previous_event_id` — *"ตรวจใบท้ายหายไม่ได้เหมือนเดิม เพราะไม่มีอะไรบอกว่าปลายทางควรอยู่ตรงไหน สุดท้ายก็ยังต้องมี checkpoint หรือ counter อยู่ดี"* — เหตุผลเดียวกันนี้ล้มข้อเสนอ contiguous ด้วย แต่ไม่มีใครเอาไปใช้กับมัน

### สัญญาพูดเรื่องนี้ไว้แล้วในทางตรงข้าม

guarantee ข้อ 8 ของ `event/v1` (🔒 frozen เป็นของ `devfactory-core`):

> "trace ที่ไม่มี step ย่อยถือว่าถูกต้อง — execution ที่ไม่มี step event ไม่ได้แปลว่าไม่ได้ทำอะไร"

สัญญา**บอกอยู่แล้วว่าการไม่มี event ไม่ใช่หลักฐานว่าไม่มีเหตุการณ์** · การจะสรุปความครบถ้วนจากชุด event ที่ถืออยู่จึงขัดกับ guarantee ข้อนี้โดยตรง ไม่ว่าจะนับเลขดีแค่ไหน — ต้องมี **คำแถลงปิดท้าย** เท่านั้น

## จริง ๆ มีสามคำถาม ไม่ใช่หนึ่ง

| # | คำถาม | ใครต้องการ | ปิดด้วยอะไรจริง ๆ | ราคา |
| --- | --- | --- | --- | --- |
| 1 | **เรียงให้ถูกได้ไหม** | `care-agent-platform` (บั๊กจริงวันนี้) | `sequence` monotonic — ไม่ต้อง contiguous | แทบไม่มี |
| 2 | **มีใบหายกลางทางไหม** | `devfactory-core` (มีอยู่แล้วผ่าน from→to) | contiguous · หรือ chain | ต้อง serialize ต่อ subject |
| 3 | **ปลายขาดไปไหม** | `devfactory-core` (ช่องที่เปิดอยู่) | **ใบปิดท้าย** สำหรับ subject ที่จบแล้ว · **checkpoint** สำหรับ subject ที่ยังเดินอยู่ | — |

ข้อ 3 คือของจริงที่ต้องปิด และตารางของ `devfactory-core` เองชี้ทางไว้แล้ว:

| job จบแบบ | สถานะ | ปิดยังไง |
| --- | --- | --- |
| `COMPLETED` | ✅ จับได้อยู่แล้ว | `JOB_COMPLETED` ทำหน้าที่ใบปิดท้ายอยู่แล้ว |
| `FAILED` · `CANCELLED` · `TIMED_OUT` | ❌ ช่องเปิด | **ให้ทุกการจบแบบ terminal ออกใบปิดท้ายเหมือนกัน** — ไม่ต้องมี field ใหม่เลย |
| ยังเดินอยู่ (ไม่ terminal) | ❌ ช่องเปิด | **ปิดในสัญญาไม่ได้** — trail ที่ยังเดินอยู่ไม่มีปลายที่นิยามได้ · ต้องใช้ checkpoint/high-water mark ที่ชั้น store ไม่ใช่ field บน event |

แถวกลางเป็นสามในสี่ของปัญหา และปิดได้ด้วย **semantics ไม่ใช่ wire** — `RFC-0007` ของ `devfactory-core` เพิ่ม `CANCELLED` กับ `TIMED_OUT` เป็น terminal ระดับ job ไปแล้ว สิ่งที่ยังขาดคือกฎว่าทุก terminal ต้องมีใบปิด

## ขอบเขตอำนาจ — ครึ่งหนึ่งของเรื่องนี้ไม่ใช่ของเรา

`event/v1` เป็น **derived contract** ([ADR-0006 C2](0006-contract-versioning.md)):

| ของ `agent-platform` | ของ `devfactory-core` (🔒 frozen) |
| --- | --- |
| มี field ชื่อ `sequence` · type · ขอบเขตของค่า · version | **"ลำดับต้องต่อเนื่อง"** · **"ทุก terminal ต้องมีใบปิด"** · **"ช่องว่างแปลว่ามีใบหาย"** |

ประโยคขวามือทั้งหมดคือ **guarantee ใหม่** ซึ่ง Rule 2 ของ [RFC-0005](https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/0005-platform-contract-authority.md) ให้เป็นของต้นทาง · เราเพิ่ม field ได้เอง แต่ **ประกาศการรับประกันแทนเขาไม่ได้** — และการ ship field ที่ผู้อ่านเข้าใจว่ามาพร้อมการรับประกันซึ่งไม่มีใครรับรอง แย่กว่าไม่ ship

### `required` ไม่ได้ในเวอร์ชันนี้

[ADR-0006 นิยาม breaking change](0006-contract-versioning.md) ระบุ **"เพิ่ม required field ใหม่"** ไว้ในลิสต์ breaking ตรง ๆ · `sequence` ที่บังคับต้องขึ้น `event/v2` และทำให้ payload เดิมทุกใบ invalid — ซึ่งไม่คุ้มกับการปิดข้อ 1 ที่ optional ก็พอ

## ช่องว่างที่ทั้งสองข้อเสนอมองข้าม — `event/v1` ไม่มีตัวตนของผู้ผลิต

ข้อเสนอของ `care-agent-platform` พูดถึง *"monotonic ต่อ producer"* และ *"contiguous เป็นคุณสมบัติที่ producer ประกาศ"* — แต่ `event/v1` **ไม่มี field ที่บอกว่าใครเป็นผู้ผลิต** · `source` มีแค่ `kind: internal | external` และ `system` (ชื่อระบบต้นทางสำหรับ external เท่านั้น) · process สองตัวในระบบเดียวกันแยกกันไม่ออก ซึ่งเป็นเคสของ `care-agent-platform` เอง (HTTP request กับ worker เขียน event ของผู้ป่วยคนเดียวกันพร้อมกัน)

แปลว่า **การรับประกันระดับ producer ยังเขียนลงสัญญาไม่ได้วันนี้** ไม่ว่าจะเลือกทางไหน — ถ้าจะไปทางนั้นต้องเพิ่มตัวตนของผู้ผลิตก่อน ซึ่งเป็นงานคนละชิ้น

## Options

### A. `sequence` contiguous ต่อ subject (ตามที่ `devfactory-core` เสนอ)

* ✅ ปิดช่องว่างกลางทางสำหรับ event ทุกชนิด ไม่ใช่แค่ transition
* ❌ **ไม่ปิดปลายที่ขาด ซึ่งเป็นปัญหาที่ยกมา** — ดูข้อค้นพบข้างบน
* ❌ บังคับให้ทุก consumer serialize การเขียนต่อ subject รวมรายที่ไม่ต้องการการตรวจนี้
* ❌ transaction ที่ rollback สร้างช่องว่างโดยไม่มีใครทำผิด → สัญญาณลวง แล้วคนจะเลิกเชื่อสัญญาณ
* ❌ ต้องประกาศ guarantee ใหม่ ("ห้ามข้าม") ซึ่งเป็นของต้นทาง

### B. `sequence` monotonic + `contiguous` เป็นคุณสมบัติที่ producer ประกาศ (ตามที่ `care-agent-platform` เสนอ)

* ✅ แยกสองการรับประกันออกจากกันถูกต้อง · คนที่ต้องการแค่เรียงไม่ต้องจ่ายค่า serialize
* ✅ `devfactory-core` ยังตรวจได้เต็มที่ในระบบที่มี producer เดียวต่อ subject
* ❌ **ประกาศที่ไหน** — `event/v1` ไม่มีตัวตนของผู้ผลิต ต้องเพิ่มก่อน (ดูข้างบน)
* ❌ ยังไม่ปิดปลายที่ขาดอยู่ดี — contiguous ที่ประกาศแล้วก็ยังเป็นตัวจับช่องว่างกลางทาง
* ⚠️ ครึ่งแรก (monotonic) ถูกต้องและควรทำ · ครึ่งหลังยังไม่พร้อม

### C. แยกสามชั้น — ship เฉพาะชั้นที่เป็นของเราและพร้อมแล้ว ⭐

1. **ที่นี่ ตอนนี้:** `sequence` เป็น optional integer · **monotonic เข้มงวดภายใน subject จากผู้ผลิตเดียวกัน · ไม่รับประกันความต่อเนื่อง** · ผู้อ่านเรียงด้วย `(occurred_at, sequence)` · เขียนลง `platform_rules` ตรง ๆ ว่า **ช่องว่างไม่มีความหมาย ห้ามตีความว่ามีใบหาย**
2. **ขอ RFC ที่ `devfactory-core`:** ทุกการจบแบบ terminal (`FAILED` · `CANCELLED` · `TIMED_OUT`) ต้องออกใบปิดท้ายเหมือนที่ `COMPLETED` ทำ — ปิดสามในสี่แถวของตารางเขาโดยไม่ต้องมี field ใหม่ และเป็น semantics ที่เป็นของเขาชัดเจน
3. **บันทึกว่าปิดในสัญญาไม่ได้:** trail ที่ยังเดินอยู่ไม่มีปลายที่นิยามได้ · ต้องใช้ checkpoint ที่ชั้น store — เป็นเรื่องของ API/store ไม่ใช่ของ `event/v1`

* ✅ ปิดบั๊กที่มีอยู่จริงวันนี้ (การเรียงของ `care-agent-platform`) ทันที ด้วยของที่เป็นของเราล้วน ๆ
* ✅ ไม่ ship การรับประกันที่เราไม่มีอำนาจให้ และไม่ ship กลไกที่ตอบคำถามแคบกว่าที่ผู้ใช้เข้าใจ
* ✅ ชี้ทางปิดข้อ 3 ที่ **ถูกกว่าและได้ผลกว่า** ทั้งสองข้อเสนอ
* ❌ `devfactory-core` ยังไม่ได้สิ่งที่ขอในรอบนี้ — ได้คำตอบว่าทำไมสิ่งที่ขอไม่พอ กับทางที่พอแทน
* ❌ ต้องรอ RFC ที่ต้นทางก่อนถึงจะปิดข้อ 3 ได้จริง

### D. ไม่เพิ่ม field เลย — ปิดทุกอย่างด้วยใบปิดท้าย + checkpoint

* ✅ ตรงเป้าที่สุดสำหรับข้อ 3 · ไม่แตะ wire เลย
* ❌ **ทิ้งบั๊กที่มีอยู่จริงไว้** — `care-agent-platform` เรียง event ที่ `occurred_at` เท่ากันไม่ได้ และนั่นไม่ใช่เรื่องความครบถ้วน แต่เป็นเรื่องการอ่าน trail ให้ถูกเลย
* ❌ ผลักให้แต่ละ consumer คิด tiebreaker ของตัวเอง → trail ข้าม consumer เชื่อกันไม่ได้ ซึ่งเป็นเหตุผลที่ issue เปิดมาที่นี่แต่แรก

### E. `previous_event_id` chain

* ✅ จับใบหายกลางทางแม่นกว่าเลขลำดับ
* ❌ ไม่ปิดปลายที่ขาด (`care-agent-platform` วิเคราะห์ไว้แล้วและถูกต้อง)
* ❌ บังคับให้ผู้ผลิตอ่านใบล่าสุดของ subject ก่อนเขียนทุกครั้ง = ราคาเท่า contiguous

### F. `sequence` เป็น required → `event/v2`

* ✅ ผู้อ่านพึ่งได้เสมอ ไม่ต้องเขียนโค้ดสองทาง
* ❌ payload เดิมทุกใบ invalid · consumer ทั้งสองรายต้อง migrate พร้อมกัน · เป็น breaking ตาม ADR-0006 ตรง ๆ
* ❌ ราคาสูงเกินไปสำหรับ field ที่ optional ก็ปิดบั๊กได้

## Decision

**C** — แยกสามชั้น · ship เฉพาะชั้นที่เป็นของเราและพร้อมแล้ว

**Reason:** ก่อนเลือกระหว่างสองรูปที่ consumer เสนอ ต้องตอบก่อนว่ารูปไหนแก้ปัญหาได้จริง — และคำตอบคือ **ไม่มีรูปไหนปิดปลายที่ขาดได้** เพราะเลขที่ติดมากับ event บอกไม่ได้ว่าใบสุดท้ายควรเป็นเลขอะไร · การรับ option A ไปคือการ ship ความมั่นใจปลอมพร้อมราคาที่ทุกคนต้องจ่าย ซึ่งเป็นความผิดพลาดแบบเดียวกับ false-✅ ของ `drift_check` ที่ repo นี้เจอมาสามครั้ง · ครึ่งที่ปิดได้จริงวันนี้คือการเรียง ซึ่งเป็น wire ล้วนและเป็นของเรา · ส่วนความครบถ้วนปิดด้วย **ใบปิดท้ายทุก terminal** ซึ่งถูกกว่า ได้ผลกว่า และเป็น semantics ของ `devfactory-core` ที่ต้องมี RFC ที่ต้นทางตาม ADR-0006 — เราประกาศแทนเขาไม่ได้

**Authority:** Monthop Champaruang — Platform Owner / Architecture Authority of `agent-platform`

### รูปของ field

```yaml
sequence:
  type: integer
  minimum: 1
  description: >-
    ลำดับสำหรับ **เรียง** event ภายใน subject เดียวกันจากผู้ผลิตเดียวกัน
    เพิ่มขึ้นเสมอ · ผู้อ่านเรียงด้วย (occurred_at, sequence)
    ⚠️ ไม่รับประกันความต่อเนื่อง — ช่องว่างไม่ได้แปลว่ามีใบหาย
```

เพิ่ม `platform_rules` สองข้อ:

* `"sequence ใช้เรียงเท่านั้น — ช่องว่างไม่มีความหมาย ห้ามตีความว่ามีใบหาย"`
* `"event ที่ไม่มี sequence เรียงด้วย occurred_at อย่างเดียว — ห้ามถือว่าอยู่ก่อนหรือหลังใบที่มี"`

ข้อหลังกันกรณีที่ producer เก่ากับใหม่เขียนปนกันระหว่าง migrate

**`guarantees` ไม่ขยับแม้แต่ตัวอักษรเดียว** · `derived_from.semantics_version` ยัง `"1.1"`

### ไม่ bump major — อยู่ใน `v1` เดิม

| เกณฑ์ breaking ของ [ADR-0006](0006-contract-versioning.md) | การเปลี่ยนนี้ |
| --- | --- |
| ลบ field · เปลี่ยนชื่อ field · เปลี่ยน type | ❌ ไม่มี field เดิมถูกแตะ |
| เพิ่ม required field ใหม่ · optional → required | ❌ `required` ยัง 7 ตัวเท่าเดิม |
| ลบค่าออกจาก enum · เปลี่ยนความหมายของค่าเดิม | ❌ `EventType` และ `SubjectType` ไม่ขยับ |
| เปลี่ยน default ที่ทำให้พฤติกรรมเดิมเปลี่ยน | ❌ ไม่มี default · ไม่มี `sequence` = เรียงด้วย `occurred_at` เหมือนเดิม |
| เข้มขึ้นใน validation | ❌ ผ่อนอย่างเดียว |

→ `v1.3.0` ใน `CHANGELOG.md` — **ไม่ใช่ `v1.2.0`** เพราะ CHANGELOG ของ `event/v1` มีเลขซ้ำค้างอยู่ (`v1.1.0` สองอัน · 08-18 กับ 08-19) แก้เลขและเรียงใหม่ในคอมมิตเดียวกัน — ไม่มีใคร pin ด้วย semver ของ contract จึงไม่กระทบ

## Consequences

* `contracts/event/v1/event.schema.yaml` เพิ่ม `sequence` + `platform_rules` 2 ข้อ · `CHANGELOG.md` → `v1.3.0` (พร้อมแก้เลขซ้ำที่ค้างอยู่)
* `care-agent-platform` ย้าย `sequence_no` ของตัวเองมาใช้ชื่อกลาง — บั๊กการเรียงบน Postgres ปิดโดยไม่ต้อง serialize อะไร
* **ต้องเปิดเรื่องที่ `devfactory-core`** ขอ RFC สำหรับ "ทุกการจบแบบ terminal ต้องออกใบปิดท้าย" — ถ้าไม่เปิด ข้อ 3 จะค้างเงียบ ๆ และ issue #23 จะถูกปิดทั้งที่ยังไม่ได้แก้สิ่งที่เขาถาม
* **`event/v1` ยังไม่มีตัวตนของผู้ผลิต** — การรับประกันระดับ producer (รวม option B ครึ่งหลัง) เขียนลงสัญญาไม่ได้จนกว่าจะเพิ่ม · บันทึกไว้ ไม่ทำในรอบนี้
* trail ของ subject ที่ยังเดินอยู่ **ตรวจความครบถ้วนไม่ได้ด้วย `event/v1`** ไม่ว่ารูปไหน — เป็นข้อจำกัดของสัญญา ไม่ใช่ของ implementation · เขียนไว้ให้คนที่มาถามซ้ำอ่านเจอ
* **drift check ตรวจข้อนี้ไม่ได้** — ตรวจได้แค่ว่า schema ยัง valid · "monotonic" กับ "ช่องว่างไม่มีความหมาย" พิสูจน์ได้จาก payload จริงของ consumer เท่านั้น ตามขอบเขตที่ [ADR-0011](0011-conformance-automation.md) วางไว้
* ADR-0014 ฝากช่องว่างเรื่อง **event ที่บันทึกว่าเงื่อนไข consent ถูกประเมินแล้ว** ไว้กับ issue นี้ — ยังไม่ปิดในรอบนี้ เพราะเป็นเรื่องเนื้อหาของ event ไม่ใช่ลำดับ · ย้ายไปเป็นงานของตัวเองหลัง #23 ปิด

## Sources

[issue #23](https://github.com/monthop-gmail/agent-platform/issues/23) + คอมเมนต์ของ `care-agent-platform` · [devfactory-core#7](https://github.com/monthop-gmail/devfactory-core/issues/7) (end-to-end simulation + replay) · [care-agent-platform PR #9](https://github.com/monthop-gmail/care-agent-platform/pull/9) (`sequence_no`) · [RFC-0005](https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/0005-platform-contract-authority.md) Rule 2 · [RFC-0007](https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/0007-job-lifecycle-completeness.md) (terminal states) · `event/v1` guarantee ข้อ 8
