-- Demo reviewer account for graders (Supabase SQL Editor / MCP).
-- Email: demo.reviewer@qatest.local
-- Password: DemoReviewer-2026!
-- Safe to re-run: updates password + confirms email if user exists.

DO $$
DECLARE
  new_id uuid := gen_random_uuid();
BEGIN
  IF EXISTS (SELECT 1 FROM auth.users WHERE email = 'demo.reviewer@qatest.local') THEN
    UPDATE auth.users
      SET encrypted_password = crypt('DemoReviewer-2026!', gen_salt('bf')),
          email_confirmed_at = COALESCE(email_confirmed_at, now()),
          updated_at = now()
    WHERE email = 'demo.reviewer@qatest.local';
  ELSE
    INSERT INTO auth.users (
      instance_id, id, aud, role, email, encrypted_password, email_confirmed_at,
      raw_app_meta_data, raw_user_meta_data, created_at, updated_at,
      confirmation_token, recovery_token, email_change_token_new, email_change
    ) VALUES (
      '00000000-0000-0000-0000-000000000000',
      new_id,
      'authenticated',
      'authenticated',
      'demo.reviewer@qatest.local',
      crypt('DemoReviewer-2026!', gen_salt('bf')),
      now(),
      '{"provider":"email","providers":["email"]}'::jsonb,
      '{"display_name":"Demo Reviewer"}'::jsonb,
      now(),
      now(),
      '', '', '', ''
    );
    INSERT INTO auth.identities (
      id, user_id, identity_data, provider, provider_id, last_sign_in_at, created_at, updated_at
    ) VALUES (
      new_id,
      new_id,
      jsonb_build_object('sub', new_id::text, 'email', 'demo.reviewer@qatest.local'),
      'email',
      new_id::text,
      now(),
      now(),
      now()
    );
  END IF;
END $$;
