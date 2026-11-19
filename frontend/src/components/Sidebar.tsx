import { useState } from 'react'

interface NavItem {
  label: string
  active?: boolean
  soon?: boolean
}

const navItems: NavItem[] = [
  { label: 'ANALYTICS', active: true },
  { label: 'TELEMETRY' },
]

/** Fixed desktop sidebar; collapses behind a button on small screens. */
export default function Sidebar() {
  // `open` remembers whether the mobile menu is showing. This is our first
  // piece of React state: when it changes, React redraws the component.
  const [open, setOpen] = useState(false)

  return (
    <>
      <button
        type="button"
        className={`sidebar__toggle ${open ? 'sidebar__toggle--open' : ''}`}
        onClick={() => setOpen(!open)}
        aria-label={open ? 'Close navigation' : 'Open navigation'}
        aria-expanded={open}
      >
        {open ? '✕' : '☰'}
      </button>

      <aside className={`sidebar ${open ? 'sidebar--open' : ''}`}>
        <div className="brand">
          <span className="brand__name">LECLERC</span>
          <span className="brand__accent">LABS</span>
          <span className="brand__sub">RACE INTELLIGENCE</span>
        </div>

        <nav className="nav" aria-label="Main navigation">
          {navItems.map((item) => (
            <div
              key={item.label}
              className={[
                'nav__item',
                item.active ? 'nav__item--active' : '',
                item.soon ? 'nav__item--soon' : '',
              ]
                .filter(Boolean)
                .join(' ')}
            >
              <span>{item.label}</span>
              {item.soon && <span className="nav__soon-tag">SOON</span>}
            </div>
          ))}
        </nav>

        <div className="sidebar__footer">
          <p>DATA SOURCE</p>
          <p>OpenF1 · via FastAPI</p>
          <p className="sidebar__disclaimer">
            Independent personal project. Not affiliated with Formula 1 or any driver.
          </p>
        </div>
      </aside>
    </>
  )
}
