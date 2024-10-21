from PyQt6 import QtCore
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import sys
import os
import conndb
from PyQt6.QtWidgets import QFileDialog
import shutil 

class sinhvien(QMainWindow):
    def __init__(self, parent=None):
        super(sinhvien, self).__init__(parent)
        uic.loadUi("sinhvien.ui", self)
        self.setWindowTitle("Thông tin sinh viên")
        self.image = ""
        self.pixmap = QPixmap("./img/avatar/user.png")

        # Khởi tạo các nút và kết nối tín hiệu
        self.btnTimKiem = self.findChild(QtWidgets.QPushButton, 'btnTimKiem')
        self.btnChonAnh = self.findChild(QtWidgets.QPushButton, 'btnChonAnh')
        self.btnThem = self.findChild(QtWidgets.QPushButton, 'btnThem')
        self.btnLamMoi = self.findChild(QtWidgets.QPushButton, 'btnLamMoi')
        self.btnSua = self.findChild(QtWidgets.QPushButton, 'btnSua')
        self.btnXoa = self.findChild(QtWidgets.QPushButton, 'btnXoa')
        self.btnThoat = self.findChild(QtWidgets.QPushButton, 'btnThoat')  # Tìm nút THOÁT

        # Tìm QLabel để hiển thị hình ảnh
        self.lblAvatar = self.findChild(QtWidgets.QLabel, 'lblAvatar')  # Đảm bảo tên đúng
        self.lblAvatar.setPixmap(self.pixmap)
        self.lblAvatar.setScaledContents(True)  # Tùy chọn: Để hình ảnh được thu nhỏ hoặc phóng to vừa với QLabel
        
        # Kết nối các nút với các hàm xử lý
        self.btnTimKiem.clicked.connect(self.searchItem)
        self.lblAvatar.setPixmap(self.pixmap)
        self.btnChonAnh.clicked.connect(self.chooseImage)
        self.tblSinhVien.clicked.connect(self.getItem)
        self.btnThem.clicked.connect(self.addItem)
        self.btnLamMoi.clicked.connect(self.resetTextBox)
        self.btnSua.clicked.connect(self.updateItem)
        self.btnXoa.clicked.connect(self.deleteItem)
        self.btnThoat.clicked.connect(self.confirmExit)  # Kết nối nút THOÁT
        self.conn = conndb.conndb()
        self.loadData()
        self.image_path = None  # Biến lưu đường dẫn ảnh

    def chooseImage(self):
        imgLink = QFileDialog.getOpenFileName(filter='*.jpg *.png')
        if imgLink[0]:
            self.image_path = imgLink[0]
            self.pixmap = QPixmap(imgLink[0])

        # Kiểm tra kích thước ảnh
        if self.pixmap.width() > 1024 or self.pixmap.height() > 1024:
            self.messageBoxInfo("Thông báo", "Ảnh quá lớn, vui lòng chọn ảnh có kích thước nhỏ hơn!")
            return

        # Giảm kích thước nếu cần
        self.pixmap = self.pixmap.scaled(128, 128, Qt.AspectRatioMode.KeepAspectRatio)
        self.lblAvatar.setPixmap(self.pixmap)

    def addItem(self):
        if self.txtMaSinhVien.text() == "" or self.txtTenSinhVien.text() == "":
            self.messageBoxInfo("Thông Báo", "Vui lòng nhập đầy đủ thông tin!")
            return
        
        MaSinhVien = self.txtMaSinhVien.text()
        TenSinhVien = self.txtTenSinhVien.text()
        Lop = self.txtLop.text()
        GioiTinh = self.cbGioiTinh.currentText()
        
        if self.image_path:
            with open(self.image_path, 'rb') as file:
                avatar_data = file.read()
        else:
            avatar_data = None
        
        Avatar = os.path.basename(self.image_path) if self.image_path else "user.png"

        # Thêm thông tin sinh viên vào CSDL MySQL
        strsql = f"INSERT INTO sinh_vien (MaSinhVien, TenSinhVien, Lop, GioiTinh, Avatar) VALUES ('{MaSinhVien}', '{TenSinhVien}', '{Lop}', '{GioiTinh}', '{Avatar}')"
        self.conn.queryExecute(strsql)
        
        self.messageBoxInfo("Thông báo", "Thêm sinh viên thành công!")
        self.resetTextBox()
        self.loadData()

    def getItem(self):
        row = self.tblSinhVien.currentRow()
        if row < 0:  # Kiểm tra xem có dòng nào được chọn không
            return

        try:
            MaSinhVien = self.tblSinhVien.item(row, 0).text()
            # Lấy thông tin sinh viên từ cơ sở dữ liệu theo Mã Sinh Viên
            strsql = f"SELECT MaSinhVien, TenSinhVien, Lop, GioiTinh, Avatar FROM sinh_vien WHERE MaSinhVien = '{MaSinhVien}'"
            result = self.conn.queryResult(strsql)

            if result:  # Kiểm tra nếu có kết quả
                # Điền thông tin sinh viên vào các ô nhập liệu
                self.txtMaSinhVien.setText(result[0][0])  # Mã sinh viên
                self.txtTenSinhVien.setText(result[0][1])  # Tên sinh viên
                self.txtLop.setText(result[0][2])  # Lớp học
                self.cbGioiTinh.setCurrentText(result[0][3])  # Giới tính

                # Kiểm tra xem ảnh đại diện là đường dẫn hay dữ liệu nhị phân (BLOB)
                avatar_data = result[0][4]  # Dữ liệu ảnh lưu trong cột Avatar

                if avatar_data:  # Nếu ảnh đại diện có dữ liệu
                    # Nếu bạn lưu ảnh dưới dạng đường dẫn tệp
                    if isinstance(avatar_data, str):
                        pixmap = QPixmap(avatar_data)  # Sử dụng đường dẫn ảnh để load
                    else:
                        # Nếu ảnh được lưu dưới dạng BLOB (nhị phân)
                        pixmap = QPixmap()
                        pixmap.loadFromData(avatar_data)

                    # Hiển thị ảnh trong QLabel
                    self.lblAvatar.setPixmap(pixmap.scaled(128, 128, Qt.AspectRatioMode.KeepAspectRatio))
                else:
                    # Nếu không có ảnh thì sử dụng ảnh mặc định
                    self.lblAvatar.setPixmap(QPixmap("./img/avatar/user.png"))
            else:
                self.messageBoxInfo("Thông báo", "Không tìm thấy sinh viên.")
        except Exception as e:
            print(f"Lỗi: {e}")



    def searchItem(self):
        if self.txtTimKiem.text() == "":
            self.messageBoxInfo("Thông Báo", "Vui lòng nhập tên sinh viên cần tìm!")
            return
        
        TenSinhVien = self.txtTimKiem.text()
        strsql = f"SELECT * FROM sinh_vien WHERE TenSinhVien LIKE '%{TenSinhVien}%'"
        result = self.conn.queryResult(strsql)
        
        row = 0
        self.tblSinhVien.setRowCount(len(result))
        for user in result:
            self.tblSinhVien.setItem(row, 0, QtWidgets.QTableWidgetItem(str(user[0])))
            self.tblSinhVien.setItem(row, 1, QtWidgets.QTableWidgetItem(str(user[1])))
            self.tblSinhVien.setItem(row, 2, QtWidgets.QTableWidgetItem(str(user[2])))
            self.tblSinhVien.setItem(row, 3, QtWidgets.QTableWidgetItem(str(user[3])))
            row += 1
        
        self.pixmap = QPixmap("./img/avatar/user.png")
        self.lblAvatar.setPixmap(self.pixmap)
        self.txtMaSinhVien.setEnabled(True)

    def updateItem(self):
        if self.txtMaSinhVien.text() == "" or self.txtTenSinhVien.text() == "":
            self.messageBoxInfo("Thông Báo", "Vui lòng nhập đầy đủ thông tin!")
            return

        MaSinhVien = self.txtMaSinhVien.text()
        HoTen = self.txtTenSinhVien.text()
        GioiTinh = self.cbGioiTinh.currentText()
        Lop = self.txtLop.text()

        strsql = f"SELECT * FROM sinh_vien WHERE MaSinhVien = '{MaSinhVien}'"
        result = self.conn.queryResult(strsql)

        if not result:
            self.messageBoxInfo("Thông Báo", "Mã sinh viên không tồn tại!")
            return

        strsql_update = f"UPDATE sinh_vien SET TenSinhVien='{HoTen}', GioiTinh='{GioiTinh}', Lop='{Lop}' WHERE MaSinhVien='{MaSinhVien}'"
        self.conn.queryExecute(strsql_update)

        if self.image_path:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            avatar_dir = os.path.join(dir_path, 'img', 'avatar')

            old_avatar_path = os.path.join(avatar_dir, result[0][4])
            if os.path.exists(old_avatar_path) and result[0][4] != "user.png":
                print(f"Removing old avatar: {old_avatar_path}")  # Debugging
                os.remove(old_avatar_path)

            new_avatar = os.path.join(avatar_dir, os.path.basename(self.image_path))
            print(f"Copying new avatar to: {new_avatar}")  # Debugging
            shutil.copy2(self.image_path, new_avatar)

            strsql_update_avatar = f"UPDATE sinh_vien SET Avatar='{os.path.basename(self.image_path)}' WHERE MaSinhVien='{MaSinhVien}'"
            self.conn.queryExecute(strsql_update_avatar)

        self.messageBoxInfo("Thông Báo", "Cập nhật thông tin sinh viên thành công!")
        self.resetTextBox()
        self.loadData()

    def deleteItem(self):
        MaSinhVien = self.txtMaSinhVien.text()
        if not MaSinhVien:
            self.messageBoxInfo("Thông Báo", "Vui lòng nhập Mã sinh viên để xóa!")
            return

        # Kiểm tra xem mã sinh viên có tồn tại không
        strsql = f"SELECT * FROM sinh_vien WHERE MaSinhVien='{MaSinhVien}'"
        result = self.conn.queryResult(strsql)
        if not result:
            self.messageBoxInfo("Thông Báo", "Mã sinh viên không tồn tại!")
            return

        # Xóa sinh viên
        strsql_delete = f"DELETE FROM sinh_vien WHERE MaSinhVien='{MaSinhVien}'"
        self.conn.queryExecute(strsql_delete)
        self.messageBoxInfo("Thông Báo", "Xóa sinh viên thành công!")
        self.resetTextBox()
        self.loadData()

    def resetTextBox(self):
        self.txtMaSinhVien.setText("")
        self.txtTenSinhVien.setText("")
        self.txtLop.setText("")
        self.cbGioiTinh.setCurrentIndex(0)
        self.lblAvatar.setPixmap(QPixmap("./img/avatar/user.png"))
        self.image_path = None  # Đặt lại đường dẫn ảnh

    def loadData(self):
        strsql = "SELECT * FROM sinh_vien"
        result = self.conn.queryResult(strsql)

        row = 0
        self.tblSinhVien.setRowCount(len(result))
        for user in result:
            self.tblSinhVien.setItem(row, 0, QtWidgets.QTableWidgetItem(str(user[0])))
            self.tblSinhVien.setItem(row, 1, QtWidgets.QTableWidgetItem(str(user[1])))
            self.tblSinhVien.setItem(row, 2, QtWidgets.QTableWidgetItem(str(user[2])))
            self.tblSinhVien.setItem(row, 3, QtWidgets.QTableWidgetItem(str(user[3])))
            row += 1

   

    def messageBoxInfo(self, title, message):
        QMessageBox.information(self, title, message)
        
    def confirmExit(self):
        reply = QMessageBox.question(self, 'xác nhận',"Bạn có chắc chắn muốn thoát ?",QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            QtWidgets.QApplication.quit()
        else:
            pass

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = sinhvien()
    window.show()
    sys.exit(app.exec())
