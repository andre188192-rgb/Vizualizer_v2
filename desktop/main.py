import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyqtgraph as pg
from PyQt5 import QtWidgets


class CncPulseAnalyzer(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("CNC Pulse Monitor - Инженерный анализ")
        self.resize(1200, 800)

        self.data = pd.DataFrame()

        self.plot_widget = pg.PlotWidget(title="Временные графики")
        self.fft_widget = pg.PlotWidget(title="Спектр вибрации (FFT)")
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(0)
        self.table.setRowCount(0)

        open_button = QtWidgets.QPushButton("Открыть лог")
        open_button.clicked.connect(self.open_log)

        export_button = QtWidgets.QPushButton("Экспорт PDF отчета")
        export_button.clicked.connect(self.export_report)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(open_button)
        button_layout.addWidget(export_button)
        button_layout.addStretch()

        left_layout = QtWidgets.QVBoxLayout()
        left_layout.addLayout(button_layout)
        left_layout.addWidget(self.plot_widget, stretch=2)
        left_layout.addWidget(self.fft_widget, stretch=1)

        right_layout = QtWidgets.QVBoxLayout()
        right_layout.addWidget(QtWidgets.QLabel("Сырые данные"))
        right_layout.addWidget(self.table)

        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(left_layout, stretch=3)
        main_layout.addLayout(right_layout, stretch=2)

        container = QtWidgets.QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def open_log(self) -> None:
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Открыть лог", str(Path.cwd()), "Logs (*.csv *.json)"
        )
        if not path:
            return
        if path.endswith(".csv"):
            self.data = pd.read_csv(path)
        else:
            with open(path, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
            self.data = pd.DataFrame(payload)
        self.update_views()

    def update_views(self) -> None:
        self.plot_widget.clear()
        self.fft_widget.clear()
        if self.data.empty:
            return

        if "vibration_rms" in self.data.columns:
            vib = self.data["vibration_rms"].to_numpy()
            self.plot_widget.plot(vib, pen=pg.mkPen("#2563eb", width=2), name="RMS")
            fft = np.abs(np.fft.rfft(vib - np.mean(vib)))
            freqs = np.fft.rfftfreq(len(vib), d=0.001)
            self.fft_widget.plot(freqs, fft, pen=pg.mkPen("#f97316", width=2))

        self.table.setRowCount(min(len(self.data), 200))
        self.table.setColumnCount(len(self.data.columns))
        self.table.setHorizontalHeaderLabels(self.data.columns)
        for row in range(self.table.rowCount()):
            for col, name in enumerate(self.data.columns):
                value = str(self.data.iloc[row, col])
                self.table.setItem(row, col, QtWidgets.QTableWidgetItem(value))

    def export_report(self) -> None:
        if self.data.empty:
            QtWidgets.QMessageBox.information(self, "Отчет", "Сначала откройте лог")
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Сохранить отчет", "report.txt", "Text (*.txt)"
        )
        if not path:
            return
        summary = self.data.describe(include="all").to_string()
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("Отчет CNC Pulse Monitor\n")
            handle.write(summary)
        QtWidgets.QMessageBox.information(self, "Отчет", "Отчет сохранен")


def main() -> None:
    app = QtWidgets.QApplication(sys.argv)
    window = CncPulseAnalyzer()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
