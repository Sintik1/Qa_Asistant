-- QA Assistant — Variant B (Operational)
-- Tables: profiles, user_settings, documents, generation_runs,
--         generation_chunks, test_cases
-- Target: Supabase Postgres + auth.users; file bodies in Storage (paths in columns)

create extension if not exists "pgcrypto";

-- ---------------------------------------------------------------------------
-- Helpers
-- ---------------------------------------------------------------------------

create or replace function public.set_updated_at()
returns trigger
language plpgsql
set search_path = public
as $$
begin
  new.updated_at = timezone('utc', now());
  return new;
end;
$$;

-- ---------------------------------------------------------------------------
-- Enums
-- ---------------------------------------------------------------------------

do $$ begin
  create type public.document_status as enum ('uploaded', 'parsed', 'failed');
exception when duplicate_object then null;
end $$;

do $$ begin
  create type public.run_status as enum (
    'pending', 'extracting', 'chunking', 'calling_ai',
    'validating', 'done', 'failed'
  );
exception when duplicate_object then null;
end $$;

do $$ begin
  create type public.chunk_status as enum (
    'pending', 'processing', 'done', 'failed', 'skipped'
  );
exception when duplicate_object then null;
end $$;

do $$ begin
  create type public.chunk_method as enum ('header', 'fixed', 'recursive');
exception when duplicate_object then null;
end $$;

-- ---------------------------------------------------------------------------
-- 1. profiles (1:1 auth.users)
-- ---------------------------------------------------------------------------

create table if not exists public.profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  display_name text,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);

create trigger profiles_set_updated_at
  before update on public.profiles
  for each row execute function public.set_updated_at();

-- ---------------------------------------------------------------------------
-- 2. user_settings (1:1 profiles)
-- Leopold API token is NOT stored here (see .env / Vault); only has_api_token.
-- ---------------------------------------------------------------------------

create table if not exists public.user_settings (
  user_id uuid primary key references public.profiles (id) on delete cascade,
  chunk_size integer not null default 4000
    check (chunk_size > 0 and chunk_size <= 100000),
  chunk_overlap integer not null default 200
    check (chunk_overlap >= 0 and chunk_overlap < chunk_size),
  chunk_method public.chunk_method not null default 'header',
  has_api_token boolean not null default false,
  updated_at timestamptz not null default timezone('utc', now())
);

create trigger user_settings_set_updated_at
  before update on public.user_settings
  for each row execute function public.set_updated_at();

-- Auto-create profile + default settings on signup
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.profiles (id, display_name)
  values (
    new.id,
    coalesce(new.raw_user_meta_data->>'display_name', split_part(new.email, '@', 1))
  )
  on conflict (id) do nothing;

  insert into public.user_settings (user_id)
  values (new.id)
  on conflict (user_id) do nothing;

  return new;
end;
$$;

revoke all on function public.handle_new_user() from public;
revoke all on function public.handle_new_user() from anon, authenticated;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- ---------------------------------------------------------------------------
-- 3. documents
-- ---------------------------------------------------------------------------

create table if not exists public.documents (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles (id) on delete cascade,
  original_filename text not null,
  mime_type text,
  size_bytes bigint not null
    check (size_bytes >= 0 and size_bytes <= 104857600), -- 100 MiB (TZ)
  storage_path text not null,
  status public.document_status not null default 'uploaded',
  page_count integer check (page_count is null or page_count >= 0),
  extracted_chars integer check (extracted_chars is null or extracted_chars >= 0),
  error_message text,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);

create index if not exists documents_user_id_created_at_idx
  on public.documents (user_id, created_at desc);

create trigger documents_set_updated_at
  before update on public.documents
  for each row execute function public.set_updated_at();

-- ---------------------------------------------------------------------------
-- 4. generation_runs
-- ---------------------------------------------------------------------------

create table if not exists public.generation_runs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles (id) on delete cascade,
  document_id uuid not null references public.documents (id) on delete cascade,
  status public.run_status not null default 'pending',
  chunk_size integer not null default 4000 check (chunk_size > 0),
  chunk_overlap integer not null default 200 check (chunk_overlap >= 0),
  chunk_method public.chunk_method not null default 'header',
  error_code text,
  error_message text,
  result_csv_path text,
  case_count integer not null default 0 check (case_count >= 0),
  started_at timestamptz not null default timezone('utc', now()),
  finished_at timestamptz,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now()),
  constraint generation_runs_finished_after_start
    check (finished_at is null or finished_at >= started_at)
);

create index if not exists generation_runs_user_id_created_at_idx
  on public.generation_runs (user_id, created_at desc);

create index if not exists generation_runs_document_id_idx
  on public.generation_runs (document_id);

create trigger generation_runs_set_updated_at
  before update on public.generation_runs
  for each row execute function public.set_updated_at();

