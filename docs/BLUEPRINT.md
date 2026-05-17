# Khatabook SaaS — High-End Blueprint v1

## 1) Product Scope

### Core Modules
1. Tenant/workspace management (business + branches)
2. Party ledger (customer/supplier)
3. Debit/credit entries and running balance
4. Settlements and partial payments
5. Reminder automation (SMS/WhatsApp/Email)
6. Reports (aging, receivables/payables, exports)
7. Subscription plans, quotas, and billing lifecycle
8. Admin console (support, audit, operations)

## 2) Architecture

- **Frontend:** Next.js + TypeScript
- **Backend:** API layer with modular services
- **Database:** PostgreSQL + Prisma ORM
- **Auth:** JWT/session provider + tenant memberships
- **Billing:** Stripe subscriptions + webhook processing
- **Queue/Jobs:** Redis-backed worker for reminders/reports
- **Storage:** Object storage for attachments/invoices
- **Observability:** logs, tracing, errors, metrics

## 3) Multi-tenant Data Strategy

- Shared database model with strict `tenant_id` scoping.
- Row-level access constraints in data layer.
- Every business table includes:
  - `tenant_id`
  - `created_at`
  - `updated_at`
  - `created_by` (where applicable)

## 4) Data Consistency Rules

- Money mutations are append-only through ledger entries.
- Balances are derived from ledger entry totals.
- Payment updates create compensating entries; no silent rewrites.
- All external webhook events are idempotent.

## 5) Security Baseline

- Role-based access: Owner/Admin/Staff/ReadOnly
- Secrets in env manager; no client exposure
- Request rate limiting (IP + tenant + user)
- Audit logs for all financial mutations
- Signed webhook verification
- Backup and restore drills

## 6) SLA & Performance Targets

- Uptime objective: 99.9%
- P95 read latency: <250ms
- P95 write latency: <400ms
- Export and reminder jobs are asynchronous

## 7) API Domain Boundaries

- `auth/*`
- `tenants/*`
- `parties/*`
- `ledger/*`
- `payments/*`
- `reports/*`
- `billing/*`
- `admin/*`

## 8) 90-Day Delivery Plan

### Phase 0 (Week 1–2)
- Final schema and architecture freeze
- Auth + tenant membership foundation
- CI, linting, test harness, migration pipeline

### Phase 1 (Week 3–6)
- Parties, ledger entries, settlements
- Dashboard and report v1
- Reminder job pipeline

### Phase 2 (Week 7–9)
- Stripe subscriptions + quotas
- Trial and dunning lifecycle
- Admin controls + audit enhancement

### Phase 3 (Week 10–12)
- Security hardening
- Load/perf optimization
- Release readiness and go-live checklist
