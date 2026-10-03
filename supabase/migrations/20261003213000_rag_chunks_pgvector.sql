-- RAG: durable document/case chunks + pgvector match RPCs
-- Applied remotely as rag_chunks_pgvector_v2

create extension if not exists vector with schema extensions;

create table if not exists public.document_chunks (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles (id) on delete cascade,
  document_id uuid not null references public.documents (id) on delete cascade,
  chunk_index integer not null check (chunk_index >= 0),
  section_number text,
  section_path text,
  title text,
  content text not null,
  metadata jsonb not null default '{}'::jsonb,
  embedding extensions.vector(768),
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now()),
  unique (document_id, chunk_index)
);

create index if not exists document_chunks_user_id_idx on public.document_chunks (user_id);
create index if not exists document_chunks_document_id_idx on public.document_chunks (document_id);
create index if not exists document_chunks_embedding_hnsw_idx
  on public.document_chunks
  using hnsw (embedding extensions.vector_cosine_ops);

drop trigger if exists document_chunks_set_updated_at on public.document_chunks;
create trigger document_chunks_set_updated_at
  before update on public.document_chunks
  for each row execute function public.set_updated_at();

create table if not exists public.case_chunks (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles (id) on delete cascade,
  source_type text not null default 'template'
    check (source_type in ('template', 'approved_case', 'anti_example')),
  test_case_id uuid references public.test_cases (id) on delete set null,
  name text not null,
  status text not null default 'Approved',
  step text not null default '',
  expected_result text not null default '',
  tags text[] not null default '{}',
  content text not null,
  metadata jsonb not null default '{}'::jsonb,
  embedding extensions.vector(768),
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);

create index if not exists case_chunks_user_id_idx on public.case_chunks (user_id);
create index if not exists case_chunks_source_type_idx on public.case_chunks (user_id, source_type);
create index if not exists case_chunks_embedding_hnsw_idx
  on public.case_chunks
  using hnsw (embedding extensions.vector_cosine_ops);

drop trigger if exists case_chunks_set_updated_at on public.case_chunks;
create trigger case_chunks_set_updated_at
  before update on public.case_chunks
  for each row execute function public.set_updated_at();

alter table public.document_chunks enable row level security;
alter table public.case_chunks enable row level security;

drop policy if exists document_chunks_select_own on public.document_chunks;
create policy document_chunks_select_own on public.document_chunks
  for select using (user_id = auth.uid());
drop policy if exists document_chunks_insert_own on public.document_chunks;
create policy document_chunks_insert_own on public.document_chunks
  for insert with check (user_id = auth.uid());
drop policy if exists document_chunks_update_own on public.document_chunks;
create policy document_chunks_update_own on public.document_chunks
  for update using (user_id = auth.uid()) with check (user_id = auth.uid());
drop policy if exists document_chunks_delete_own on public.document_chunks;
create policy document_chunks_delete_own on public.document_chunks
  for delete using (user_id = auth.uid());

drop policy if exists case_chunks_select_own on public.case_chunks;
create policy case_chunks_select_own on public.case_chunks
  for select using (user_id = auth.uid());
drop policy if exists case_chunks_insert_own on public.case_chunks;
create policy case_chunks_insert_own on public.case_chunks
  for insert with check (user_id = auth.uid());
drop policy if exists case_chunks_update_own on public.case_chunks;
create policy case_chunks_update_own on public.case_chunks
  for update using (user_id = auth.uid()) with check (user_id = auth.uid());
drop policy if exists case_chunks_delete_own on public.case_chunks;
create policy case_chunks_delete_own on public.case_chunks
  for delete using (user_id = auth.uid());

create or replace function public.match_document_chunks(
  query_embedding extensions.vector(768),
  match_count integer default 5,
  filter_user_id uuid default auth.uid(),
  exclude_document_id uuid default null,
  only_document_id uuid default null
)
returns table (
  id uuid,
  document_id uuid,
  section_number text,
  section_path text,
  title text,
  content text,
  metadata jsonb,
  similarity float
)
language sql
stable
security invoker
set search_path = public, extensions
as $$
  select
    dc.id,
    dc.document_id,
    dc.section_number,
    dc.section_path,
    dc.title,
    dc.content,
    dc.metadata,
    (1 - (dc.embedding <=> query_embedding))::float as similarity
  from public.document_chunks dc
  where dc.user_id = coalesce(filter_user_id, auth.uid())
    and dc.embedding is not null
    and (exclude_document_id is null or dc.document_id <> exclude_document_id)
    and (only_document_id is null or dc.document_id = only_document_id)
  order by dc.embedding <=> query_embedding
  limit greatest(coalesce(match_count, 5), 1);
$$;

create or replace function public.match_case_chunks(
  query_embedding extensions.vector(768),
  match_count integer default 5,
  filter_user_id uuid default auth.uid(),
  source_types text[] default array['template', 'approved_case']
)
returns table (
  id uuid,
  source_type text,
  name text,
  status text,
  step text,
  expected_result text,
  tags text[],
  content text,
  similarity float
)
language sql
stable
security invoker
set search_path = public, extensions
as $$
  select
    cc.id,
    cc.source_type,
    cc.name,
    cc.status,
    cc.step,
    cc.expected_result,
    cc.tags,
    cc.content,
    (1 - (cc.embedding <=> query_embedding))::float as similarity
  from public.case_chunks cc
  where cc.user_id = coalesce(filter_user_id, auth.uid())
    and cc.embedding is not null
    and (source_types is null or cc.source_type = any(source_types))
  order by cc.embedding <=> query_embedding
  limit greatest(coalesce(match_count, 5), 1);
$$;

grant execute on function public.match_document_chunks(extensions.vector, integer, uuid, uuid, uuid)
  to authenticated, service_role;
grant execute on function public.match_case_chunks(extensions.vector, integer, uuid, text[])
  to authenticated, service_role;
