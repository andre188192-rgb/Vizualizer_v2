import { useEffect, useState } from 'react'
import StatusCard from '../components/StatusCard.jsx'
import EventTable from '../components/EventTable.jsx'
import MaintenanceForm from '../components/MaintenanceForm.jsx'
import MetricChart from '../components/MetricChart.jsx'
import ThresholdForm from '../components/ThresholdForm.jsx'

const API_BASE = 'http://localhost:8000'
const API_KEY = 'changeme'

export default function App() {
  const [latest, setLatest] = useState(null)
  const [events, setEvents] = useState([])
  const [maintenance, setMaintenance] = useState([])
  const [metrics, setMetrics] = useState([])

  const loadEvents = async () => {
    const response = await fetch(`${API_BASE}/events`)
    const data = await response.json()
    setEvents(data.events ?? [])
  }

  const loadMaintenance = async () => {
    const response = await fetch(`${API_BASE}/maintenance`)
    const data = await response.json()
    setMaintenance(data.maintenance ?? [])
  }

  const loadMetrics = async () => {
    const response = await fetch(`${API_BASE}/metrics`)
    const data = await response.json()
    setMetrics(data.metrics ?? [])
    setLatest(data.metrics?.[data.metrics.length - 1] ?? null)
  }

  useEffect(() => {
    loadEvents()
    loadMaintenance()
    loadMetrics()
    const interval = setInterval(() => {
      loadMetrics()
    }, 2000)
    return () => clearInterval(interval)
  }, [])

  const requestSnapshot = async () => {
    await fetch(`${API_BASE}/snapshot`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-API-Key': API_KEY },
      body: JSON.stringify({ minutes: 5 })
    })
    loadEvents()
  }

  const resetAlarm = async () => {
    await fetch(`${API_BASE}/alarm/reset`, { method: 'POST', headers: { 'X-API-Key': API_KEY } })
    loadEvents()
  }

  return (
    <div>
      <header>
        <h1>CNC Pulse Monitor</h1>
        <p>Удаленный мониторинг состояния фрезерного станка</p>
      </header>
      <main>
        <section className="grid">
          <StatusCard title="Сеть" value={`${latest?.voltage?.toFixed?.(1) ?? '--'} V`} />
          <StatusCard title="Ток" value={`${latest?.current?.toFixed?.(2) ?? '--'} A`} />
          <StatusCard title="Температура шпинделя" value={`${latest?.spindle_temp?.toFixed?.(1) ?? '--'} °C`} />
          <StatusCard title="Вибрация (RMS)" value={`${latest?.vibration_rms?.toFixed?.(2) ?? '--'} g`} />
        </section>

        <section className="card">
          <h3>Графики в реальном времени</h3>
          {metrics.length ? <MetricChart metrics={metrics} /> : <p>Данные еще не поступили.</p>}
        </section>

        <section className="card">
          <h3>Состояние станка</h3>
          <span
            className={`badge ${
              latest?.state === 'ALARM' ? 'alarm' : latest?.state === 'WARN' ? 'warn' : 'normal'
            }`}
          >
            {latest?.state ?? 'NO DATA'}
          </span>
          <div className="form-row" style={{ marginTop: 16 }}>
            <button onClick={requestSnapshot}>Сформировать диагностический снимок</button>
            <button className="secondary" onClick={resetAlarm}>
              Сбросить аварию
            </button>
          </div>
        </section>

        <section className="card">
          <h3>Настройки порогов</h3>
          <ThresholdForm apiKey={API_KEY} />
        </section>

        <section className="card">
          <h3>Журнал событий</h3>
          <EventTable events={events} />
        </section>

        <section className="card">
          <h3>Журнал обслуживания</h3>
          <MaintenanceForm apiKey={API_KEY} onSaved={loadMaintenance} />
          <EventTable
            events={maintenance.map((entry) => ({
              id: entry.id,
              timestamp: entry.timestamp,
              category: entry.maintenance_type,
              message: entry.comment ?? '-',
              severity: entry.performed_by
            }))}
          />
        </section>
      </main>
    </div>
  )
}
