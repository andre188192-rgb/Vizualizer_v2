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

export default function MetricChart({ metrics }) {
  const labels = metrics.map((entry) => new Date(entry.timestamp).toLocaleTimeString('ru-RU'))

  const data = {
    labels,
    datasets: [
      {
        label: 'Температура шпинделя, °C',
        data: metrics.map((entry) => entry.spindle_temp),
        borderColor: '#2563eb',
        backgroundColor: 'rgba(37, 99, 235, 0.2)'
      },
      {
        label: 'Вибрация RMS, g',
        data: metrics.map((entry) => entry.vibration_rms),
        borderColor: '#f97316',
        backgroundColor: 'rgba(249, 115, 22, 0.2)'
      }
    ]
  }

  return <Line data={data} />
}
