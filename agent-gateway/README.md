# agent-gateway

ทางเข้าเดียวของทุก agent traffic

## Scope
- authentication / authorization ของ caller
- routing ไปยัง runtime ที่เหมาะสม
- rate limit, quota, tenant isolation
- request/response normalization

## Status
นิยามขอบเขตเท่านั้น — repo นี้ไม่ implement, code จริงอยู่ใน product repo ที่ consume module นี้
