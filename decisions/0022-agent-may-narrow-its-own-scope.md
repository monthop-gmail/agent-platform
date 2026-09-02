# ADR-0022: กฎ "สามฝ่ายตกลงตรงกัน" ให้ฝ่าย agent พูดได้ครึ่งเดียว

**Status:** Accepted (2026-09-02)
**Date:** 2026-09-02
**Depends on:** [ADR-0009](0009-capability-model.md) · [ADR-0010](0010-risk-approval-taxonomy.md) · [ADR-0021](0021-workspace-is-a-scope-not-a-boundary.md)
**Blocking:** [issue #47](https://github.com/monthop-gmail/agent-platform/issues/47) · `contracts/agent/v1`

## Context

`contracts/profile/v1/profile.schema.yaml` เขียนกฎไว้เองว่า:

> "สิทธิ์จริงคือส่วนที่ profile, agent และ policy ของ tenant ตกลงตรงกัน**ทั้งสามฝ่าย** ค่าที่กว้างที่สุดชนะไม่ได้"

แต่ไล่ `agent/v1` ครบทุก field แล้ว ฝ่าย agent มีที่ให้เขียนแค่สามอย่าง และ **ทั้งสามอย่างคือการขอ**:

| field | ความหมายตาม schema |
| --- | --- |
| `tools` | *"tool ที่ agent นี้ **ขอ** ใช้ — การอนุญาตจริงเป็นของ policy"* |
| `capability_requirement` | สิ่งที่ agent **ต้องการ** |
| `policy_profile` | **ชื่อ** ของเพดานที่ใช้ — ไม่ใช่เนื้อหา |

**ไม่มี field ไหนให้เขียนว่า "ถึงเพดานจะเปิดให้ แต่ agent ตัวนี้ห้ามแตะ"**

```text
กฎบอก:     สิทธิ์จริง = profile ∩ agent ∩ tenant policy
schema ให้:  profile กับ tenant policy ลดได้ · agent ขอได้อย่างเดียว
        ↓
"สามฝ่าย" จริง ๆ คือสองฝ่าย บวกผู้ยื่นคำขอ
```

นี่เป็นแผลชนิดเดียวกับที่ repo นี้เจอมาแล้วสี่ครั้ง — **กฎที่บังคับสิ่งที่ schema ไม่มีที่ให้ทำตาม** ([#22](https://github.com/monthop-gmail/agent-platform/issues/22) ไม่มี field อ้างใบเดิม · [ADR-0016](0016-recording-which-consent-allowed-access.md) ไม่มีที่บันทึกใบยินยอม · [ADR-0019](0019-execution-records-its-approval.md) ไม่มีที่ชี้ใบอนุมัติ · [ADR-0020](0020-consent-event-vocabulary.md) ไม่มีชื่อ event) — **ครั้งนี้คือครั้งที่ห้า**

เจอโดย [`agent-builder-dsh-poc`](https://github.com/monthop-gmail/agent-builder-dsh-poc) ที่ manifest มี `policy: { forbidden: [...] }` และ `humanApproval: { required: [...] }` อยู่แล้ว แล้ว **ไม่มีที่ลงใน `agent/v1`**

## "ไม่ได้ขอ" ไม่เท่ากับ "ห้าม" — และนี่คือเหตุผลที่ field ใหม่จำเป็นจริง

ข้อโต้แย้งที่ต้องตอบก่อน: *ถ้า agent ไม่อยากใช้ tool ไหน ก็ไม่ต้องใส่ใน `tools` สิ — intersection จัดการให้เอง*

ใช้ไม่ได้ด้วยสองเหตุผล:

1. **`agent/v1` มี `mcp_servers`** ซึ่งเป็นรายการ id ของ server — **tool ที่มาจาก MCP server ไม่ได้ถูกแจกแจงใน `tools`** · agent จึงได้ tool ที่ไม่เคยระบุมาโดยไม่มีทางปฏิเสธ
2. **การไม่ใส่ แยกไม่ออกจากการลืมใส่** · deny ที่เขียนไว้ชัดคือคำแถลงที่ตรวจได้ ส่วนความว่างเปล่าไม่ใช่คำแถลงอะไรเลย — เป็นหลักเดียวกับที่ `consent/v1` ห้าม `conditions: []` และที่ `event/v1` เขียนว่าช่องว่างของ `sequence` ไม่มีความหมาย

## Options

### A. เพิ่มบล็อก `policy` ที่ **ตัดออกได้อย่างเดียว** ⭐

```yaml
policy:                       # optional · deny-only ตามนิยาม
  deny_tools:        [github.pr.merge]
  deny_capabilities: [shell]
  require_human_for: [github.pr.comment]
```

ชื่อ field ข้างในตรงกับ `profile/v1.policy` ที่มีอยู่แล้ว (`deny_capabilities` · `require_human_for`) การรวมจึงเป็น union ตรง ๆ ไม่ต้องแปลงศัพท์

* ✅ ปิดช่องว่างระหว่างกฎกับ schema โดยไม่แตะกฎ
* ✅ **ปลอดภัยโดยโครงสร้าง ไม่ใช่โดยวินัย** — ไม่มี `allow` ให้เขียน agent จึงผ่อนข้อจำกัดของ tenant ไม่ได้แม้อยากทำ
* ✅ additive ล้วน — `agent/v1` ยังไม่มีใคร pin (ตรวจใน [`consumers.md`](../architecture/consumers.md) แล้ว) และ payload เดิมยัง valid
* ❌ คำว่า `policy` ปรากฏใกล้กันสามที่ — `policy/v1` (contract) · `agent.policy_profile` (ชื่อเพดาน) · `agent.policy` (ข้อจำกัดของตัวเอง)

### B. เหมือน A แต่ตั้งชื่อบล็อกว่า `restrictions`

* ✅ อ่านแล้วรู้ทันทีว่าตัดออกอย่างเดียว ไม่ต้องอ่าน description
* ✅ เลี่ยงคำว่า `policy` ที่ชนกันสามที่ ([ADR-0017](0017-the-word-subject.md) เพิ่งสอนว่าคำเดียวหลายความหมายราคาแพง)
* ❌ ชื่อนอกต่างจาก `profile/v1.policy` ทั้งที่ **ชื่อข้างในเหมือนกันและต้อง union กัน** — คนที่อ่านสองไฟล์เรียงกันจะไม่เห็นว่ามันรวมกัน ซึ่งเป็นความเสี่ยงที่ตรงข้ามกับที่ ADR-0017 กัน
* ❌ `require_human_for` ไม่ใช่การ "restrict" ตรง ๆ แต่เป็นการยกระดับผู้ตัดสิน — ชื่อกล่องจะพาให้เข้าใจแคบไป

### C. ไม่เพิ่ม field — ให้ agent ลดขอบเขตด้วยการไม่ใส่ใน `tools`

* ✅ ไม่แตะสัญญาเลย
* ❌ **`mcp_servers` ทำให้ใช้ไม่ได้** — tool จาก MCP ไม่ได้อยู่ใน `tools` ตั้งแต่แรก
* ❌ การไม่ใส่แยกไม่ออกจากการลืมใส่
* ❌ ไม่มีทางแสดง `require_human_for` ได้เลยไม่ว่าจะเขียน `tools` อย่างไร

### D. เพิ่มทั้ง `allow` และ `deny` ฝั่ง agent

* ✅ ยืดหยุ่นที่สุด
* ❌ **ละเมิดกฎ "ค่าที่กว้างที่สุดชนะไม่ได้" ทันที** — agent จะผ่อนข้อจำกัดของ tenant ได้ แปลว่า guardrail ไม่มีความหมาย · ผู้ขอเองก็ปฏิเสธทางนี้ด้วยเหตุผลเดียวกัน

### E. ไม่ทำอะไร

* ❌ กฎที่เขียนว่าสามฝ่ายจะยังหมายถึงสองฝ่ายต่อไป · และ consumer รายแรกที่จะ pin `agent/v1` มี field ที่ไม่มีที่ลงอยู่แล้ววันนี้

## Decision

**A** — เพิ่มบล็อก `policy` ที่ตัดออกได้อย่างเดียว · ชื่อ field ข้างในตรงกับ `profile/v1.policy`

**Reason:** ปัญหาคือ agent ไม่มีปากเสียงในกฎที่บอกว่ามีสามฝ่าย ไม่ใช่ชื่อของกล่อง · เลือก `policy` ตาม `profile/v1` เพราะ **ชื่อข้างในต้องเหมือนกันเพื่อให้ union อ่านออก** และคนที่เห็น `agent.policy.deny_capabilities` กับ `profile.policy.deny_capabilities` จะรู้ทันทีว่ามันรวมกัน — ต่างจากเคส [ADR-0017](0017-the-word-subject.md) ที่คำเดียวกันหมายถึง**สิ่งตรงข้ามกัน** (ผู้กระทำ vs เจ้าของข้อมูล) ที่นี่มันคือของชนิดเดียวกันคนละชั้น การใช้ชื่อเดียวกันจึงช่วยไม่ใช่ทำร้าย · ปฏิเสธ D เพราะ `allow` ฝั่ง agent ทำให้ guardrail ของ tenant ไม่มีความหมาย และ **สิ่งที่ทำให้ field นี้ปลอดภัยพอจะเพิ่มคือการที่มันตัดออกได้อย่างเดียวโดยนิยาม**

**Authority:** Monthop Champaruang — Platform Owner / Architecture Authority of `agent-platform`

### กฎการรวมที่ต้องเขียนกำกับ — schema บังคับให้ไม่ได้

```text
allow  →  intersection    profile.tools.allow ∩ agent.tools
deny   →  union           profile.policy.deny_* ∪ agent.policy.deny_*
```

* **ไม่มีฝ่ายไหนขยายสิ่งที่อีกฝ่ายปิด** — deny ของใครก็ตามชนะเสมอ
* **`agent.policy` ไม่มี `authority_map`** โดยเจตนา — การ map `action_risk → authority` เป็นของ tenant ตาม [ADR-0010](0010-risk-approval-taxonomy.md) ถ้า agent เขียนเองได้ มันจะลดระดับผู้อนุมัติของตัวเองได้
* **`additionalProperties: false`** ที่บล็อกนี้ — กัน `allow` ที่ถูกเติมเข้ามาภายหลังแบบเงียบ ๆ

### ตอบคำถามข้อ 3 ของ [#46](https://github.com/monthop-gmail/agent-platform/issues/46) ไปด้วย — `capability_requirement` ของสองฝ่ายรวมกันยังไง

`capability_requirement` **ไม่ใช่การอนุญาต แต่เป็นความต้องการ** — จึงไม่รวมแบบ intersection

`profiles/README.md` เขียนกฎไว้แล้วว่า *"`deny_capabilities` ต้องไม่ขัดกับ `capability_requirement.required`"* ซึ่งเมื่อมีฝ่าย agent เพิ่มเข้ามาจะกลายเป็น:

```text
required(agent) ∪ required(profile)   ตัดกับ   deny(agent) ∪ deny(profile) ∪ deny(tenant)
    → ต้องเป็นเซตว่าง
    → ถ้าไม่ว่าง = การผูก agent เข้ากับ profile นั้น **invalid ให้ reject ไม่ใช่ลดให้เงียบ ๆ**
```

หลักเดียวกับ `consent/v1` ที่ tenant ไม่ตรงกันต้อง **reject ไม่ใช่ coerce** · agent ที่ต้องการ `shell` ภายใต้ profile ที่ปิด `shell` **ไม่ใช่ agent ที่รันแบบจำกัด แต่คือ agent ที่รันไม่ได้**

### `deny_tools` — ความไม่สมมาตรที่ต้องบันทึก

`profile/v1.policy` มี `deny_capabilities` และ `require_human_for` แต่ **ไม่มี `deny_tools`** เพราะเพดานฝั่ง profile ใช้ `tools.allow` เป็น allowlist อยู่แล้ว

แต่ช่องเดียวกับที่ทำให้ agent ต้องมี `deny_tools` (**tool จาก `mcp_servers` ไม่ผ่าน allowlist**) มีอยู่ฝั่ง profile เหมือนกัน — **ไม่แก้ใน ADR นี้** เพราะ `profile/v1` มี instance จริง 6 ตัวใน `profiles/` และ blast radius ต่างกัน · บันทึกไว้เป็นช่องที่รู้แล้ว

### ไม่ bump major — `agent/v1` `v1.0.0` → `v1.1.0`

optional field ใหม่ล้วน · `required` ยัง 5 ตัวเท่าเดิม · ไม่มีการเข้มขึ้น · **ยังไม่มี consumer รายไหน pin `agent/v1`** ([`consumers.md`](../architecture/consumers.md) ตาราง version usage) จึงไม่มีใครต้อง migrate

## Consequences

* `agent-builder-dsh-poc` มีที่ลงให้ `policy.forbidden` และ `humanApproval.required` ใน manifest ของเขา
* กฎ "สามฝ่าย" กลายเป็นสามฝ่ายจริงเป็นครั้งแรกนับตั้งแต่เขียนกฎนั้น
* **drift check ตรวจข้อนี้ไม่ได้** — กฎการรวม (intersection/union) และกฎ required ∩ deny = ∅ พิสูจน์ได้จากเทสของ consumer ที่รันจริงเท่านั้น ตามขอบเขต [ADR-0011](0011-conformance-automation.md)
* ⚠️ **ถ้า deny-list ถูก compile ลงไปในสิ่งที่ build แล้ว มันต้องอยู่ใน identity ของสิ่งนั้นด้วย** — เป็นเรื่องเดียวกับที่ [ADR-0023](0023-frozen-bindings-and-identity.md) ตอบสำหรับ model binding · **สองใบนี้ต้องอ่านคู่กัน**
* ยังไม่ปิด: `deny_tools` ฝั่ง `profile/v1` · และ `tool_calling` ที่ไม่มีใน `CapabilityId` ([#46](https://github.com/monthop-gmail/agent-platform/issues/46) ข้อ 2) ซึ่งเป็นคนละเรื่อง

## Sources

[issue #47](https://github.com/monthop-gmail/agent-platform/issues/47) · `profile/v1` คำอธิบายกฎสามฝ่าย · [`profiles/README.md`](../profiles/README.md) กฎที่ schema จับไม่ได้ · [ADR-0010](0010-risk-approval-taxonomy.md) `authority_map` เป็นของ tenant · [ADR-0017](0017-the-word-subject.md) บทเรียนเรื่องคำเดียวหลายความหมาย · [ADR-0013](0013-approval-supersedes-chain.md) แผลชนิดเดียวกันครั้งแรก
