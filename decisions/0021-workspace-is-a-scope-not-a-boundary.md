# ADR-0021: `workspace_id` เป็น **ขอบเขตอนุญาต** ไม่ใช่ **กำแพง** — ต่างจาก `tenant_id` ตรงไหน

**Status:** Accepted (2026-08-22)
**Date:** 2026-08-22
**Depends on:** [ADR-0007](0007-multi-tenancy.md) · [ADR-0010](0010-risk-approval-taxonomy.md) · [ADR-0012](0012-consent-contract.md)
**Blocking:** [enterprise-knowledge#23](https://github.com/monthop-gmail/enterprise-knowledge/issues/23) ซึ่งบล็อก `schema.sql` ของเขาอยู่

## Context

`enterprise-knowledge` เปิด [#23](https://github.com/monthop-gmail/enterprise-knowledge/issues/23) ถามสามข้อก่อนจะเขียนแถวจริงลง `schema.sql` — และบอกตรง ๆ ว่าเคาะช้าแล้วต้องรื้อ เพราะกระทบ `ScopePredicate`, fixture ทั้งชุด และ **security boundary**

**สองในสามข้อ ADR-0007 ตอบไว้แล้ว** — ต้องชี้ให้เห็น ไม่ใช่ตัดสินใหม่:

| คำถามของเขา | คำตอบที่มีอยู่แล้ว |
| --- | --- |
| knowledge plane ต้องมี `workspace_id` ไหม | ✅ **ต้องมี** — [ADR-0007 Consequences](0007-multi-tenancy.md) เขียนว่า *"`workspace_id` required สำหรับ **execution/knowledge/tool** · optional สำหรับ event ระดับ tenant"* |
| `department` เป็น metadata filter ได้ไหม | ❌ **ไม่ได้** — ADR-0007 และตารางศัพท์ที่ lock ไว้ระบุว่า `Project`/`Department` เป็น **label ของ workspace** · `identity/v1` `WorkspaceId` ก็เขียนกำกับไว้เอง |

ข้อที่สาม — **`workspace_id` เข้มเท่า `tenant_id` หรือเปล่า** — **ยังไม่มีใครเคาะ** และเป็นเหตุผลที่ ADR ฉบับนี้มีอยู่

## ทำไมข้อนี้ยังเปิดอยู่ — ADR-0007 พูดสองอย่างที่ต้องอ่านคู่กัน

ในไฟล์เดียวกัน:

> `tenant_id` — "ขอบเขต isolation **แข็ง** — ห้ามข้ามเด็ดขาด (DB/index/storage แยกได้)"
> `workspace_id` — "ขอบเขตงาน — agent, knowledge, tool, policy อยู่ใน workspace"
> เหตุผลที่เลือก A — "2 ชั้นพอสำหรับ isolation จริง (**tenant = boundary, workspace = grouping**)"

แต่เหตุผลที่ **ปฏิเสธ option C** (แบน ไม่มี workspace) คือ:

> "ไม่มีที่ให้แบ่งงาน/ทีมภายใน tenant เดียวกัน → **ทีมหนึ่งเห็น knowledge อีกทีมทั้งหมด**"

อ่านคู่กันแล้วได้ข้อจำกัดสองข้อที่ต้องเป็นจริงพร้อมกัน:

```text
ถ้า workspace ไม่บังคับอะไรเลย   → การปฏิเสธ option C ไม่มีความหมาย
ถ้า workspace แข็งเท่า tenant     → มีสองกำแพงที่เหมือนกัน แล้วทำไมต้องมีสองชั้น
```

คำตอบที่ทำให้ทั้งสองประโยคจริงพร้อมกันมีทางเดียว: **สองชั้นนี้ต่างกันที่ "ข้ามได้ไหมถ้ามีคนอนุญาต" ไม่ใช่ที่ "เข้มแค่ไหน"**

## คำวินิจฉัยที่เสนอ

| | `tenant_id` | `workspace_id` |
| --- | --- | --- |
| ข้ามได้ไหม | **ไม่ได้ทุกกรณี** — ไม่มี policy · ไม่มี consent · ไม่มี admin คนไหนอนุญาตได้ | **ปฏิเสธโดยปริยาย แต่อนุญาตได้** ผ่าน `policy/v1` (และ `consent/v1` ถ้าเป็นข้อมูลส่วนบุคคล) |
| บังคับที่ชั้นไหน | **ชั้นเก็บข้อมูล** — RLS / partition / index · โค้ดแอปข้ามไม่ได้แม้เขียนผิด | **ชั้นตรวจสิทธิ์** — ทุก query ถูก scope โดยปริยาย การขยายต้องผ่านการตัดสิน |
| ผิดแล้วเป็นอะไร | bug ระดับความปลอดภัย — **reject ไม่ใช่ coerce** | การเข้าถึงที่ไม่ได้รับอนุญาต — deny แล้วบันทึก |
| ต้อง audit ไหม | การพยายามข้าม = เหตุการณ์ที่ต้องบันทึกเสมอ | **การข้ามที่สำเร็จต้องบันทึกเสมอ** ว่าอนุญาตด้วยอะไร |

แถวสุดท้ายคือหัวใจ — ถ้า cross-workspace ทำได้เงียบ ๆ มันก็ไม่ต่างจากไม่มี workspace

## Options

### A. `workspace_id` แข็งเท่า `tenant_id` — ข้ามไม่ได้ทุกกรณี

* ✅ ง่ายที่สุดในการ implement — บังคับที่ชั้นเก็บข้อมูลเหมือนกันทั้งคู่
* ✅ ไม่มีทางรั่วจากการเขียน policy ผิด
* ❌ **แชร์ knowledge ข้ามทีมใน org เดียวกันไม่ได้เลย** ซึ่งเป็นความต้องการปกติ (คู่มือกลาง · นโยบายบริษัท · ฐานความรู้ที่ทุกแผนกใช้)
* ❌ ถ้าสองชั้นข้ามไม่ได้เหมือนกัน **ก็ไม่มีเหตุผลที่ต้องมีสองชั้น** — ขัดกับเหตุผลที่ ADR-0007 เลือก A แทน B
* ❌ ทีมจะเลี่ยงด้วยการทำสำเนาข้ามหลาย workspace ซึ่งแย่กว่า — สำเนาที่ drift ได้และเพิกถอนไม่ได้

### B. **ปฏิเสธโดยปริยาย · อนุญาตได้ผ่านการตัดสินที่บันทึกไว้** ⭐

* ✅ ทำให้ทั้งสองประโยคใน ADR-0007 จริงพร้อมกัน — ทีมหนึ่งไม่เห็น knowledge อีกทีมโดยอัตโนมัติ แต่สองชั้นไม่ซ้ำซ้อน
* ✅ ใช้กลไกที่มีอยู่แล้วทั้งหมด — `policy/v1` ตอบ *"identity นี้ทำ action นี้ได้ไหม"* · `consent/v1` ตอบ *"กับข้อมูลของใคร"* · `event/v1` บันทึกว่าเกิดขึ้น · **ไม่ต้องสร้าง contract ใหม่**
* ✅ ตรงกับที่ `care-agent-platform` ทำอยู่แล้วโดยไม่รู้ตัว — องค์กรภายนอกเข้าถึงข้อมูลได้ผ่าน consent ไม่ใช่ผ่านการเป็น tenant ([ADR-0010 ของเขา](https://github.com/monthop-gmail/care-agent-platform/blob/main/decisions/0010-organizations-are-not-tenants.md))
* ❌ **รั่วได้ถ้าเขียน policy ผิด** — ต่างจาก tenant ที่ผิดยังไงก็ไม่รั่วเพราะ DB กั้นให้
* ❌ implement แพงกว่า A — ต้องมีทางตรวจสิทธิ์จริง ไม่ใช่แค่ `WHERE workspace_id = ?`

### C. `workspace` เป็น label เฉย ๆ ไม่บังคับอะไร — application เลือกใช้เอง

* ✅ ถูกที่สุด
* ❌ **ทำให้การปฏิเสธ option C ของ ADR-0007 ไม่มีความหมาย** — ทีมหนึ่งเห็น knowledge อีกทีมทั้งหมด ซึ่งเป็นเหตุผลเดียวที่ workspace ถูกสร้างขึ้นมา
* ❌ `identity/v1` `WorkspaceId` เขียนไว้เองว่า *"agent, knowledge, tool, policy **อยู่ใน** workspace"* — ไม่ใช่ *"มี label เป็น workspace"*

### D. ปล่อยให้แต่ละ repo ตัดสินเอง

* ❌ `care-agent-platform` บังคับ tenant ด้วย RLS · `enterprise-knowledge` จะทำอีกแบบ · แล้ว policy กับ audit trail ข้าม repo จะเทียบกันไม่ได้
* ❌ เป็นคำถามเรื่อง **security boundary** — ปล่อยให้ต่างคนต่างตีความคือวิธีที่ช่องโหว่เกิดโดยไม่มีใครตั้งใจ

## Decision

**B** — `workspace_id` ปฏิเสธโดยปริยาย · ข้ามได้ผ่านการตัดสินที่บันทึกไว้ · บังคับที่ชั้นตรวจสิทธิ์ ไม่ใช่ชั้นเก็บข้อมูล

**Reason:** เป็นคำตอบเดียวที่ทำให้ทั้งสองประโยคใน ADR-0007 จริงพร้อมกัน — *"workspace = grouping"* กับ *"ไม่มี workspace แล้วทีมหนึ่งเห็น knowledge อีกทีมทั้งหมด"* · ความต่างระหว่างสองชั้นไม่ได้อยู่ที่ความเข้ม แต่อยู่ที่ **มีใครอนุญาตให้ข้ามได้ไหม** — tenant ไม่มี · workspace มี และการอนุญาตนั้นต้องผ่านกลไกที่บันทึกไว้ · ปฏิเสธ A เพราะถ้าสองชั้นข้ามไม่ได้เหมือนกันก็ไม่มีเหตุผลที่ต้องมีสองชั้น และจะผลักให้ทีมทำสำเนาข้าม workspace ซึ่งแย่กว่าปัญหาเดิม · ปฏิเสธ C เพราะทำให้เหตุผลที่ ADR-0007 ปฏิเสธ option C หายไปทั้งหมด

**Authority:** Monthop Champaruang — Platform Owner / Architecture Authority of `agent-platform`

### สิ่งที่ตามมาโดยตรงสำหรับ `enterprise-knowledge`

ตอบคำถามทั้งสามข้อของ [#23](https://github.com/monthop-gmail/enterprise-knowledge/issues/23):

1. **ต้องมี `workspace_id` ตั้งแต่แรก** — ADR-0007 ตอบไว้แล้ว ไม่ใช่เรื่องใหม่ · ทางเลือกที่ 2 ของเขา (ใส่เลยตอนนี้) คือทางที่สัญญากำหนดอยู่แล้ว
2. **ไม่เท่ากับ tenant** — `tenant_id` บังคับที่ชั้นเก็บข้อมูล (RLS/partition) · `workspace_id` บังคับที่ชั้นตรวจสิทธิ์ แบบ deny-by-default ที่ขยายได้ด้วยการตัดสินที่บันทึกไว้
3. **`department` เป็น label ของ workspace** ไม่ใช่ metadata อิสระ — และ **metadata filter ที่ลอยอยู่โดยไม่มี workspace คือชั้นที่สามที่ ADR-0007 ห้ามไว้ ในชื่ออื่น**

⚠️ **ทางเลือกที่ 3 ของเขา (`workspace_id` nullable ก่อน) ใช้ไม่ได้** — ขัดทั้ง ADR-0007 ที่ระบุว่า required สำหรับ knowledge และขัด §25 ของเขาเองที่ห้ามให้ scope filter เป็น optional ใน production path · เขาเขียนข้อกังวลนี้ไว้เองแล้วและถูกต้อง

### ผลต่อ contract

**ไม่มี field ใหม่ ไม่มี contract ใหม่** — กลไกครบอยู่แล้ว · สิ่งที่ต้องเปลี่ยนคือ**คำอธิบายให้คนอ่านเจอกฎนี้ตรงที่เขาอ่าน**:

| ไฟล์ | เปลี่ยนอะไร |
| --- | --- |
| `contracts/identity/v1` `WorkspaceId` | เขียนให้ชัดว่าเป็น deny-by-default ที่ขยายได้ผ่าน `policy/v1` และการข้ามที่สำเร็จต้องบันทึก · ต่างจาก `TenantId` ที่ข้ามไม่ได้ทุกกรณี |
| `planes/knowledge.md` | เพิ่มกฎการ scope — วันนี้พูดถึงแต่ tenant |

`identity/v1` **ไม่มี field เปลี่ยน** — เป็นการเขียนความหมายที่ ADR-0007 ตัดสินไว้แล้วให้ชัดขึ้น จึงเป็น `v1.1.0` ไม่ใช่ major

## Consequences

* `enterprise-knowledge` ปลดบล็อก Phase 1 ได้ทันที และรู้ว่าต้องบังคับ workspace ที่ชั้นไหน (ไม่ใช่ชั้นเดียวกับ tenant)
* **การข้าม workspace ที่สำเร็จต้องออก audit event เสมอ** — ใช้ `policy/v1` `Decision` + `event/v1` ที่มีอยู่ ไม่ต้องมีอะไรใหม่
* `care-agent-platform` ไม่กระทบ — เขาบังคับ tenant ด้วย RLS อยู่แล้วซึ่งเป็นชั้นที่แข็งกว่า และ `care_organization` ของเขาเป็น record ในโดเมน ไม่ใช่ workspace
* `devfactory-core` ไม่กระทบ — `workspace_id` optional สำหรับ event ระดับ tenant ตาม ADR-0007 เดิม
* **drift check ตรวจข้อนี้ไม่ได้** — เป็นกฎว่าบังคับที่ชั้นไหน ซึ่งพิสูจน์ได้จากเทสของ consumer ที่รันจริงเท่านั้น (แบบเดียวกับ RLS ของ `care-agent-platform` ที่มีเทส 65 ตัว)
* ยังไม่ปิด: **ยังไม่มี `knowledge/v1` contract** — เกณฑ์ ADR-0012 ข้อ 2 กับ 3 ยังไม่ครบ · ADR นี้ตอบเรื่อง scope ไม่ได้ทำให้ contract เกิด

## Sources

[enterprise-knowledge#23](https://github.com/monthop-gmail/enterprise-knowledge/issues/23) · [ADR-0007](0007-multi-tenancy.md) Decision + Consequences + เหตุผลที่ปฏิเสธ option C · `identity/v1` `$defs.TenantId` / `$defs.WorkspaceId` · ตารางศัพท์ที่ lock ใน [`README.md`](README.md) แถว `Project`/`Department` · [care-agent-platform ADR-0010](https://github.com/monthop-gmail/care-agent-platform/blob/main/decisions/0010-organizations-are-not-tenants.md)
