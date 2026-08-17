# Profiles

**contract เดียวกัน แต่ profile ต่างกัน** — profile ไม่เพิ่มความสามารถใหม่ให้ platform
แต่กำหนดว่างานประเภทหนึ่งใช้อะไรได้ และต้องขออนุมัติเมื่อไหร่

schema อยู่ที่ [`contracts/profile/v1`](../contracts/profile/v1/) · ไฟล์ในโฟลเดอร์นี้เป็น **instance** ของ schema นั้น

## 6 profile

| Profile | ใช้กับ | จุดเด่นของกรอบอำนาจ |
| --- | --- | --- |
| [`coding-agent`](coding-agent/profile.yaml) | devfactory-core · agent-fleet | เขียน code ได้เต็มที่ใน sandbox · **merge เป็นของคน** |
| [`security-agent`](security-agent/profile.yaml) | navi-security-agent | เข้มที่สุด — **AI ≠ Authority** · ห้าม physical action ทุกชนิด |
| [`knowledge-agent`](knowledge-agent/profile.yaml) | enterprise-knowledge | อ่านอย่างเดียว · ความเสี่ยงคือ *เห็นสิ่งที่ไม่ควรเห็น* ไม่ใช่ทำข้อมูลพัง |
| [`enterprise-agent`](enterprise-agent/profile.yaml) | Odoo · ERP · CRM | อ่านอิสระ แต่ **ทุกการเขียนต้องมีคนเห็นชอบ** |
| [`workflow-agent`](workflow-agent/profile.yaml) | orchestration | มอบหมายได้ แต่ **ห้ามแก้ artifact เอง** (RFC-0004) |
| [`autonomous-agent`](autonomous-agent/profile.yaml) | opt-in ต่อ tenant | profile เดียวที่เปิด `autonomous_execution` · แลกด้วยเพดานที่ต่ำที่สุด |

## เปรียบเทียบ authority_map

จุดที่ profile ต่างกันจริง ๆ อยู่ที่ตารางนี้ — `action_risk` เท่ากันแต่ได้ `authority` ต่างกันตามบริบทงาน

| Profile | low | medium | high | critical |
| --- | --- | --- | --- | --- |
| coding-agent | `auto` | `auto` | `approval_required` | `human_command_required` |
| knowledge-agent | `auto` | `auto` | `approval_required` | `human_command_required` |
| workflow-agent | `auto` | `auto` | `approval_required` | `human_command_required` |
| enterprise-agent | `auto` | **`approval_required`** | `human_command_required` | `human_command_required` |
| autonomous-agent | **`notify`** | `approval_required` | `human_command_required` | `human_command_required` |
| security-agent | **`notify`** | `approval_required` | **`human_command_required`** | `human_command_required` |

อ่านตารางนี้แล้วจะเห็นเหตุผลของ [ADR-0010](../decisions/0010-risk-approval-taxonomy.md) ชัดที่สุด — ถ้าใช้ `risk_level` ค่าเดียวรวมทุกอย่าง จะเขียนตารางนี้ไม่ได้เลย เพราะ `medium` ของ coding-agent กับ `medium` ของ enterprise-agent เป็นความเสี่ยงระดับเดียวกัน แต่ต้องการอำนาจอนุมัติคนละระดับ

`security-agent` และ `autonomous-agent` ไม่มี `auto` เลยแม้แต่ระดับ low — เพราะงานเฝ้าระวังแตะข้อมูลบุคคล และงานที่เริ่มเองไม่มีคนคอยเบรก

## กติกา

* profile เป็น **เพดาน ไม่ใช่การอนุญาต** — สิทธิ์จริงคือส่วนที่ profile, agent และ policy ของ tenant ตกลงตรงกันทั้งสามฝ่าย ค่าที่กว้างที่สุดชนะไม่ได้
* `tools.allow` ว่าง = **ไม่อนุญาต tool ใดเลย** ไม่ใช่อนุญาตทั้งหมด
* `tools.deny` ชนะ `allow` เสมอ
* `authority` ที่ไม่ได้ระบุใน `authority_map` ให้ fallback เป็น `human_command_required`
* `extends` **ทำให้แคบลงได้อย่างเดียว** — profile ลูกที่เปิดสิ่งที่พ่อปิดไว้ถือว่าผิด contract
  (ตัวอย่างจริง: `autonomous-agent` มี tool set ใกล้ `knowledge-agent` มาก แต่ **ใช้ `extends` ไม่ได้**
  เพราะ knowledge-agent ปิด `autonomous_execution` ไว้ — เขียนเหตุผลไว้ในไฟล์แล้ว)

## ตรวจสอบ

instance ทุกไฟล์ validate ผ่าน `contracts/profile/v1/profile.schema.yaml` แล้ว โดย resolve `$ref` ข้ามไฟล์ผ่าน local registry (map `https://schemas.agent-platform.internal/` → `contracts/`)

⚠️ **schema จับได้แค่รูปแบบ ไม่จับความหมาย** — กฎที่ยังต้องตรวจด้วยคนหรือ lint ภายนอก:

| กฎ | ทำไม schema จับไม่ได้ |
| --- | --- |
| `extends` ต้องทำให้แคบลงเท่านั้น | ต้องเทียบสองไฟล์พร้อมกัน |
| tool ใน `allow` ต้องมีอยู่จริงใน tool registry | registry เป็น runtime state |
| `deny_capabilities` ต้องไม่ขัดกับ `capability_requirement.required` | ต้องเทียบข้าม field |
| `require_human_for` ต้องเป็น subset ของ tool ที่ profile นี้แตะได้ | เทียบข้าม field |

เครื่องมือตรวจอยู่นอก repo นี้ — [ADR-0008](../decisions/0008-reference-stack.md) ห้ามมี code ใน `agent-platform`
