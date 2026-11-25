-- Per-user prompt and scenario-template library.
-- Separate from case_chunks: saving a row must not change RAG retrieval.

create table if not exists public.user_prompts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles (id) on delete cascade,
  name text not null,
  content text not null,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now()),
  constraint user_prompts_name_len check (char_length(btrim(name)) between 1 and 200),
  constraint user_prompts_content_len check (char_length(content) between 1 and 20000),
  constraint user_prompts_user_name_unique unique (user_id, name)
);

create index if not exists user_prompts_user_created_idx
  on public.user_prompts (user_id, created_at desc);

create trigger user_prompts_set_updated_at
  before update on public.user_prompts
  for each row execute function public.set_updated_at();

create table if not exists public.scenario_templates (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles (id) on delete cascade,
  name text not null,
  content text not null,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now()),
  constraint scenario_templates_name_len check (char_length(btrim(name)) between 1 and 200),
  constraint scenario_templates_content_len check (char_length(content) between 1 and 20000),
  constraint scenario_templates_user_name_unique unique (user_id, name)
);

create index if not exists scenario_templates_user_created_idx
  on public.scenario_templates (user_id, created_at desc);

create trigger scenario_templates_set_updated_at
  before update on public.scenario_templates
  for each row execute function public.set_updated_at();

alter table public.user_prompts enable row level security;
alter table public.scenario_templates enable row level security;

create policy user_prompts_select_own on public.user_prompts
  for select using (user_id = auth.uid());
create policy user_prompts_insert_own on public.user_prompts
  for insert with check (user_id = auth.uid());
create policy user_prompts_update_own on public.user_prompts
  for update using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy user_prompts_delete_own on public.user_prompts
  for delete using (user_id = auth.uid());

create policy scenario_templates_select_own on public.scenario_templates
  for select using (user_id = auth.uid());
create policy scenario_templates_insert_own on public.scenario_templates
  for insert with check (user_id = auth.uid());
create policy scenario_templates_update_own on public.scenario_templates
  for update using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy scenario_templates_delete_own on public.scenario_templates
  for delete using (user_id = auth.uid());

grant select, insert, update, delete on public.user_prompts to authenticated, service_role;
grant select, insert, update, delete on public.scenario_templates to authenticated, service_role;

comment on table public.user_prompts is 'Named prompts the user inserts into a generation run';
comment on table public.scenario_templates is 'Named scenario templates applied only when the user selects them';
