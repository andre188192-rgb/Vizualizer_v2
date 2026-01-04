export default function StatusCard({ title, value }) {
  return (
    <div className="card">
      <h3>{title}</h3>
      <p style={{ fontSize: 24, margin: 0 }}>{value}</p>
    </div>
  )
}
