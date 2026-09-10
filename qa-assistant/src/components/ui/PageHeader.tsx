interface PageHeaderProps {
  title: string
  description?: string
}

export function PageHeader({ title, description }: PageHeaderProps) {
  return (
    <header className="mb-6">
      <h1 className="text-2xl font-bold text-slate-900 md:text-3xl">{title}</h1>
      {description ? (
        <p className="mt-2 text-sm text-slate-600 md:text-base">{description}</p>
      ) : null}
    </header>
  )
}
