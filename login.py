from hashlib import md5
from PyQt5 import uic, QtWidgets
import sys
import sqlite3 as db

# ==================== Database Connection and table creation if no exist =======================
database = db.connect("kavyant.db")
cusror = database.cursor()
cusror.execute("CREATE TABLE IF NOT EXISTS auth_user(ID INTEGER PRIMARY KEY AUTOINCREMENT, USERNAME VARCHAR(256) , PASSWORD VARCHAR(256) , USERGROUP VARCHAR(50), ACTIVATED BOOL )")
# ==================== Database Connection and table creation if no exist =======================

class ForgetPassword(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.forgot_password = uic.loadUi('forgot_password.ui', self)
        self.login_id = self.findChild(QtWidgets.QLineEdit,"linePasswordReset_LoginID")
        self.password = self.findChild(QtWidgets.QLineEdit,"linePasswordReset_OldPassword")
        self.new_password = self.findChild(QtWidgets.QLineEdit,"linePasswordReset_NewPassword")
        self.re_new_password = self.findChild(QtWidgets.QLineEdit,"linePasswordReset_NewPasswordConfirm")
        self.messege = self.findChild(QtWidgets.QLabel,"messege")

        self.forgot_password.buttonPasswordReset_ChangePassword.clicked.connect(self.changePassword)
        self.forgot_password.buttonPasswordReset_AskAdmin.clicked.connect(self.password_messege)
        self.forgot_password.buttonPasswordReset_Cancel.clicked.connect(self.close)

    def changePassword(self):
        if self.login_id.text() == "" or self.password.text() == "" or self.new_password.text() == "" or self.re_new_password.text() == "":
            self.messege.setText("Please fill all the fields!")
        else :
            pass
            cusror.execute(f"SELECT * FROM auth_user WHERE USERNAME = '{self.login_id.text()}' AND PASSWORD = '{md5(bytes(self.password.text(),'utf-8')).hexdigest()}'")     
            user = cusror.fetchall()
            if user:
                if self.new_password.text() == self.re_new_password.text():
                    cusror.execute(f"UPDATE auth_user SET PASSWORD = '{md5(bytes(self.re_new_password.text(),'utf-8')).hexdigest()}' WHERE USERNAME = '{self.login_id.text()}' AND PASSWORD = '{md5(bytes(self.password.text(),'utf-8')).hexdigest()}'")
                    database.commit()
                    self.messege.setText("Password has been changed!")  
                else:
                    self.messege.setText("Confirm password is not matched!")  
            else :
                self.messege.setText("User not found!")
                

    def password_messege(self):
        self.close()
        self.w = PasswordMessege()
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
                print("Success!")  
            else :
                self.fail.setText("Incorrect Credential!")    


    def changePassword(self):
        self.close()
        self.w = ForgetPassword()
        self.w.show()
            
  
    
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Login()
    app.exec_()