import { useEffect, useState } from 'react'

const API_BASE = 'http://localhost:8000'

export default function ThresholdForm({ apiKey }) {
  const [values, setValues] = useState({
    vibration_warn: 0,
    vibration_alarm: 0,
    spindle_temp_warn: 0,
    spindle_temp_alarm: 0
  })

  const load = async () => {
    const response = await fetch(`${API_BASE}/thresholds`)
    const data = await response.json()
    if (data.thresholds) {
      setValues(data.thresholds)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const updateField = (field) => (event) => {
    setValues((prev) => ({ ...prev, [field]: Number(event.target.value) }))
  }

  const save = async (event) => {
    event.preventDefault()
    await fetch(`${API_BASE}/thresholds`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', 'X-API-Key': apiKey },
      body: JSON.stringify(values)
    })
    await load()
  }

  return (
    <form onSubmit={save} className="form-row">
      <div>
        <label>Вибрация WARN</label>
        <input type="number" step="0.01" value={values.vibration_warn} onChange={updateField('vibration_warn')} />
      </div>
      <div>
        <label>Вибрация ALARM</label>
        <input type="number" step="0.01" value={values.vibration_alarm} onChange={updateField('vibration_alarm')} />
      </div>
      <div>
        <label>Температура WARN</label>
        <input type="number" step="0.1" value={values.spindle_temp_warn} onChange={updateField('spindle_temp_warn')} />
      </div>
      <div>
        <label>Температура ALARM</label>
        <input type="number" step="0.1" value={values.spindle_temp_alarm} onChange={updateField('spindle_temp_alarm')} />
      </div>
      <div style={{ alignSelf: 'end' }}>
        <button type="submit">Сохранить пороги</button>
      </div>
    </form>
  )
}
