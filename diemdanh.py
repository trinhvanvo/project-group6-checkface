from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6 import uic
import cv2
import face_recognition
import numpy as np
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QMessageBox
from datetime import datetime
import conndb
import os

class diemdanh(QtWidgets.QMainWindow):  # Đổi tên lớp và thừa kế đúng kiểu
    
    
    def __init__(self, parent=None):  # Thêm tham số parent
        super(diemdanh, self).__init__(parent)  # Gọi hàm khởi tạo của QWidget đúng cách
        uic.loadUi('diemdanh.ui', self)
        self.cap = None
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_frame)
        # Kết nối Camera
        self.btnMoCamera.clicked.connect(self.open_camera)
        self.btnDongCamera.clicked.connect(self.close_camera)
        self.btnDiemDanh.clicked.connect(self.diemDanh)
        self.btnThoat.clicked.connect(self.confirm_exit)
        
        # Khởi tạo hàm kết nối cơ sở dữ liệu
        self.conn=conndb.conndb()
        
        #Biến dừng camera
        self.cap=None
    
    def open_camera (self):
        self.cap = cv2.VideoCapture(0) #Mở camera
        if not self.cap.isOpened():
            print ("Không thể mở camera")
            return
        self.timer.start(80) #Cập nhật khung mình mỗi 1ms
        self.btnMoCamera.setEnabled(False)
        self.btnDongCamera.setEnabled(True)
                                      
    def close_camera(self):       
        if self.cap is not None:  # Kiểm tra xem camera đã được mở hay chưa
            self.timer.stop()  # Dừng timer trước
            self.cap.release()  # Giải phóng camera
            self.cap = None  # Đặt cap về None sau khi giải phóng
            self.image_label.clear()  # Xóa nội dung label để tránh hiển thị khung hình cũ
            self.btnMoCamera.setEnabled(True)  # Bật lại nút "Mở Camera"
            self.btnDongCamera.setEnabled(False)  # Vô hiệu hóa nút "Đóng Camera"
           
    def recognizeFace(self, frame):
        #chuyển ảnh từ camera sang RGB
        rgb_frame =cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Nhận diện khuôn mặt
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        #Truy xuất tất cả ảnh trong cơ sở dữ liệu
        strsql = "SELECT MaSinhVien, Avatar FROM sinh_vien"
        students = self.conn.queryResult(strsql)
        
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            for student in students:
                # So sánh khuôn mặt
                avatar_path = f"./img/avatar/{student[1]}"
                known_image = face_recognition.load_image_file(avatar_path)
                known_encoding = face_recognition.face_encodings(known_image)[0]

                # So sánh khuôn mặt từ camera với ảnh từ database
                matches = face_recognition.compare_faces([known_encoding], face_encoding)
                if True in matches:
                    # Nếu trùng khớp, hiển thị thông tin sinh viên
                    self.displayStudentInfo(student[0])
                    return  
                    
    def displayStudentInfo(self, MaSinhVien):
        strsql = f"SELECT * FROM sinh_vien WHERE MaSinhVien = '{MaSinhVien}'"
        student = self.conn.queryResult(strsql)[0]

        self.lblMaSinhVien.setText(student[0])
        self.lblTenSinhVien.setText(student[1])
        self.lblLop.setText(student[2])
        self.lblGioiTinh.setText(student[3])
        avatar_path = f"./img/avatar/{student[4]}"
        pixmap = QPixmap(avatar_path)
        self.lblAvatar.setPixmap(pixmap) 
    
    def diemDanh(self):
        # Ghi lại thời gian điểm danh
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M:%S")
        self.txtNgayHienTai.setText(current_date)
        self.txtThoiGianHienTai.setText(current_time)

        QMessageBox.information(self, "Thông báo", "Đã điểm danh thành công!")             

    def closeCamera(self):
        if self.cap:
            self.cap.release()
            cv2.destroyAllWindows()
               
    def update_frame(self):
        if self.cap is not None and self.cap.isOpened():
            ret, frame = self.cap.read()  # Đọc khung hình từ camera
            if ret:
                
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

                # Vẽ hình chữ nhật quanh khuôn mặt
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

                # Chuyển đổi khung hình từ BGR sang RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                self.image_label.setPixmap(QPixmap.fromImage(q_img))  # Hiển thị trên image_label
        else:
            self.timer.stop()
        
    def confirm_exit(self):
        reply = QMessageBox.question(self, 'xác nhận',"Bạn có chắc chắn muốn thoát ?",QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            QtWidgets.QApplication.quit()
        else:
            pass
        
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main_window = diemdanh()  # Tạo một đối tượng của lớp diemdanh
    main_window.show()  # Hiển thị cửa sổ chính
    sys.exit(app.exec())
