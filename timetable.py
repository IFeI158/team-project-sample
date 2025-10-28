import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QSpinBox, QLabel

class SpinBoxExample(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QSpinBox 예제")

        layout = QVBoxLayout()

        # 라벨
        self.label = QLabel("값: 0")
        layout.addWidget(self.label)

        # 스핀박스
        self.spin = QSpinBox()
        self.spin.setRange(0, 100)       # 최소/최대값 설정
        self.spin.setSingleStep(1)       # 증가 단위
        self.spin.setValue(0)            # 초기값
        self.spin.valueChanged.connect(self.update_label)
        layout.addWidget(self.spin)

        self.setLayout(layout)
        self.resize(200, 100)

    def update_label(self, value):
        self.label.setText(f"값: {value}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SpinBoxExample()
    win.show()
    sys.exit(app.exec_())
