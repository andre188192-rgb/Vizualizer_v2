import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  LineElement,
  PointElement,
  Tooltip,
  Legend
} from 'chart.js'
import { Line } from 'react-chartjs-2'

ChartJS.register(CategoryScale, LinearScale, LineElement, PointElement, Tooltip, Legend)

const SENSOR_ERROR = -999

export default function MetricChart({ metrics }) {
  const labels = metrics.map((entry) => new Date(entry.timestamp).toLocaleTimeString('ru-RU'))

  const temperatureData = metrics.map((entry) =>
    entry.spindle_temp === SENSOR_ERROR ? null : entry.spindle_temp
  )
  const vibrationData = metrics.map((entry) =>
    entry.vibration_rms === SENSOR_ERROR ? null : entry.vibration_rms
  )

  const data = {
    labels,
    datasets: [
      {
        label: 'Температура шпинделя, °C',
        data: temperatureData,
        borderColor: '#2563eb',
        backgroundColor: 'rgba(37, 99, 235, 0.2)',
        spanGaps: true
      },
      {
        label: 'Вибрация RMS, g',
        data: vibrationData,
        borderColor: '#f97316',
        backgroundColor: 'rgba(249, 115, 22, 0.2)',
        spanGaps: true
      }
    ]
  }

  const hasErrors = metrics.some(
    (entry) => entry.spindle_temp === SENSOR_ERROR || entry.vibration_rms === SENSOR_ERROR
  )

  return (
    <div>
      {hasErrors && <p>Некоторые датчики не отвечают — точки скрыты на графике.</p>}
      <Line data={data} />
    </div>
  )
}
