-- DVOP Productivity Command Center cloud sync schema
-- Run this in Supabase SQL Editor after creating your project.

create table if not exists public.dvop_dashboard_states (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  app_key text not null default 'dvop-command-center-main',
  data jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (user_id, app_key)
);

alter table public.dvop_dashboard_states enable row level security;

drop policy if exists "Users can view their own dashboard state" on public.dvop_dashboard_states;
create policy "Users can view their own dashboard state"
on public.dvop_dashboard_states
for select
to authenticated
using ((select auth.uid()) = user_id);

drop policy if exists "Users can insert their own dashboard state" on public.dvop_dashboard_states;
create policy "Users can insert their own dashboard state"
on public.dvop_dashboard_states
for insert
to authenticated
with check ((select auth.uid()) = user_id);

drop policy if exists "Users can update their own dashboard state" on public.dvop_dashboard_states;
create policy "Users can update their own dashboard state"
on public.dvop_dashboard_states
for update
to authenticated
using ((select auth.uid()) = user_id)
with check ((select auth.uid()) = user_id);

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists set_dvop_dashboard_states_updated_at on public.dvop_dashboard_states;
create trigger set_dvop_dashboard_states_updated_at
before update on public.dvop_dashboard_states
for each row
execute function public.set_updated_at();
