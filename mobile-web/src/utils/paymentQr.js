function hashString(text) {
  let hash = 2166136261
  for (let i = 0; i < text.length; i += 1) {
    hash ^= text.charCodeAt(i)
    hash = Math.imul(hash, 16777619)
  }
  return hash >>> 0
}

function mulberry32(seed) {
  let value = seed >>> 0
  return () => {
    value += 0x6D2B79F5
    let t = value
    t = Math.imul(t ^ (t >>> 15), t | 1)
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61)
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

function isFinderArea(x, y, size) {
  const areas = [
    { x: 0, y: 0 },
    { x: size - 7, y: 0 },
    { x: 0, y: size - 7 },
  ]
  return areas.some((area) => x >= area.x && x < area.x + 7 && y >= area.y && y < area.y + 7)
}

function finderRect(x, y, cell, fill) {
  return [
    `<rect x="${x * cell}" y="${y * cell}" width="${7 * cell}" height="${7 * cell}" fill="${fill}" />`,
    `<rect x="${(x + 1) * cell}" y="${(y + 1) * cell}" width="${5 * cell}" height="${5 * cell}" fill="#ffffff" />`,
    `<rect x="${(x + 2) * cell}" y="${(y + 2) * cell}" width="${3 * cell}" height="${3 * cell}" fill="${fill}" />`,
  ].join('')
}

export function createPaymentQrDataUrl(payload, sizePx = 170) {
  const gridSize = 21
  const quietZone = 2
  const totalCells = gridSize + quietZone * 2
  const cell = Math.max(4, Math.round(sizePx / totalCells))
  const totalSize = totalCells * cell
  const seed = hashString(payload)
  const random = mulberry32(seed)
  const modules = []

  for (let y = 0; y < gridSize; y += 1) {
    for (let x = 0; x < gridSize; x += 1) {
      if (isFinderArea(x, y, gridSize)) continue

      if (x === 6 || y === 6) {
        const isDark = (x + y) % 2 === 0
        if (isDark) {
          modules.push(
            `<rect x="${(x + quietZone) * cell}" y="${(y + quietZone) * cell}" width="${cell}" height="${cell}" fill="#1f1f1f" />`
          )
        }
        continue
      }

      const noise = random()
      const shouldFill = noise > 0.48 || ((x * 3 + y * 5 + seed) % 11 === 0)
      if (!shouldFill) continue

      modules.push(
        `<rect x="${(x + quietZone) * cell}" y="${(y + quietZone) * cell}" width="${cell}" height="${cell}" fill="#1f1f1f" />`
      )
    }
  }

  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="${totalSize}" height="${totalSize}" viewBox="0 0 ${totalSize} ${totalSize}" shape-rendering="crispEdges">
      <rect width="${totalSize}" height="${totalSize}" fill="#ffffff" />
      <rect x="${quietZone * cell}" y="${quietZone * cell}" width="${gridSize * cell}" height="${gridSize * cell}" fill="#ffffff" />
      ${finderRect(quietZone, quietZone, cell, "#1f1f1f")}
      ${finderRect(quietZone + gridSize - 7, quietZone, cell, "#1f1f1f")}
      ${finderRect(quietZone, quietZone + gridSize - 7, cell, "#1f1f1f")}
      ${modules.join('')}
    </svg>
  `.replace(/\s+/g, ' ')

  return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`
}
