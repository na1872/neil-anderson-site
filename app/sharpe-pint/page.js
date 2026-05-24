'use client'

import { useEffect, useMemo, useState } from 'react'

const DATA_ROOT = '/sharpe-pint/data'

function escapeText(value = '') {
  return String(value)
}

function formatIssueDate(value) {
  if (!value) return 'Latest issue'
  const date = new Date(`${value}T00:00:00`)
  if (Number.isNaN(date.getTime())) return value
  return new Intl.DateTimeFormat('en-GB', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  }).format(date)
}

function formatGeneratedTime(value) {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return new Intl.DateTimeFormat('en-GB', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

function displayTitle(title = '') {
  return title.replace(/^The Sharpe Pint:\s*/i, '').trim() || title
}

function countSources(sections = []) {
  return sections.reduce((total, section) => total + (section.sources?.length || 0), 0)
}

function sourceLabel(source) {
  const title = source.title || source.publisher || source.url || 'Source'
  const publisher = source.publisher ? `, ${source.publisher}` : ''
  const published = source.published_date ? `, ${source.published_date}` : ''
  return `${title}${publisher}${published}`
}

function ContentBlocks({ blocks = [] }) {
  return blocks.map((block, index) => {
    const key = `${block.type || 'paragraph'}-${index}`

    if (block.type === 'heading') return <h3 key={key}>{escapeText(block.text)}</h3>
    if (block.type === 'quote') return <blockquote key={key}>{escapeText(block.text)}</blockquote>
    if (block.type === 'code') {
      return (
        <pre key={key}>
          <code>{block.text || ''}</code>
        </pre>
      )
    }
    if (block.type === 'bullets') {
      return (
        <ul key={key}>
          {(block.items || []).map((item, itemIndex) => (
            <li key={itemIndex}>{escapeText(item)}</li>
          ))}
        </ul>
      )
    }
    return <p key={key}>{escapeText(block.text || '')}</p>
  })
}

function Sources({ sources = [] }) {
  if (!sources.length) return null

  return (
    <aside className="sp-sources">
      <h3>Sources</h3>
      <ul className="sp-source-list">
        {sources.map((source, index) => {
          const label = sourceLabel(source)
          return (
            <li key={`${source.url || label}-${index}`}>
              {source.url ? (
                <a href={source.url} target="_blank" rel="noopener noreferrer">
                  {label}
                </a>
              ) : (
                label
              )}
              {source.note ? <span className="sp-source-note">{source.note}</span> : null}
            </li>
          )
        })}
      </ul>
    </aside>
  )
}

export default function SharpePintPage() {
  const [index, setIndex] = useState(null)
  const [selectedFile, setSelectedFile] = useState('')
  const [briefing, setBriefing] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    async function loadIndex() {
      try {
        const response = await fetch(`${DATA_ROOT}/index.json`, { cache: 'no-store' })
        if (!response.ok) throw new Error(`HTTP ${response.status}`)
        const data = await response.json()
        setIndex(data)
        setSelectedFile(data.latest || 'latest.json')
      } catch (err) {
        setError('No briefing data found.')
      }
    }

    loadIndex()
  }, [])

  useEffect(() => {
    if (!selectedFile) return

    async function loadBriefing() {
      try {
        const response = await fetch(`${DATA_ROOT}/${encodeURIComponent(selectedFile)}`, { cache: 'no-store' })
        if (!response.ok) throw new Error(`HTTP ${response.status}`)
        setBriefing(await response.json())
        setError('')
      } catch (err) {
        setError('Could not load this issue.')
      }
    }

    loadBriefing()
  }, [selectedFile])

  const issueOptions = useMemo(() => index?.issues || [], [index])

  return (
    <main className="sp-page">
      <header className="sp-hero">
        <div className="sp-hero-shade" />
        <nav className="sp-topbar" aria-label="Site">
          <a className="sp-brand" href="/">Neil Anderson</a>
          <span>The Sharpe Pint</span>
        </nav>
        <div className="sp-hero-content">
          <p className="sp-kicker">Daily markets briefing</p>
          <h1>Finance ideas, market moves, and useful edges.</h1>
          <p>A concise read for markets, investing, quant notes, and business psychology.</p>
        </div>
      </header>

      <div className="sp-shell">
        <section className="sp-article-head" aria-label="Issue details">
          <div className="sp-article-copy">
            <p className="sp-article-date">{formatIssueDate(briefing?.date)}</p>
            <h2>{displayTitle(briefing?.title || 'Loading')}</h2>
          </div>
          <div className="sp-tools">
            <label className="sp-picker" htmlFor="issue-select">
              <span>Archive</span>
              <select
                id="issue-select"
                value={selectedFile}
                onChange={(event) => setSelectedFile(event.target.value)}
                disabled={!issueOptions.length}
              >
                {issueOptions.length ? (
                  issueOptions.map((issue, position) => (
                    <option key={issue.file} value={issue.file}>
                      {position === 0 ? 'Latest: ' : ''}
                      {formatIssueDate(issue.date)}, {formatGeneratedTime(issue.generated_at)}
                    </option>
                  ))
                ) : (
                  <option>Latest issue</option>
                )}
              </select>
            </label>
            <div>
              <span>Sources</span>
              <strong>{briefing?.metadata?.source_count ?? countSources(briefing?.sections)}</strong>
            </div>
            <div>
              <span>Generated</span>
              <strong>{formatGeneratedTime(briefing?.metadata?.generated_at)}</strong>
            </div>
          </div>
        </section>

        {error ? <div className="sp-status">{error}</div> : null}

        {briefing ? (
          <article className="sp-briefing">
            <section className="sp-section sp-section-opening">
              <p className="sp-section-eyebrow">Opening mood</p>
              <div className="sp-content">
                <ContentBlocks blocks={briefing.opening_mood || []} />
              </div>
            </section>

            {(briefing.sections || []).map((section) => (
              <section className="sp-section" key={section.id || section.title}>
                <h2>{section.title || 'Untitled section'}</h2>
                <div className="sp-content">
                  <ContentBlocks blocks={section.content || []} />
                </div>
                <Sources sources={section.sources || []} />
              </section>
            ))}

            {briefing.stuff_worth_remembering?.length ? (
              <section className="sp-section sp-section-memory">
                <h2>Stuff Worth Remembering Today</h2>
                <ul className="sp-memory-list">
                  {briefing.stuff_worth_remembering.map((item, index) => (
                    <li key={index}>{item}</li>
                  ))}
                </ul>
              </section>
            ) : null}
          </article>
        ) : null}
      </div>
    </main>
  )
}
