import type { HistoryItem, SubtitleSegment } from '../types'

interface ExportPair {
  source: string
  target: string
  segmentId?: string
  corrected?: boolean
}

interface ExportTextOptions {
  title: string
  sessionId?: string
  items: ExportPair[]
}

function sanitizeFilenamePart(value: string) {
  return value.replace(/[\\/:*?"<>|\s]+/g, '-').replace(/^-+|-+$/g, '') || 'subtitles'
}

function formatTimestamp(date = new Date()) {
  const pad = (value: number) => String(value).padStart(2, '0')
  return [
    date.getFullYear(),
    pad(date.getMonth() + 1),
    pad(date.getDate()),
  ].join('') + '-' + [pad(date.getHours()), pad(date.getMinutes()), pad(date.getSeconds())].join('')
}

function buildSubtitleText({ title, sessionId, items }: ExportTextOptions) {
  const lines = [
    title,
    sessionId ? `Session: ${sessionId}` : '',
    `Exported At: ${new Date().toLocaleString()}`,
    '',
  ].filter(Boolean)

  if (items.length === 0) {
    lines.push('暂无可导出的字幕。')
    return lines.join('\n')
  }

  items.forEach((item, index) => {
    lines.push(`[${index + 1}]${item.segmentId ? ` ${item.segmentId}` : ''}${item.corrected ? ' [已修正]' : ''}`)
    lines.push(`原文：${item.source || '-'}`)
    lines.push(`译文：${item.target || '-'}`)
    lines.push('')
  })

  return lines.join('\n')
}

function downloadText(filename: string, content: string) {
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = filename
  document.body.appendChild(anchor)
  anchor.click()
  anchor.remove()
  URL.revokeObjectURL(url)
}

export function exportSubtitleSegmentsToTxt(sessionId: string, segments: SubtitleSegment[]) {
  const sorted = [...segments].sort((a, b) => a.segmentId.localeCompare(b.segmentId))
  const content = buildSubtitleText({
    title: 'LinguaFlow 实时字幕导出',
    sessionId,
    items: sorted.map((segment) => ({
      segmentId: segment.segmentId,
      source: segment.source,
      target: segment.target,
      corrected: segment.corrected,
    })),
  })
  const filename = `linguaflow-${sanitizeFilenamePart(sessionId)}-${formatTimestamp()}.txt`
  downloadText(filename, content)
}

export function exportHistoryItemsToTxt(items: HistoryItem[], label = 'history') {
  const content = buildSubtitleText({
    title: 'LinguaFlow 历史字幕导出',
    sessionId: label,
    items: items.map((item) => ({
      segmentId: item.segment_id,
      source: item.source_text,
      target: item.target_text,
      corrected: item.corrected,
    })),
  })
  const filename = `linguaflow-${sanitizeFilenamePart(label)}-${formatTimestamp()}.txt`
  downloadText(filename, content)
}
