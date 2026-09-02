# conformance

**ข้อยกเว้นเดียวของ [ADR-0008](../decisions/0008-reference-stack.md)** — โฟลเดอร์เดียวใน repo นี้ที่มี code ได้

ขอบเขตกำหนดโดย [ADR-0011](../decisions/0011-conformance-automation.md) และ**บังคับด้วยความตั้งใจ ไม่ใช่ด้วยเครื่อง** — ถ้ามันเริ่มโต นั่นคือสัญญาณให้ทบทวน ADR ไม่ใช่ให้ขยายเงียบ ๆ

## ใช้ยังไง

```bash
# ดึง manifest จาก repo ต้นทางผ่าน raw.githubusercontent
python3 conformance/drift_check.py

# ใช้ clone ในเครื่องแทน — ชี้โฟลเดอร์แม่ที่มีหลาย clone ได้
python3 conformance/drift_check.py --local /opt/docker-test
```

`--local` หา `<dir>/<repo-name>/<path>` ก่อน แล้วค่อย `<dir>/<path>` · repo ที่ไม่มี clone ในเครื่องจะดึงจาก network ต่อ **ไม่ใช่เดาจากไฟล์ของ repo อื่น** — เวอร์ชันแรกอ่านไฟล์เดียวให้ทุก repo ซึ่งมองไม่เห็นตอนมี consumer รายเดียว

ต้องมี `pyyaml` `jsonschema` `referencing` · **ไม่มี `requirements.txt` โดยตั้งใจ** — pin ไว้ใน [workflow](../.github/workflows/drift-check.yml) แทน เพราะ ADR-0008 ห้าม dependency manifest ใน repo นี้

`exit 1` เมื่อมี FAIL · `exit 0` เมื่อมีแค่ WARN

## ตรวจอะไร

