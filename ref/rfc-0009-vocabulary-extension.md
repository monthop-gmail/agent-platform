# RFC-0009 + PR #13 — เพิ่ม event type เป็น additive

บันทึกดิบของการแก้ Rule 2 เมื่อ 2026-08-18 — เก็บทั้งสองฝั่งไว้ด้วยกันเพราะเป็นการเปลี่ยนแปลงเดียวกัน

| ฝั่ง | เอกสาร |
| --- | --- |
| ต้นทาง (semantics) | [`devfactory-core/rfcs/0009-vocabulary-extension.md`](https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/0009-vocabulary-extension.md) — merged ที่ [devfactory-core#12](https://github.com/monthop-gmail/devfactory-core/pull/12) |
| ปลายทาง (wire schema) | [agent-platform#13](https://github.com/monthop-gmail/agent-platform/pull/13) — merged `37a1997` · 5 ไฟล์ +74/-7 |

ผลผูกพันอยู่ที่ [`decisions/0006-contract-versioning.md`](../decisions/0006-contract-versioning.md) และ schema — ไฟล์นี้เป็นบันทึกเท่านั้น

---

# 1. RFC-0009 (ต้นฉบับจาก `devfactory-core`)

> คัดลอกตามต้นฉบับ ไม่แก้ — **relative link ข้างในชี้ไปยังไฟล์ใน `devfactory-core` ไม่ใช่ repo นี้**
> เติม `https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/` ข้างหน้าเพื่อเปิด
> (`0005-platform-contract-authority.md` · `../references/team-notes/2026-08-18-adr-0006-ownership-transfer.md`)

# RFC-0009: Vocabulary Extension Is Additive

## Status
Draft — Architecture Owner direction agreed 2026-08-18 · pending maintainer approval per `GOVERNANCE.md`

**Amends [RFC-0005](0005-platform-contract-authority.md) Rule 2** and its mirror in
[ADR-0006](https://github.com/monthop-gmail/agent-platform/blob/main/decisions/0006-contract-versioning.md).
Everything else in RFC-0005 stands.

Raw proposal that prompted this: [`references/team-notes/2026-08-18-adr-0006-ownership-transfer.md`](../references/team-notes/2026-08-18-adr-0006-ownership-transfer.md)

## Context
RFC-0005 split contract authority: semantics here, canonical wire schema at
`agent-platform`. On 2026-08-18 `agent-platform` accepted that split as ADR-0006
option **C2**, added it as a third option alongside A2 and B2, and published
`contracts/approval/v1` and `contracts/event/v1` as canonical. Both carry
`derived_from` pointers to `contract-semantics.yaml` at `semantics_version: "1.0"`
and mark their semantic sections with 🔒.

The split is therefore in force on both sides, and the two contracts that were
blocked for two days now exist.

A team review of that arrangement raised one objection, and it is correct.

## Problem Statement
RFC-0005 Rule 2 classifies five kinds of change as semantic, each requiring an RFC
in this repository first. The first of those five is:

> adding, removing, or renaming a decision type or event type

**Adding** does not belong in that list — at least not for event types.

An event type is a new category of observation. When `navi-security-agent` needs
one for a sighting, or `enterprise-knowledge` needs one for ACL-aware retrieval,
Rule 2 sends that change through this repository: an RFC, a majority maintainer
vote, an Architecture Owner with no stake in the outcome, for vocabulary Dev
Factory does not use and has no view on. Multiply by the repositories being
planned and Dev Factory becomes the ecosystem's gatekeeper by accident — the
opposite of the intended topology, where `agent-platform` sits at the centre and
Dev Factory is one consumer among several.

The published schema already disagrees with the rule. `event/v1` carries this
under `platform_rules`:

> consumer ที่เจอ `event_type` ที่ไม่รู้จักต้องเก็บ event ไว้แล้วข้ามการตีความ ห้าม drop และห้าม fail

A contract that instructs consumers how to behave when they meet an unknown event
type is a contract that expects its enum to grow. Rule 2 made that growth require
an RFC here. The schema and the ownership rule were describing different futures.

## Goals
- Remove the bottleneck for vocabulary other repositories need.
- Keep the protections that made the split worth having.
- Change as little as possible: ADR-0006 is accepted and two contracts are
  published.

## Non-Goals
- Reopening the ownership question. C2 is accepted on both sides and this RFC
  does not disturb it.
- Changing the wire schema. Which fields exist and what they are called remains
  `agent-platform`'s, exactly as before.

## Decision — separate *adding* from *changing*, and treat events and decisions differently

### Event types: adding is additive

`agent-platform` may add new event types under Rule 1, on its own ADR process,
with no RFC here.

The seven canonical types stay exactly as they are:

```text
JOB_CREATED · STATE_TRANSITION · GOVERNANCE_DECISION · TASK_ASSIGNED
EXECUTION_STARTED · EXECUTION_FAILED · JOB_COMPLETED
```

**Removing, renaming, or redefining any of the seven remains a semantic change**
and still requires an RFC here. The list is now a *required minimum*, not a
closed set: these seven must exist and must keep their meanings, and the enum may
grow past them.

### Decision types: adding stays semantic

The approval vocabulary — `APPROVE`, `REJECT`, `REQUIRE_CHANGES` — stays closed.
Adding a fourth outcome still requires an RFC here.

The asymmetry is deliberate and is the substance of this RFC rather than an
inconsistency in it. A new event type is a new thing to observe; it cannot weaken
a guarantee, because nothing is permitted or forbidden on the basis of an event's
existence. A new approval outcome is different in kind. A value such as
`AUTO_APPROVE`, or an `APPROVE_WITH_CONDITIONS` whose conditions nobody checks,
creates a path by which execution proceeds without a human `APPROVE` — Rule 2's
own fifth clause, and the direction lock this repository exists to hold. That
path can be opened by adding a value, without removing or renaming anything.

So: adding to an observation vocabulary is additive; adding to a decision
vocabulary is not.

### Rule 2, as amended

A change is semantic — requiring an RFC here before `agent-platform` may
implement it — when it:

1. removes, renames, or redefines an existing decision type or event type
2. adds a decision type
3. weakens or removes a stated guarantee
4. changes a semantically required field to optional, or the reverse
5. changes what an existing decision, event, or state *means*
6. introduces a path by which execution can proceed without `APPROVE`

Adding an event type is not on this list. It is additive under Rule 1.

## Consequence — `semantics_version` moves to 1.1

`contract-semantics.yaml` goes to `1.1`, because the `frozen` block changes
meaning: `event_types` becomes a required minimum rather than a closed set.

Both published contracts pin `semantics_version: "1.0"` in `derived_from`, so
both need their pointer updated to `1.1`. This is the first real exercise of the
drift mechanism, and it behaves as designed — a change to what is frozen produces
a version move, which produces a visible, required update at every derived
contract. Sequencing: this repository merges first, then `agent-platform` updates
the two pointers. The window between the two merges is a known, deliberate
mismatch, and ADR-0006 checks `derived_from` at contract-change time rather than
in CI, so nothing fires spuriously in between.

## Alternatives Considered

**Transfer ownership of `approval` and `event` to `agent-platform` outright (A2).**
This was the proposal that prompted the review, made on the understanding that
ADR-0006 was still `Pending`. It had in fact been accepted with C2 hours earlier,
and both contracts had been published.

Rejected because it costs far more than the problem does. It would reverse a
decision the platform's Architecture Authority signed the same day, rewrite the
ownership framing of two canonical contracts, and remove twelve 🔒 markers — to
solve a bottleneck that one clause of one rule creates. The narrow amendment
removes the bottleneck completely, and there is no second problem that the
transfer would additionally solve.

It would also discard what the same review asked to preserve. The proposal's own
closing point was **Owner ≠ unilateral authority** — ownership must not mean the
owner may redefine governance at will. That is precisely what C2 Rule 5 already
provides: semantics resolve at this repository's Architecture Owner, schema shape
and versioning at `agent-platform`'s, and neither may settle the other's half.
Transferring everything and then re-deriving that protection through ADR review
would arrive at a weaker version of what is already in force.

**Do nothing.** Leaves the bottleneck in place. It costs nothing today, because
no other consumer repository exists yet, and it becomes expensive precisely when
the ecosystem starts to work — the first time a second consumer needs a word for
something.

## Confirmations to `agent-platform`

- **Owner ≠ unilateral authority** — agreed and already satisfied by C2 Rule 5.
  No change needed.
- **Breaking changes require ADR and review** — agreed, per ADR-0006's existing
  definition of breaking. This RFC adds one clause: weakening or removing a
  guarantee counts as breaking even when the wire format stays compatible. A
  schema can remain compatible while the meaning underneath it does not, and that
  case must not pass as additive.
- **Checking `derived_from` at contract-change time rather than in CI** —
  accepted. ADR-0008 forbids implementation in that repository and a workflow
  that fetches and hashes another repository's manifest is code to maintain.
  `hash_scope: frozen` stays available for when the stated review conditions are
  met.
- **`subject_id` and `job_id` both kept** — agreed, including the added schema
  rule that they must match when `subject_type: job`.

## What still cannot be claimed

The team's Definition of Done ends with:

> `devfactory-core` ลงทะเบียนเป็น **first conforming consumer**

ADR-0006 defines a consumer as having a manifest, a CI conformance test over
**real payloads**, and a release gate. This repository has the manifest.
`packages/*` has no code, so there is no payload to validate and no release to
gate.

`conformance.status` stays `unknown` and the registry entry reads **registered,
not conforming**. `platform-contract.yaml` now carries a `registration` field so
the two are not conflated by a reader skimming the table. The item closes when
[issue #2](https://github.com/monthop-gmail/devfactory-core/issues/2) produces
code that emits real payloads — five of the six DoD items are done, this one is
blocked on implementation rather than on agreement.

## Architectural Impact

- **Control Plane** — none. The approval vocabulary is unchanged and stays closed.
- **Orchestration** — none.
- **Execution** — none.
- **Observability** — the event vocabulary becomes extensible by
  `agent-platform`. The seven canonical types and all eight event guarantees are
  unchanged.

## Risk Assessment

| risk | severity | mitigation |
| --- | --- | --- |
| An added event type quietly changes what an existing one means | medium | Redefinition is clause 1 of the amended rule and stays semantic; adding a near-duplicate that drains meaning from an existing type is a redefinition in substance and is treated as one |
| The event enum sprawls with no editor | low | `agent-platform` owns it under its own ADR process, which is where every other enum in the contract set already lives |
| The asymmetry between events and decisions is read as an oversight | medium | Stated as the substance of the decision with the failure mode it prevents (`AUTO_APPROVE`), not as an exception |
| The 1.0 → 1.1 pointer update is forgotten upstream | medium | Both contracts carry the pointer explicitly and ADR-0006 declares a stale pointer out of conformance; the update is two lines in files that are reviewed on change |
| A future consumer needs a decision type and hits the bottleneck this RFC removes for events | low | Accepted deliberately — that is the case where a review here is worth its cost, since it is the direction lock being touched |

## Migration Plan

1. Accept this RFC.
2. `contract-semantics.yaml` → `semantics_version: "1.1"`; `event_types` marked
   as a required minimum; `platform_may_add_freely` gains event types.
   **Included in this change.**
3. `platform-contract.yaml` pins `approval/v1` and `event/v1`, which now exist,
   and records `registration: registered`. **Included in this change.**
4. `agent-platform` amends ADR-0006 Rule 2, updates both `derived_from` pointers
   to `1.1`, and adjusts the 🔒 note on `EventType` in `event/v1`.
5. Conformance stays blocked on code — issue #2.

## Open Questions
- Should an added event type still be announced to consumers somehow, or is the
  `CHANGELOG.md` for `event/v1` enough? The changelog is enough for now; a
  notification mechanism is worth having only once there are consumers to notify.

---

# 2. PR #13 — คำอธิบายตอนเปิด (`agent-platform`)

คู่กับ [devfactory-core#12](https://github.com/monthop-gmail/devfactory-core/pull/12) — **merge PR โน้นก่อน** เพราะ PR นี้ชี้ไปที่ `semantics_version: "1.1"` ที่จะมีอยู่จริงหลัง PR โน้น merge

## ปัญหา

`กฎ 5 ข้อ` ข้อ 2 รวมคำว่า **เพิ่ม** ไว้กับ ลบ/เปลี่ยนชื่อ:

> เพิ่ม/ลบ/เปลี่ยนชื่อ decision หรือ event type

ผลคือ event type ใหม่ที่ repo อื่นต้องการ ต้องผ่าน RFC cycle + majority maintainer vote ของ `devfactory-core`

```text
navi-security-agent  → event type สำหรับ sighting
enterprise-knowledge → event type สำหรับ ACL-aware retrieval
              ↓
        รอ devfactory-core
              ↓
  vocabulary ที่ Dev Factory ไม่ได้ใช้ ถูก gate โดย Dev Factory
```

คูณด้วยจำนวน repo ที่วางแผนไว้ = Dev Factory กลายเป็นศูนย์กลางของ ecosystem โดยไม่ตั้งใจ ตรงข้ามกับ topology ที่ ADR-0001 ตั้งไว้

**schema ที่เราเขียนเองก็ไม่เห็นด้วยกับกฎนี้อยู่แล้ว** — `event/v1` `platform_rules`:

> consumer ที่เจอ `event_type` ที่ไม่รู้จักต้องเก็บ event ไว้แล้วข้ามการตีความ ห้าม drop และห้าม fail

contract ที่สอนวิธีรับมือ event type ที่ไม่รู้จัก คือ contract ที่คาดว่า enum จะโต · กฎ ownership กับ schema กำลังบรรยายอนาคตคนละแบบ

`devfactory-core` เห็นด้วยและออก [RFC-0009](https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/0009-vocabulary-extension.md)

## แก้อะไร

| | เพิ่มค่าใหม่ | ลบ · เปลี่ยนชื่อ · เปลี่ยนความหมาย |
| --- | --- | --- |
| `event/v1` `EventType` | ✅ **additive** — ADR ที่นี่พอ | 🔒 semantic — RFC ที่ต้นทาง |
| `approval/v1` `Decision` | 🔒 **semantic** — RFC ที่ต้นทาง | 🔒 semantic — RFC ที่ต้นทาง |

**Rule 2 ฉบับแก้** — 6 ประเภท ไม่มี "เพิ่ม event type":

1. ลบ/เปลี่ยนชื่อ/เปลี่ยนความหมาย decision หรือ event type ที่มีอยู่
2. **เพิ่ม decision type**
3. ลดหรือถอน guarantee
4. เปลี่ยน field ที่มีความหมาย required ↔ optional
5. เปลี่ยนความหมายของ decision/event/state ที่มีอยู่
6. เปิดทางให้ execution เดินได้โดยไม่มี `APPROVE`

### ความไม่สมมาตรเป็นเจตนา

event type ใหม่ = สิ่งที่สังเกตเพิ่ม · ลดทอน guarantee ไม่ได้ เพราะไม่มีอะไรถูกอนุญาตหรือห้ามจากการที่ event มีอยู่

decision outcome ใหม่ = คนละเรื่อง · `AUTO_APPROVE` หรือ `APPROVE_WITH_CONDITIONS` ที่ไม่มีใครตรวจ condition **เปิดทางให้ execution เดินโดยไม่มี `APPROVE` ของคน — ด้วยการเพิ่มค่า ไม่ใช่ลบค่า** ซึ่งเป็นข้อ 6 ของ Rule 2 เอง

เขียนคำอธิบายนี้ลงใน `$defs` ของทั้งสองไฟล์ เพื่อให้คนที่เปิดไฟล์เดียวเห็นเหตุผล ไม่ต้องไปขุด ADR

## ที่ไม่เปลี่ยน

- 7 event type เดิม — ครบ ไม่ขยับ (กลายเป็น *ขั้นต่ำที่ต้องมี*)
- guarantee ทั้ง 8 ข้อของ `event/v1` — ครบ ไม่ขยับ
- `approval/v1` `Decision` 3 ค่า — ครบ ไม่ขยับ
- ไม่มี field ใดถูกเพิ่ม ลบ หรือเปลี่ยน type ในทั้งสอง schema

## `semantics_version` 1.0 → 1.1

ต้นทางขยับเพราะ `frozen` เปลี่ยนความหมาย · `derived_from` ทั้งสองไฟล์อัปเดตตาม

**นี่คือกลไก drift ทำงานจริงครั้งแรก และทำงานตามที่ออกแบบ** — สิ่งที่ frozen เปลี่ยน → version ขยับ → เกิด update ที่บังคับและมองเห็นได้ที่ทุก derived contract · ไม่ต้องเดา ไม่ต้องไว้ใจ

## Versioning

| contract | เดิม | ใหม่ | breaking? |
| --- | --- | --- | --- |
| `event/v1` | v1.0.0 | **v1.1.0** | ไม่ — payload ที่ถูกต้องกับ v1.0.0 ยังถูกต้องทุกตัว ชุดค่าที่รับกว้างขึ้นเท่านั้น |
| `approval/v1` | v1.0.0 | **v1.0.1** | ไม่ — แก้ description กับ pointer เท่านั้น schema ไม่ขยับ |

ไม่ขึ้น major ตาม ADR-0006 — การขยาย enum ภายใน major ทำได้ และไม่มีการลบ field เปลี่ยน type หรือเพิ่ม required

## เพิ่มอนุประโยคเรื่อง breaking

**ลดหรือถอน guarantee = breaking เสมอ แม้ wire format ยัง compatible**

schema อยู่ได้โดยที่ความหมายข้างใต้เปลี่ยนไปแล้ว · เคสนั้นต้องไม่หลุดผ่านไปในฐานะ additive · ข้อนี้ตอบข้อกังวล **"Owner ≠ unilateral authority"** ที่ทีมยกมา — ส่วนที่เหลือของข้อกังวลนั้น Rule 5 ให้อยู่แล้ว

## หมายเหตุ

ทีมเสนอให้โอน ownership ของ `approval` + `event` มาที่ repo นี้ทั้งก้อน (A2) โดยเข้าใจว่า ADR-0006 ยัง `Pending` — ตอนตรวจพบว่า accept ไปแล้วด้วย C2 และ contract ทั้งสอง publish แล้ว จึงเลือกแก้แบบแคบแทน

เหตุผลเต็มอยู่ใน [RFC-0009 หัวข้อ Alternatives Considered](https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/0009-vocabulary-extension.md) — สรุป: การโอนทั้งก้อนต้องย้อน decision ที่เพิ่งลงนาม rewrite contract ที่ publish แล้ว และเอา 🔒 ออก 12 จุด เพื่อแก้คอขวดที่อนุประโยคเดียวสร้าง · และจะทิ้ง Rule 5 ซึ่งเป็นสิ่งที่ทีมเองขอให้มี

🤖 Generated with [Claude Code](https://claude.com/claude-code)

