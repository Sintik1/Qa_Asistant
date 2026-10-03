-- Harden trigger functions (also applied remotely as harden_auth_triggers)
-- Keep in sync with cloud for fresh environments that apply init after this patch.

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

revoke all on function public.handle_new_user() from public;
revoke all on function public.handle_new_user() from anon, authenticated;
revoke all on function public.set_updated_at() from public;
revoke all on function public.set_updated_at() from anon, authenticated;