| # | ตรวจ | จับ |
| --- | --- | --- |
| 1 | `derived_from.semantics_version` เทียบต้นทาง | ต้นทางขยับ semantics แล้วเราไม่ตาม |
| 2 | `frozen` vocabulary — ขาดค่าที่บังคับ · เกินเมื่อ `closed: true` | ลบ event type ที่ต้องมี · **เพิ่ม decision type เข้าชุดปิด** |
| 3 | จำนวน guarantees | ถอน guarantee เงียบ ๆ |
| 3b | **field ผูกกับ enum ปิด/เปิด ตรงกับ `closed` ของต้นทางไหม** | schema ประกาศว่าชุดเปิดแต่ field ยัง `$ref` ไป enum ปิด — [#17](https://github.com/monthop-gmail/agent-platform/issues/17) |
| 4 | `consumers.md` เทียบ `platform-contract.yaml` จริง | registry ตามหลัง manifest |
| 5 | ตาราง version usage | ตารางอ่านว่าปิด version ได้ทั้งที่มีคน pin |
| 6 | schema draft 2020-12 · `$ref` · `CHANGELOG.md` | contract พังหรือชี้ไปไม่มีอะไร |
| 7 | profile ทุกตัวกับ `contracts/profile/v1` | profile หลุด schema |
| 8 | **แถวที่อ้างว่า "ยังไม่มี repo"** — repo นั้นเกิดขึ้นแล้วหรือยัง | ทะเบียนที่ผูกพันรายงานข้อเท็จจริงผิดโดยไม่มีอะไรมาเทียบ — [PR #27](https://github.com/monthop-gmail/agent-platform/pull/27) |

**ข้อ 1–3 auto-discover จากบล็อก `derived_from`** — เพิ่ม derived contract ใหม่แล้วครอบคลุมเองทันที ไม่ต้องแก้ checker

**ข้อ 4 อ่าน manifest จาก branch ที่แถวระบุ ไม่ใช่ `main` เสมอ** — ref มาจากลิงก์ `/blob/<ref>/platform-contract.yaml` ในแถวเอง **ไม่มีคอลัมน์ใหม่** เพราะลิงก์นั้นคือสิ่งที่คนกดอยู่แล้ว · ไม่มี `/blob/<ref>/` → `main` เหมือนเดิม

ทะเบียนไม่ควรเดาว่าทุก repo วาง manifest ไว้บน `main` — `navi-ims` ใช้ `master` และ repo ที่ freeze สายเก่าไว้จะวาง manifest บน branch ที่มันบรรยายจริง · **การบังคับให้เอาไปไว้บน default branch คือการบังคับให้ไฟล์บรรยายโค้ดที่ไม่ใช่ตัวเอง**

**เน็ตล่มไม่ใช่ drift** — `fetch` retry 3 ครั้งก่อนยอมแพ้ แล้วแยกสองกรณีออกจากกัน:

| อะไรเกิดขึ้น | รายงานเป็น |
| --- | --- |
| **HTTP 404** — เซิร์ฟเวอร์ตอบชัดว่าไม่มีไฟล์ที่ ref นั้น | **FAIL** (ไม่ retry — retry ไม่ช่วย) |
| **403 · 5xx · connection reset · timeout** | **WARN** *"ยังไม่ได้ตรวจ ไม่ใช่ผ่าน"* |

เดิมทั้งสองกรณีตกลง `except` เดียวกันแล้วกลายเป็น FAIL ทั้งคู่ (`HTTPError` เป็น subclass ของ `URLError`) — CI บน `main` เคยแดงเพราะ `Connection reset by peer` ทั้งที่ไม่มีอะไร drift · **CI แดงที่ไม่ใช่ของจริงจะสอนให้คนเลิกเชื่อสีแดง ซึ่งเป็นโรคเดียวกับ false ✅ แค่คนละด้าน**

หลักเดียวกับที่ `ecosystem-intelligence` แก้ guardian ของตัวเอง — *"ตอบว่ายังไม่ได้ตรวจ ไม่ใช่ปิดได้ · การเดาแล้วผิด แพงกว่าการบอกว่าไม่รู้"*

⚠️ `--local` อ่านไฟล์ในเครื่องตาม branch ที่ checkout อยู่ ซึ่งอาจไม่ใช่ ref ที่ทะเบียนระบุ — โหมดนั้นมีไว้ทำงานออฟไลน์ **ผลที่ผูกพันคือผลจาก network**

**ข้อ 8 พิสูจน์ได้ทางเดียว — และต้องอ่านแบบนั้น** เห็น `README.md` ของ repo บน `raw.githubusercontent` แปลว่า repo **มีจริงแน่นอน** → FAIL · แต่ **ไม่เห็นไม่ได้แปลว่าไม่มี** — repo ที่ไม่มี README หรือที่ default branch ชื่ออื่น (`navi-ims` ใช้ `master`) ก็ไม่เห็นเหมือนกัน · check นี้จึงเป็น **ตัวจับ ไม่ใช่ตัวรับรอง** และข้อความตอน ok เขียนกำกับไว้ตรง ๆ ไม่งั้นมันจะกลายเป็นความมั่นใจปลอมตัวที่สี่

ตรวจทั้ง `main` และ `master` · owner เอาจากแถวที่มีลิงก์จริงในตาราง ไม่ hardcode · **ที่ไม่ใช้ `api.github.com` ทั้งที่แม่นกว่า** เพราะ [ADR-0011](../decisions/0011-conformance-automation.md) จำกัด host ไว้ที่ `raw.githubusercontent.com` ตัวเดียว — ขยายขอบเขตต้องแก้ ADR ไม่ใช่แก้เงียบ ๆ · เน็ตไม่ถึงจะได้ WARN ไม่ใช่ ok เพื่อไม่ให้ "ออฟไลน์" อ่านเป็น "ไม่มี repo"

**ข้อ 4 อ่านแถวใน `consumers.md` จริง ๆ ไม่ใช่ค้นทั้งไฟล์** — เวอร์ชันแรกของ check นี้ถามแค่ว่าชื่อ contract โผล่ที่ไหนสักแห่งไหม ซึ่งได้ ✅ ปลอมเพราะคำว่า `approval` โผล่ในย่อหน้าอื่นอยู่แล้ว

## ⚠️ เพิ่ม check ใหม่ต้องมี negative test

check ที่ไม่เคยเห็นสถานะ FAIL คือ check ที่ยังไม่รู้ว่าทำงาน — และ check ที่หลวมอันตรายกว่าไม่มี check เพราะสร้างความมั่นใจปลอม

วิธีทดสอบ: **สำเนาไฟล์เก็บไว้ก่อน** → แก้ให้ผิดชั่วคราว → รัน → ต้องเห็น FAIL ที่ตรงกับสิ่งที่แก้ → คืนจากสำเนา

> ⚠️ อย่าใช้ `git checkout` คืน ถ้ายังมีงานที่ยังไม่ commit อยู่ในไฟล์นั้น — เคยทำแล้วลบงานที่แก้ค้างไว้หายไปทั้งหมด · `cp` ไฟล์เก็บไว้ก่อนแล้ว `cp` กลับ ปลอดภัยกว่าและไม่ต้องพึ่งสถานะของ git

ชุดที่ใช้ตอนสร้าง checker นี้ ทั้ง 5 เคส FAIL ตามคาด:

| เคส | ผลที่ต้องได้ |
| --- | --- |
| pin `semantics_version` ผิดเวอร์ชัน | `derived: pin=1.0 แต่ต้นทาง=1.1` |
| ลบ `TASK_ASSIGNED` ออกจาก event enum | `frozen: ขาดค่าที่ต้นทางบังคับ` |
| เพิ่ม `AUTO_APPROVE` เข้า decision enum | `frozen: ต้นทาง closed=true แต่มีค่าเกิน` |
| ลบ pin ออกจากแถวใน `consumers.md` | `registry: แถวนี้ขาด pin` |
| ลบ guarantee ออกจาก schema | `frozen: guarantees มี 1 ข้อ ต้นทางบังคับ 3` |
| ให้ `event_type` ผูกกับ enum ปิดอีกครั้ง | `binding: ต้นทาง closed=false แต่ field ผูกกับ enum ปิด` |
| ถอด `decision` ออกจาก enum ปิด | `binding: closed=true แต่ไม่มี field ไหนผูกกับ enum นี้` (WARN) |
| ใส่แถว `\| \`devfactory-core\` \| — \| ยังไม่มี repo` (repo ที่มีจริง) | `ghost: monthop-gmail/devfactory-core: ทะเบียนเขียนว่า "ยังไม่มี repo" แต่ repo มีอยู่จริงแล้ว` |
| ใช้ `consumers.md` ของ `main` ตอนที่ `enterprise-knowledge` ยังเป็น ghost row | `ghost: monthop-gmail/enterprise-knowledge: …` — **เคสจริงที่เคยหลุด** |
| แถวชี้ `/blob/main/` ทั้งที่ manifest อยู่บน `v2` | `registry: … อ่าน platform-contract.yaml ที่ ref \`main\` ไม่ได้: HTTP Error 404` |
| แถวชี้ ref ที่ไม่มีอยู่จริง | เหมือนกัน — **พิสูจน์ว่า ref ถูกใช้จริง ไม่ได้ถูกเมิน** |
| `urlopen` โยน `URLError` (connection reset) | **WARN ไม่ใช่ FAIL** · และเรียกซ้ำ 3 ครั้งต่อ repo — พิสูจน์ว่า retry ทำงาน |
| `urlopen` โยน `HTTPError` **404** | **FAIL** · เรียกครั้งเดียวต่อ repo — พิสูจน์ว่า 404 ไม่ retry |
| `urlopen` โยน `HTTPError` **503** | **WARN ไม่ใช่ FAIL** — เซิร์ฟเวอร์ตอบแต่ไม่ได้บอกว่าไฟล์ไม่มี · เคสนี้จับบั๊กในแพตช์แรกได้จริง |

เคสที่ **binding** เพิ่มเข้ามาเพราะ check ที่มีอยู่จับไม่ได้: `EventType` มี 7 ค่าครบตามที่ต้นทางบังคับทุกตัว จึงผ่าน check ที่เทียบ *ค่าที่มี* — แต่ field ยังผูกกับ enum ปิด ทำให้ค่านอกลิสต์ validate ไม่ผ่าน **check ที่เทียบค่าอย่างเดียวมองไม่เห็นความปิดของ enum**

เคสที่สามคือ `AUTO_APPROVE` ที่ [RFC-0009](https://github.com/monthop-gmail/devfactory-core/blob/main/rfcs/0009-vocabulary-extension.md) ยกมาเป็นเหตุผลว่าทำไม decision vocabulary ต้องเป็นชุดปิด — เป็นเส้นทางที่เปิดได้ด้วยการ *เพิ่ม* ค่าอย่างเดียว โดยไม่ต้องลบหรือเปลี่ยนชื่ออะไรเลย

## FAIL แล้วทำยังไง

**ห้าม disable check เพื่อให้ผ่าน** — FAIL คือ out of conformance ตาม [ADR-0006](../decisions/0006-contract-versioning.md)

| FAIL ที่ | แก้ยังไง |
| --- | --- |
| `derived` — pin ไม่ตรง | อ่าน RFC ที่ต้นทางว่าเปลี่ยนอะไร แล้วอัปเดต schema + `derived_from` ให้ตรง |
| `frozen` — ขาด/เกิน | ถ้าตั้งใจให้ต่าง ต้องมี RFC ที่ต้นทางก่อน (semantic change ตาม RFC-0005 Rule 2) |
| `binding` | แยก `$defs` ที่เป็น *ชุดค่าที่รู้จัก* ออกจาก `$defs` ที่ *field อ้าง* — ดู `EventType` vs `EventTypeName` ใน `event/v1` |
| `registry` | อัปเดต `architecture/consumers.md` ให้ตรง manifest |
| `schema` / `profile` | แก้ไฟล์ที่พัง |

เคสสุดท้ายเป็นของจริง ไม่ใช่ของสมมติ — `enterprise-knowledge` เกิดเป็น repo วันที่ 2026-08-20 และทะเบียนยังเขียนว่า "ยังไม่มี repo" อยู่หนึ่งวันเต็ม **เจอด้วยตาคน ไม่ใช่ด้วย check** · check ข้อ 8 มีอยู่เพื่อไม่ให้ครั้งหน้าต้องพึ่งตาคนอีก · ตอนนี้ยังมีอีก 6 แถวที่เปิดช่องเดียวกัน
