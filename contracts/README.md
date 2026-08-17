# Contracts

canonical schema ที่ทุก repo ใน ecosystem ต้องใช้ร่วมกัน — **ผูกพัน**

เปลี่ยนได้ผ่าน ADR เท่านั้น ([ADR-0006](../decisions/0006-contract-versioning.md)) · repo ลูกที่อยากเปลี่ยนต้องเปิด [issue ที่นี่](https://github.com/monthop-gmail/agent-platform/issues/new/choose) ไม่ใช่แก้ในบ้านตัวเอง

## สถานะ v1 — 2026-08-17

| Contract | ไฟล์ | สถานะ | ADR ที่มา |
| --- | --- | --- | --- |
| [`identity/v1`](identity/v1/) | `identity.schema.yaml` | ✅ v1 | [0007](../decisions/0007-multi-tenancy.md) |
| [`agent/v1`](agent/v1/) | `agent.schema.yaml` | ✅ v1 | 0004 · 0009 |
| [`capability/v1`](capability/v1/) | `capability` · `declaration` · `requirement` | ✅ v1 | [0009](../decisions/0009-capability-model.md) |
| [`provider/v1`](provider/v1/) | `provider` · `model-provider` · `agent-provider` | ✅ v1 | [0004](../decisions/0004-agent-vs-model-provider.md) |
| [`model/v1`](model/v1/) | `inference.schema.yaml` | ✅ v1 | 0004 |
| [`tool/v1`](tool/v1/) | `tool.schema.yaml` | ✅ v1 | 0010 |
| [`mcp/v1`](mcp/v1/) | `mcp-server.schema.yaml` | ✅ v1 | — |
| [`execution/v1`](execution/v1/) | `execution.schema.yaml` | ✅ v1 | [0005](../decisions/0005-agent-runtime-boundary.md) |
| [`policy/v1`](policy/v1/) | `policy-decision.schema.yaml` | ✅ v1 | [0010](../decisions/0010-risk-approval-taxonomy.md) |
| [`artifact/v1`](artifact/v1/) | `artifact.schema.yaml` | ✅ v1 | — |
| [`error/v1`](error/v1/) | `error.schema.yaml` | ✅ v1 | — |
| [`approval/`](approval/) | — | ⏳ **external-authority-pending** | [0006](../decisions/0006-contract-versioning.md) |
| [`event/`](event/) | — | ⏳ **external-authority-pending** | [0006](../decisions/0006-contract-versioning.md) |

สองตัวสุดท้ายรอ agreement จาก Architecture Owner ของ `devfactory-core` — ไม่ใช่เพราะยังไม่พร้อม แต่เพราะยังไม่มีสิทธิ์ ดู [issue #6](https://github.com/monthop-gmail/agent-platform/issues/6)

## กติกา

### รูปแบบ

* **YAML + JSON Schema draft 2020-12 เท่านั้น** — ไม่มี TypeScript type, ไม่มี Pydantic model, ไม่มี `.proto` ใน repo นี้ ([ADR-0008](../decisions/0008-reference-stack.md))
* codegen เป็นหน้าที่ของ repo ลูก แต่ละภาษา gen จาก schema ชุดเดียวกัน
* field เป็น `snake_case` · id เป็น `lower-kebab` หรือ `lower_snake` ตาม `identity/v1#/$defs/Id`

### `$id` และ `$ref`

schema อ้างกันด้วย URI prefix `https://schemas.agent-platform.internal/` ซึ่ง**ไม่ resolve จริงบนอินเทอร์เน็ต** — เป็น namespace ล้วน

consumer ต้อง map prefix นี้เข้ากับ path ในเครื่องตอน bundle:

```text
https://schemas.agent-platform.internal/  →  <repo>/contracts/
```

เหตุที่ไม่ใช้ URL จริง: contract ต้องใช้ได้ในเครือข่ายปิดและตอน CI ที่ไม่มีเน็ต

### Versioning

* `contracts/<name>/vN/` — breaking change ขึ้น major ใหม่ ไม่แก้ของเดิม
* ภายใน major เพิ่ม optional field และเพิ่มค่าใน enum ได้ · **ห้าม**ลบ field, เปลี่ยน type, เพิ่ม required, ลบค่า enum, เข้มขึ้นใน validation
* ทุก contract มี `CHANGELOG.md` ของตัวเอง
* นิยาม breaking change แบบเต็มและ deprecation window อยู่ใน [ADR-0006](../decisions/0006-contract-versioning.md)

### สิ่งที่ consumer ต้องทำ

ไม่ใช่ข้อแนะนำ — repo ที่ไม่มีครบ 3 ข้อ **ไม่ถือเป็น consumer** และ platform ไม่รับประกันความเข้ากันได้ให้

1. `platform-contract.yaml` ที่ root ประกาศ version ที่ pin + ผล conformance
2. conformance test ใน CI ที่ validate payload จริงกับ schema ที่ pin
3. test เป็นเงื่อนไขของ release

ขึ้นทะเบียนที่ [`architecture/consumers.md`](../architecture/consumers.md)

### กฎที่ต้อง fallback ให้ปลอดภัย

consumer ที่เจอค่าที่ไม่รู้จักต้องเลือกทางที่ปลอดภัยกว่าเสมอ:

| เจอค่าไม่รู้จักใน | ให้ถือว่า |
| --- | --- |
| `capability` | **ไม่มี** capability นั้น |
| `action_risk` | `critical` |
| `authority` | `human_command_required` |
| field ที่ไม่รู้จัก | ข้ามไป — **ห้าม fail** |

## ศัพท์

ศัพท์ทั้งหมดที่ใช้ในไฟล์เหล่านี้ lock แล้วตาม [`decisions/`](../decisions) — ดูตาราง "ศัพท์ที่ lock แล้ว" ก่อนตั้งชื่อ field ใหม่

หลักที่ห้ามละเมิดไม่ว่าเส้นทางไหน (RFC-0004 · ADR-0003 · ADR-0005):

```text
execution ไม่ตัดสิน governance เอง
execution ไม่แตะ backend resource ตรง ๆ
execution ไม่ถือ provider credential เอง
```

external agent provider ก็ต้องผ่าน gateway เหมือนกัน — ไม่มีสิทธิ์พิเศษเพราะเป็นของ vendor
