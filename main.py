from PyQt6 import QtCore
from PyQt6 import QtWidgets
import sys
from sinhvien import sinhvien

def main():
    app = QtWidgets.QApplication(sys.argv)
    widget = QtWidgets.QStackedWidget()

    # Tạo một thể hiện của lớp sinhvien
    sinhvien_instance = sinhvien(widget)

    widget.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
    widget.addWidget(sinhvien_instance)  # Thêm thể hiện vào QStackedWidget

    widget.setCurrentIndex(0)
    widget.setFixedWidth(930)
    widget.setFixedHeight(661)
    widget.show()

    sys.exit(app.exec())  # Đảm bảo thoát chương trình đúng cách

if __name__ == "__main__":
    main()
