# Supabase (QA Assistant)

Миграции схемы **Variant B (Operational)**.

## Apply

```bash
# Option 1: Supabase CLI (linked project)
supabase db push

# Option 2: Dashboard → SQL Editor → paste
# supabase/migrations/20260928143000_init_variant_b.sql
```

Полные инструкции — в корневом `backend_documentation.md` (§2 после шага 3 ДЗ; безопасность — §1.8).

Миграции:
- `20260928143000_init_variant_b.sql` — схема + RLS + signup trigger
- `20260928140000_harden_auth_triggers.sql` — hardening SECURITY DEFINER
- `20261003183000_security_storage_policies.sql` — Storage RLS gaps (шаг 5)
