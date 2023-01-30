from hashlib import md5
from PyQt5 import uic, QtWidgets
import sys
import sqlite3 as db

# ==================== Database Connection and table creation if no exist =======================
database = db.connect("kavyant.db")
cusror = database.cursor()
cusror.execute("CREATE TABLE IF NOT EXISTS auth_user(ID INTEGER PRIMARY KEY AUTOINCREMENT, USERNAME VARCHAR(256) UNIQUE, PASSWORD VARCHAR(256) , USERGROUP VARCHAR(50), ACTIVATED BOOL, CREATED_AT DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP)")
cusror.execute("CREATE TABLE IF NOT EXISTS requests( ID INTEGER PRIMARY KEY AUTOINCREMENT , USERNAME VARCHAR(256) , REQUESTTYPE VARCHAR(256) )")
# ==================== Database Connection and table creation if no exist =======================

class AdminPanel(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.admin_panel = uic.loadUi('admin_panel.ui', self)


class ForgetPassword(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.forgot_password = uic.loadUi('forgot_password.ui', self)
        self.login_id = self.findChild(QtWidgets.QLineEdit,"linePasswordReset_LoginID")
        self.password = self.findChild(QtWidgets.QLineEdit,"linePasswordReset_OldPassword")
        self.new_password = self.findChild(QtWidgets.QLineEdit,"linePasswordReset_NewPassword")
        self.re_new_password = self.findChild(QtWidgets.QLineEdit,"linePasswordReset_NewPasswordConfirm")
        self.messege = self.findChild(QtWidgets.QLabel,"messege")
        self.messege.setStyleSheet("color: rgb(200, 50, 50);font: bold;")

        self.forgot_password.buttonPasswordReset_ChangePassword.clicked.connect(self.changePassword)
        self.forgot_password.buttonPasswordReset_AskAdmin.clicked.connect(self.password_messege)
        self.forgot_password.buttonPasswordReset_Cancel.clicked.connect(self.login)

    def changePassword(self):
        if self.login_id.text() == "" or self.password.text() == "" or self.new_password.text() == "" or self.re_new_password.text() == "":
            self.messege.setText("Please fill all the fields!")
        else :
            cusror.execute(f"SELECT * FROM auth_user WHERE USERNAME = '{self.login_id.text()}' AND PASSWORD = '{md5(bytes(self.password.text(),'utf-8')).hexdigest()}'")     
            user = cusror.fetchall()
            if user:
                if len(self.new_password.text()) >= 7:
                    if self.new_password.text() == self.re_new_password.text():
                        cusror.execute(f"UPDATE auth_user SET PASSWORD = '{md5(bytes(self.re_new_password.text(),'utf-8')).hexdigest()}' WHERE USERNAME = '{self.login_id.text()}' AND PASSWORD = '{md5(bytes(self.password.text(),'utf-8')).hexdigest()}'")
                        database.commit()
                        self.messege.setText("Password has been changed!")  
                    else:
                        self.messege.setText("Confirm password is not matched!")  
                else :
                    self.messege.setText("Password should have minimum 7 characters!")
            else :
                self.messege.setText("User not found!")
                

    def password_messege(self):
        if self.login_id.text() == "":
            self.messege.setText("Please enter your login ID")
        else :
            cusror.execute(f"INSERT INTO requests (USERNAME, REQUESTTYPE) VALUES ('{self.login_id.text()}', 'RESET PASSWORD')")     
            database.commit()
            self.close()
            self.w = PasswordMessege()
            self.w.show()

    def login(self):
        self.close()
        self.w = Login()
        self.w.show()

class PasswordMessege(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.password_messege = uic.loadUi('password_messege.ui', self)
        self.password_messege.buttonLoginPanelMessage_Exit.clicked.connect(self.close)

class Login(QtWidgets.QDialog):
    
    def __init__(self):
        super(Login, self).__init__()
        self.log = uic.loadUi('login.ui', self)
        self.username = self.findChild(QtWidgets.QLineEdit,"lineLoginPanel_LoginID")
        self.password = self.findChild(QtWidgets.QLineEdit,"lineLoginPanel_Password")
        self.fail = self.findChild(QtWidgets.QLabel, "wrong_password")
        self.fail.setStyleSheet("color: rgb(200, 50, 50);font: bold;")
        self.log.buttonLoginPanel_OK.clicked.connect(self.login)
        self.log.buttonLoginPanel_ForgotPassword.clicked.connect(self.changePassword)
        self.log.buttonLoginPanel_Cancel.clicked.connect(self.close)

        self.show()

    def login(self):
        if self.username.text() == "" or self.password.text() == "":
            self.fail.setText("Enter Login Id and Password!")
        else:
            password = md5(bytes(self.password.text(),"utf-8")).hexdigest()
            cusror.execute(f"SELECT * FROM auth_user WHERE USERNAME = '{self.username.text()}' AND PASSWORD = '{password}'")     
            user = cusror.fetchall()
            if user:
                if user[0][3] == 'admin':
                    self.adminPanel()
                else :
                    print("Welcome to main app!")
            else :
                self.fail.setText("Incorrect Credential!")    

    def adminPanel(self):
        self.close()
        self.w = AdminPanel()
        self.w.showMaximized()
        self.w.show()

    def changePassword(self):
        self.close()
        self.w = ForgetPassword()
        self.w.show()
            
  
    
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Login()
    app.exec_()