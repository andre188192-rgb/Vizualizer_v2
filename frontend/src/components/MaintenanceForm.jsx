import { useState } from 'react'

const API_BASE = 'http://localhost:8000'

export default function MaintenanceForm({ onSaved }) {
  const [maintenanceType, setMaintenanceType] = useState('Замена охлаждающей жидкости')
  const [performedBy, setPerformedBy] = useState('')
  const [comment, setComment] = useState('')

  const submit = async (event) => {
    event.preventDefault()
    await fetch(`${API_BASE}/maintenance`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        maintenance_type: maintenanceType,
        performed_by: performedBy,
        comment
      })
    })
    setPerformedBy('')
    setComment('')
    onSaved?.()
  }

  return (
    <form onSubmit={submit} className="form-row" style={{ marginBottom: 16 }}>
      <div style={{ flex: 1 }}>
        <label>Тип обслуживания</label>
        <select value={maintenanceType} onChange={(e) => setMaintenanceType(e.target.value)}>
          <option>Замена охлаждающей жидкости</option>
          <option>Проверка шпинделя</option>
          <option>Контроль вибрации</option>
          <option>Плановое ТО</option>
        </select>
      </div>
      <div style={{ flex: 1 }}>
        <label>Исполнитель</label>
        <input value={performedBy} onChange={(e) => setPerformedBy(e.target.value)} required />
      </div>
      <div style={{ flex: 2 }}>
        <label>Комментарий</label>
        <textarea value={comment} onChange={(e) => setComment(e.target.value)} />
      </div>
      <div style={{ alignSelf: 'end' }}>
        <button type="submit">Добавить</button>
      </div>
    </form>
  )
}
