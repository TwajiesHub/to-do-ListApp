export default function Header({ smartDates, onToggleSmartDates }) {
  return (
    <header className="header">
      <h1 className="header-title">Tick</h1>
      <div className="smart-toggle">
        <span id="smart-dates-label">Smart dates</span>
        <button
          type="button"
          role="switch"
          aria-checked={smartDates}
          aria-labelledby="smart-dates-label"
          className="switch"
          onClick={onToggleSmartDates}
        />
      </div>
    </header>
  )
}
