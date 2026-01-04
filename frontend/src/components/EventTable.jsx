export default function EventTable({ events }) {
  if (!events.length) {
    return <p>Нет данных.</p>
  }
  return (
    <table className="table">
      <thead>
        <tr>
          <th>Время</th>
          <th>Категория</th>
          <th>Сообщение</th>
          <th>Статус</th>
        </tr>
      </thead>
      <tbody>
        {events.map((event) => (
          <tr key={event.id}>
            <td>{new Date(event.timestamp).toLocaleString('ru-RU')}</td>
            <td>{event.category}</td>
            <td>{event.message}</td>
            <td>{event.severity}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
