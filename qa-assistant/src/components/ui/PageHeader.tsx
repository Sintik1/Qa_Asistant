interface PageHeaderProps {
  title: string
  description?: string
}

export function PageHeader({ title, description }: PageHeaderProps) {
  return (
    <header className="mb-4 sm:mb-6">
      <h1 className="text-xl font-bold text-slate-900 sm:text-2xl md:text-3xl">
        {title}
      </h1>
      {description ? (
        <p className="mt-2 text-sm leading-relaxed text-slate-600 md:text-base">
          {description}
        </p>
      ) : null}
    </header>
  )
}
