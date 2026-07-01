import { describe, it, expect, vi } from 'vitest'

const mountMock = vi.fn(() => 'mounted-app-instance')
vi.mock('svelte', () => ({ mount: mountMock }))

describe('main', () => {
  it('mounts App into the #app element', async () => {
    document.body.innerHTML = '<div id="app"></div>'
    const target = document.getElementById('app')
    const App = (await import('./App.svelte')).default

    const mod = await import('./main.js')

    expect(mountMock).toHaveBeenCalledTimes(1)
    expect(mountMock).toHaveBeenCalledWith(App, { target })
    expect(mod.default).toBe('mounted-app-instance')
  })
})
