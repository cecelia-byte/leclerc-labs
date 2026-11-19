/** Top bar: product identity and data-source transparency. */
export default function Header() {
  return (
    <header className="header">
      <div>
        <p className="eyebrow">RACE INTELLIGENCE</p>
        <h1 className="header__title">MOTORSPORT PERFORMANCE SYSTEM</h1>
      </div>

      <div className="header__actions">
        <span className="badge badge--source">REAL DATA · OPENF1</span>
        <span className="season-pill">v0.9</span>
      </div>
    </header>
  )
}
