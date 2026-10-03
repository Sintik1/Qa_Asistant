-- DZ step 5: close Storage RLS gaps (debug update/delete, exports update).
-- Path isolation: first folder segment must equal auth.uid().

create policy debug_storage_update on storage.objects
  for update
  using (
    bucket_id = 'debug'
    and (storage.foldername(name))[1] = (auth.uid())::text
  )
  with check (
    bucket_id = 'debug'
    and (storage.foldername(name))[1] = (auth.uid())::text
  );

create policy debug_storage_delete on storage.objects
  for delete
  using (
    bucket_id = 'debug'
    and (storage.foldername(name))[1] = (auth.uid())::text
  );

create policy exports_storage_update on storage.objects
  for update
  using (
    bucket_id = 'exports'
    and (storage.foldername(name))[1] = (auth.uid())::text
  )
  with check (
    bucket_id = 'exports'
    and (storage.foldername(name))[1] = (auth.uid())::text
  );
