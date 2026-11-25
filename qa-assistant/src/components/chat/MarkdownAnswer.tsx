import type { ReactNode } from 'react'

const INLINE_RE =
  /(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`|\[[^\]]+\]\([^)\s]+\))/g

function renderInline(text: string, keyPrefix: string): ReactNode[] {
  const nodes: ReactNode[] = []
  let last = 0
  let index = 0
  for (const match of text.matchAll(INLINE_RE)) {
    const start = match.index ?? 0
    if (start > last) {
      nodes.push(text.slice(last, start))
    }
    const token = match[0]
    const key = `${keyPrefix}-${index}`
    index += 1
    if (token.startsWith('**')) {
      nodes.push(<strong key={key}>{token.slice(2, -2)}</strong>)
    } else if (token.startsWith('`')) {
      nodes.push(
        <code key={key} className="rounded bg-slate-100 px-1">
          {token.slice(1, -1)}
        </code>,
      )
    } else if (token.startsWith('[')) {
      const label = token.slice(1, token.indexOf(']'))
      const href = token.slice(token.indexOf('](') + 2, -1)
      const safe = href.startsWith('https://') || href.startsWith('http://')
      nodes.push(
        safe ? (
          <a key={key} href={href} className="text-violet-700 underline" target="_blank" rel="noreferrer">
            {label}
          </a>
        ) : (
          <span key={key}>{label}</span>
        ),
      )
    } else {
      nodes.push(<em key={key}>{token.slice(1, -1)}</em>)
    }
    last = start + token.length
  }
  if (last < text.length) {
    nodes.push(text.slice(last))
  }
  return nodes
}

function isOrdered(line: string): boolean {
  return /^\d+\.\s+\S/.test(line)
}

function isBullet(line: string): boolean {
  return /^[-*]\s+\S/.test(line)
}

function isTableRow(line: string): boolean {
  const trimmed = line.trim()
  return trimmed.startsWith('|') && trimmed.endsWith('|') && trimmed.slice(1, -1).includes('|')
}

function isTableRule(line: string): boolean {
  return /^\|\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|$/.test(line.trim())
}

function tableCells(line: string): string[] {
  const body = line.trim().replace(/^\|/, '').replace(/\|$/, '')
  return body.split('|').map((cell) => cell.trim().replace(/\\\|/g, '|'))
}

function renderCell(text: string, keyPrefix: string): ReactNode {
  const parts = text.split(/<br\s*\/?>/i)
  return parts.map((part, index) => (
    <span key={`${keyPrefix}-${index}`}>
      {index > 0 ? <br /> : null}
      {renderInline(part, `${keyPrefix}-${index}`)}
    </span>
  ))
}

export function MarkdownAnswer({ text }: { text: string }) {
  const lines = text.replace(/\r\n/g, '\n').split('\n')
  const blocks: ReactNode[] = []
  let index = 0

  while (index < lines.length) {
    const line = lines[index]
    const key = `b-${index}`
    if (!line.trim()) {
      blocks.push(<div key={key} className="h-3" />)
      index += 1
      continue
    }
    const heading = /^(#{1,6})\s+(\S.*)$/.exec(line)
    if (heading) {
      const level = heading[1].length
      const className =
        level <= 2 ? 'mb-2 text-base font-semibold text-slate-900' : 'mb-1 text-sm font-semibold text-slate-900'
      blocks.push(
        <p key={key} className={className}>
          {renderInline(heading[2], key)}
        </p>,
      )
      index += 1
      continue
    }
    if (isTableRow(line)) {
      const raw: string[][] = []
      const start = index
      while (index < lines.length && isTableRow(lines[index])) {
        if (!isTableRule(lines[index])) {
          raw.push(tableCells(lines[index]))
        }
        index += 1
      }
      const [header, ...body] = raw
      if (header) {
        blocks.push(
          <div key={`table-${start}`} className="mb-2 overflow-x-auto">
            <table className="w-full border-collapse text-left text-sm">
              <thead>
                <tr>
                  {header.map((cell, cellIndex) => (
                    <th
                      key={`${key}-h-${cellIndex}`}
                      className="border border-slate-200 bg-slate-50 px-2 py-1 font-semibold text-slate-900"
                    >
                      {renderCell(cell, `${key}-h-${cellIndex}`)}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {body.map((row, rowIndex) => (
                  <tr key={`${key}-r-${rowIndex}`}>
                    {row.map((cell, cellIndex) => (
                      <td
                        key={`${key}-${rowIndex}-${cellIndex}`}
                        className="border border-slate-200 px-2 py-1 align-top text-slate-800"
                      >
                        {renderCell(cell, `${key}-${rowIndex}-${cellIndex}`)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>,
        )
      }
      continue
    }
    if (isOrdered(line) || isBullet(line)) {
      const ordered = isOrdered(line)
      const items: ReactNode[] = []
      const start = index
      while (index < lines.length && (ordered ? isOrdered(lines[index]) : isBullet(lines[index]))) {
        const item = lines[index].replace(ordered ? /^\d+\.\s+/ : /^[-*]\s+/, '')
        items.push(<li key={`${key}-${index}`}>{renderInline(item, `${key}-${index}`)}</li>)
        index += 1
      }
      const List = ordered ? 'ol' : 'ul'
      blocks.push(
        <List
          key={`list-${start}`}
          className={`mb-2 space-y-1 pl-5 ${ordered ? 'list-decimal' : 'list-disc'}`}
        >
          {items}
        </List>,
      )
      continue
    }
    blocks.push(
      <p key={key} className="mb-1 last:mb-0">
        {renderInline(line, key)}
      </p>,
    )
    index += 1
  }

  return <div className="text-slate-800">{blocks}</div>
}
