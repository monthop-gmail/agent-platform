# capability/v1

## v1.1.0 — 2026-09-02

เพิ่ม `tool_calling` และตีพิมพ์ **แผนที่ id → scope ที่เป็นทางการ** ตาม [ADR-0024](../../../decisions/0024-tool-calling-and-canonical-scope.md) จาก [issue #50](https://github.com/monthop-gmail/agent-platform/issues/50)

* `CapabilityId` +1 — **`tool_calling`**
* `$defs.canonical_scope` — แผนที่ที่ทุก catalog ต้องยึด ห้ามตัดสินเอง

### `tool_calling` คนละเรื่องกับ `mcp` / `github` / `browser`

```text
tool_calling (provider)  →  model พูดภาษา tool call เป็นไหม
github · browser (tool)  →  มี tool อะไรให้เรียกบ้าง
```

model ที่ `tool_calling` ไม่ได้ **เรียก `github` ไม่ได้แม้ tool นั้นจะต่ออยู่** — สองอย่างนี้ไม่ทดแทนกัน · และเพราะ [ADR-0009](../../../decisions/0009-capability-model.md) บอกว่า *unknown = ไม่มี* consumer จึงตั้งชื่อเองแล้วใช้แทนไม่ได้เลย ต่างจากเคส `error/v1` ที่ยังมีทางเลี่ยงแบบไม่สวย

### แผนที่ scope — เติมสิ่งที่ขาด ไม่ใช่สร้างแนวคิดใหม่

`CapabilityScope` (`provider` · `host` · `tool`) **มีอยู่แล้วตั้งแต่ v1.0.0** พร้อมกฎว่า *"capability ตัวเดียวกันอยู่ได้แค่ scope เดียว"*

แต่ `scope` เป็น field ของแต่ละรายการใน catalog → **คนทำ catalog ตัดสินเอง** → กฎนั้นไม่มีอะไรทำให้จริง และวันนี้ยังไม่มีใครตอบได้ว่า `github` อยู่ scope ไหน (ทั้ง repo ยังไม่มี catalog instance เลยสักอัน)

| scope | capability |
| --- | --- |
| `provider` | `vision` · `long_context` · `streaming` · **`tool_calling`** |
| `host` | `code_execution` · `shell` · `filesystem` · `docker` · `network_egress` |
| `tool` | `git` · `github` · `browser` · `mcp` |
| `unscoped` | `autonomous_execution` |

⚠️ **`autonomous_execution` ไม่ใช่ความสามารถทางเทคนิค แต่เป็นระดับอำนาจ** จึงไม่เข้ากับสาม scope ที่ ADR-0009 นิยามไว้ · บันทึกเป็นข้อยกเว้นที่รู้แล้ว **ไม่ยัดเข้ากลุ่มใดกลุ่มหนึ่งเพื่อให้ตารางสวย**

### แผนที่ซ้ำกับ enum จึงมี check บังคับ

`drift_check` ข้อ 4b ตรวจว่า keys ทุกกลุ่มรวมกัน **== `CapabilityId` เป๊ะ** — ขาด · เกิน · ซ้ำ = แดง · **นี่คือครั้งแรกที่กฎ "ตัวเดียวกันอยู่ได้แค่ scope เดียว" ถูกบังคับด้วยเครื่อง**

### ไม่ breaking — และตรวจ consumer จริงแล้ว

13 ค่าเดิมไม่ขยับ · `canonical_scope` เป็นบล็อกอธิบาย ไม่ใช่ constraint

`care-agent-platform` เป็นรายเดียวที่ pin `capability/v1` และ manifest เขียนกำกับเองว่า *"ActionRisk — ผูกกับ capability ไม่ใช่กับ request"* · ค้นโค้ดแล้วไม่มีการใช้ค่า `CapabilityId` เลย — **ยืนยันจากไฟล์จริง ไม่ใช่จากการอนุมานว่า additive แล้วปลอดภัย**

## v1.0.0 — 2026-08-17
- ตั้งต้นตาม [ADR-0009](../../../decisions/0009-capability-model.md)
- 3 schema แยกกัน: `capability` (taxonomy) · `declaration` (ใครมีอะไร) · `requirement` (task ต้องการอะไร)
- taxonomy รอบแรก 13 ค่า · `ActionRisk` นิยามที่นี่ตาม [ADR-0010](../../../decisions/0010-risk-approval-taxonomy.md)
