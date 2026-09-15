import type { ReactNode } from 'react'

interface UploadSectionProps {
  children: ReactNode
}

export function UploadSection({ children }: UploadSectionProps) {
  return (
    <section className="space-y-4 rounded-md border border-dashed border-violet-400 p-3 sm:p-4 md:p-5">
      <h2 className="text-base font-semibold text-violet-700">Загрузка файлов</h2>
      {children}
    </section>
  )
}