-- ---------------------------------------------------------------------------
-- 5. generation_chunks
-- ---------------------------------------------------------------------------

create table if not exists public.generation_chunks (
  id uuid primary key default gen_random_uuid(),
  run_id uuid not null references public.generation_runs (id) on delete cascade,
  user_id uuid not null references public.profiles (id) on delete cascade,
  chunk_index integer not null check (chunk_index >= 0),
  content_preview text,
  storage_path text,
  status public.chunk_status not null default 'pending',
  retry_count integer not null default 0
    check (retry_count >= 0 and retry_count <= 10),
  raw_response_path text,
  error_message text,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now()),
  unique (run_id, chunk_index)
);

create index if not exists generation_chunks_run_id_idx
  on public.generation_chunks (run_id);

create trigger generation_chunks_set_updated_at
  before update on public.generation_chunks
  for each row execute function public.set_updated_at();

-- ---------------------------------------------------------------------------
-- 6. test_cases (CSV: Name, Status, Step, Expected Result)
-- ---------------------------------------------------------------------------

create table if not exists public.test_cases (
  id uuid primary key default gen_random_uuid(),
  run_id uuid not null references public.generation_runs (id) on delete cascade,
  user_id uuid not null references public.profiles (id) on delete cascade,
  chunk_id uuid references public.generation_chunks (id) on delete set null,
  name text not null,
  status text not null default 'Approved',
  step text not null,
  expected_result text not null,
  sort_order integer not null default 0 check (sort_order >= 0),
  created_at timestamptz not null default timezone('utc', now()),
  constraint test_cases_nonempty_step check (length(trim(step)) > 0)
);

create index if not exists test_cases_run_id_sort_idx
  on public.test_cases (run_id, sort_order);

create index if not exists test_cases_user_id_idx
  on public.test_cases (user_id);

-- ---------------------------------------------------------------------------
-- RLS: owner isolation (Auth UX / CORS refined in DZ step 5)
-- ---------------------------------------------------------------------------

alter table public.profiles enable row level security;
alter table public.user_settings enable row level security;
alter table public.documents enable row level security;
alter table public.generation_runs enable row level security;
alter table public.generation_chunks enable row level security;
alter table public.test_cases enable row level security;

create policy profiles_select_own on public.profiles
  for select using (id = auth.uid());
create policy profiles_update_own on public.profiles
  for update using (id = auth.uid()) with check (id = auth.uid());

create policy user_settings_select_own on public.user_settings
  for select using (user_id = auth.uid());
create policy user_settings_insert_own on public.user_settings
  for insert with check (user_id = auth.uid());
create policy user_settings_update_own on public.user_settings
  for update using (user_id = auth.uid()) with check (user_id = auth.uid());

create policy documents_select_own on public.documents
  for select using (user_id = auth.uid());
create policy documents_insert_own on public.documents
  for insert with check (user_id = auth.uid());
create policy documents_update_own on public.documents
  for update using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy documents_delete_own on public.documents
  for delete using (user_id = auth.uid());

create policy generation_runs_select_own on public.generation_runs
  for select using (user_id = auth.uid());
create policy generation_runs_insert_own on public.generation_runs
  for insert with check (user_id = auth.uid());
create policy generation_runs_update_own on public.generation_runs
  for update using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy generation_runs_delete_own on public.generation_runs
  for delete using (user_id = auth.uid());

create policy generation_chunks_select_own on public.generation_chunks
  for select using (user_id = auth.uid());
create policy generation_chunks_insert_own on public.generation_chunks
  for insert with check (user_id = auth.uid());
create policy generation_chunks_update_own on public.generation_chunks
  for update using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy generation_chunks_delete_own on public.generation_chunks
  for delete using (user_id = auth.uid());

create policy test_cases_select_own on public.test_cases
  for select using (user_id = auth.uid());
create policy test_cases_insert_own on public.test_cases
  for insert with check (user_id = auth.uid());
create policy test_cases_update_own on public.test_cases
  for update using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy test_cases_delete_own on public.test_cases
  for delete using (user_id = auth.uid());

grant usage on schema public to authenticated;
grant select, update on public.profiles to authenticated;
grant select, insert, update on public.user_settings to authenticated;
grant select, insert, update, delete on public.documents to authenticated;
grant select, insert, update, delete on public.generation_runs to authenticated;
grant select, insert, update, delete on public.generation_chunks to authenticated;
grant select, insert, update, delete on public.test_cases to authenticated;

comment on table public.profiles is 'App profile linked to auth.users';
comment on table public.user_settings is 'Per-user chunk defaults; Leopold token NOT stored';
comment on table public.documents is 'Requirements file metadata; body in Storage';
comment on table public.generation_runs is 'One generation session for a document';
comment on table public.generation_chunks is 'Per-chunk AI work + debug artifact paths';
comment on table public.test_cases is 'Normalized CSV rows for TestRail/Zephyr';
