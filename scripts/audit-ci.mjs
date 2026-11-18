import { spawnSync } from 'node:child_process'

// No patched picomatch release exists yet. Keep CI sensitive to every other
// high or critical advisory, including advisories in picomatch itself.
const allowedAdvisories = new Set([
  'https://github.com/advisories/GHSA-fc5q-39xc-vjpf',
])

const audit = spawnSync('npm', ['audit', '--json'], {
  encoding: 'utf8',
  maxBuffer: 10 * 1024 * 1024,
})

if (audit.error || ![0, 1].includes(audit.status)) {
  console.error(audit.error ?? audit.stderr ?? 'npm audit failed')
  process.exit(1)
}

let report
try {
  report = JSON.parse(audit.stdout)
} catch {
  console.error('npm audit did not return valid JSON')
  process.exit(1)
}

if (!report.vulnerabilities || !report.metadata?.vulnerabilities) {
  console.error('npm audit returned an unexpected report')
  process.exit(1)
}

const blockingSeverities = new Set(['high', 'critical'])
const failures = new Set()
const allowed = new Set()

function inspect(name, visited = new Set()) {
  if (visited.has(name)) return
  visited.add(name)

  const vulnerability = report.vulnerabilities[name]
  if (!vulnerability || !Array.isArray(vulnerability.via)) {
    failures.add(`Unknown vulnerability chain: ${name}`)
    return
  }

  for (const source of vulnerability.via) {
    if (typeof source === 'string') {
      inspect(source, visited)
    } else if (blockingSeverities.has(source.severity)) {
      if (allowedAdvisories.has(source.url)) {
        allowed.add(source.url)
      } else {
        failures.add(`${name}: ${source.url ?? source.title ?? 'unknown advisory'}`)
      }
    }
  }
}

for (const [name, vulnerability] of Object.entries(report.vulnerabilities)) {
  if (blockingSeverities.has(vulnerability.severity)) inspect(name)
}

for (const url of allowed) console.log(`Temporarily allowed: ${url}`)
for (const failure of failures) console.error(`Blocking audit finding: ${failure}`)

if (failures.size > 0) process.exit(1)
console.log('No unallowed high or critical npm advisories')
