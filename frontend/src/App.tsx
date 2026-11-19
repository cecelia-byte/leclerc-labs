import Sidebar from './components/Sidebar'
import Header from './components/Header'
import DashboardPage from './components/DashboardPage'

/**
 * App is only a layout container in Stage 1.
 * Later stages will add routing here (e.g. /drivers/:id and /compare).
 */
export default function App() {
  return (
    <div className="app-shell">
      <Sidebar />
      <div className="app-main">
        <Header />
        <DashboardPage />
      </div>
    </div>
  )
}
