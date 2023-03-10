from hashlib import md5
from PyQt5 import uic, QtWidgets
import sys
import sqlite3 as db
import platform
import pandas as pd
from datetime import datetime
import os

# ==================== Database Connection and table creation if no exist =======================
database = db.connect("kavyant.db")
cusror = database.cursor()
cusror.execute("CREATE TABLE IF NOT EXISTS auth_user(ID INTEGER PRIMARY KEY AUTOINCREMENT, USERNAME VARCHAR(256) UNIQUE, PASSWORD VARCHAR(256) , USERGROUP VARCHAR(50), ACTIVATED BOOL, CREATED_AT DATETIME NOT NULL DEFAULT (datetime('now','localtime')))")
cusror.execute("CREATE TABLE IF NOT EXISTS requests( ID INTEGER PRIMARY KEY AUTOINCREMENT , USERNAME VARCHAR(256) , REQUESTTYPE VARCHAR(256) )")
cusror.execute("CREATE TABLE IF NOT EXISTS login_count(ID INTEGER PRIMARY KEY AUTOINCREMENT, HOST VARCHAR(256), COUNT INTEGER(5))")
cusror.execute("CREATE TABLE IF NOT EXISTS action_record (ID INTEGER PRIMARY KEY AUTOINCREMENT ,  USERNAME VARCHAR (256) , ACTIONTIME DATETIME NOT NULL DEFAULT (datetime('now','localtime')), TYPEOFACTION VARCHAR(256), NEW_VALUE VARCHAR(256) DEFAULT NULL ,DOCUMENT_NAME VARCHAR(256) DEFAULT NULL, COMPUTERNAME VARCHAR(256), EXTRA1 VARCHAR(256) DEFAULT NULL , EXTRA2 DEFAULT NULL ) ")
cusror.execute("CREATE TABLE IF NOT EXISTS login_record  (ID INTEGER PRIMARY KEY AUTOINCREMENT , USERNAME VARCHAR(256),STATUS VARCHAR(20), COMPUTERNAME VARCHAR(150) , EXTRA1 TEXT DEFAULT NULL, EXTRA2 TEXT DEFAULT NULL, ATTEMPTED_AT DATETIME NOT NULL DEFAULT (datetime('now','localtime')) )") 

# ==================== Database Connection and table creation if no exist =======================
def convertdate(date_string): 
    try:
        date_time = datetime.strptime(date_string, '%m/%d/%Y %I:%M %p')
    except:
        date_time = datetime.strptime(date_string, '%d-%m-%Y %I:%M %p')
    # Convert the datetime object to a string using the strftime method
    new_date_string = date_time.strftime('%Y-%m-%d %H:%M:%S')
    
    return new_date_string

class AdminPanel(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.admin_panel = uic.loadUi('admin_panel.ui', self)
        self.audit_trail_rows = cusror.execute("SELECT * from action_record")
        self.audit_trail_data = self.audit_trail_rows.fetchall()        
        self.password=self.findChild(QtWidgets.QLineEdit,"lineAdminPanel_OneTimePassword")
        self.username= self.findChild(QtWidgets.QLineEdit,"lineAdminPanel_NewUser")
        self.user_group =self.findChild(QtWidgets.QComboBox,"comboAdminPanel_UserGroup")
        self.users =self.findChild(QtWidgets.QComboBox,"userlist")
        self.admin_panel.buttonAdminPanel_AddUser.clicked.connect(self.insertuser)
        self.admin_panel.buttonAdminPanel_RemoveUser.clicked.connect(self.remove_user)
        self.admin_panel.buttonAdminPanel_ResetUserPassword.clicked.connect(self.changepassword)
        self.admin_panel.buttonAdminPanel_ExportLoginList.clicked.connect(self.export_login_record)
        self.admin_panel.buttonAdminPanel_ExportUserList.clicked.connect(self.export_user_record)
        self.admin_panel.buttonPasswordReset_Cancel.clicked.connect(self.close)
        self.admin_panel.buttonAdminPanel_ActivateUser.clicked.connect(self.active_or_deactivateuser)
        self.admin_panel.buttonAdminPanel_PrintUserList.clicked.connect(self.print_userrecord)
        self.admin_panel.buttonAdminPanel_PrintLoginList_3.clicked.connect(self.print_login_record)
        self.loginreport_start_date = self.findChild(QtWidgets.QDateTimeEdit,"dateTimeAdminPanel_LoginsFrom")
        self.login_report_end_date = self.findChild(QtWidgets.QDateTimeEdit,"dateTimeAdminPanel_LoginsTill")
        
        self.msg = self.findChild(QtWidgets.QLabel,"messege")
        self.msg.setStyleSheet("color: rgb(200, 50, 50);font: bold;font-size:15px;")

        self.showLoginRecords()
        self.showUsers()
        self.update_userlist()

    def update_userlist(self):
        cusror.execute("SELECT * FROM auth_user")
        users = cusror.fetchall()
        usernames = [i[1] for i  in users]
        self.users.clear()
        self.users.addItems(usernames)

    def showUsers(self):
        self.tableWidget = self.findChild(QtWidgets.QTableWidget,"tableAdminPanel_UserList")
        cusror.execute("SELECT * FROM auth_user")
        users = cusror.fetchall()
        self.tableWidget.setRowCount(len(users))
        self.tableWidget.setColumnCount(6)  

        for id, item in enumerate(users):
            self.tableWidget.setItem(id,0, QtWidgets.QTableWidgetItem(item[1]))
            self.tableWidget.setItem(id,1, QtWidgets.QTableWidgetItem(item[3]))
            self.tableWidget.setItem(id,2, QtWidgets.QTableWidgetItem(item[5][0:10]))
            self.tableWidget.setItem(id,3, QtWidgets.QTableWidgetItem("Yes" if item[4] == 1 else "No"))
            self.tableWidget.setItem(id,4, QtWidgets.QTableWidgetItem(""))
            self.tableWidget.setItem(id,5, QtWidgets.QTableWidgetItem(""))

    def showLoginRecords(self):
        self.tableWidget = self.findChild(QtWidgets.QTableWidget,"tableAdminPanel_LoginList")
        cusror.execute("SELECT * FROM login_record")
        login_records = cusror.fetchall()
        self.tableWidget.setRowCount(len(login_records))
        self.tableWidget.setColumnCount(7)  

        for id, item in enumerate(login_records):
            self.tableWidget.setItem(id,0, QtWidgets.QTableWidgetItem(item[1]))
            self.tableWidget.setItem(id,1, QtWidgets.QTableWidgetItem(item[6][11:19]))
            self.tableWidget.setItem(id,2, QtWidgets.QTableWidgetItem(item[6][0:10]))
            self.tableWidget.setItem(id,3, QtWidgets.QTableWidgetItem(item[2]))
            self.tableWidget.setItem(id,4, QtWidgets.QTableWidgetItem(item[3]))
            self.tableWidget.setItem(id,5, QtWidgets.QTableWidgetItem(""))
            self.tableWidget.setItem(id,6, QtWidgets.QTableWidgetItem(""))

    def export_login_record(self):      
        start_date =convertdate(self.loginreport_start_date.text())
        end_date  = convertdate(self.login_report_end_date.text())
        cusror.execute("SELECT * FROM login_record WHERE ATTEMPTED_AT BETWEEN ? AND ?", (start_date, end_date))
        login_records = cusror.fetchall()
        if len(login_records) >0:

            login_record_with_header = [("ID","USERNAME","STATUS","COMPUTERNAME", "EXTRA1","EXTRA2","ATTEMPT_AT")]+login_records
            data = pd.DataFrame(login_record_with_header)
            data.to_csv("login_record.csv")
            self.msg.setText("Login records successfully exported!")
        else:
            self.msg.setText("No data Found !")
    
    def print_login_record(self):
        start_date =convertdate(self.loginreport_start_date.text())
        end_date   = convertdate(self.login_report_end_date.text())
        cusror.execute("SELECT * FROM login_record WHERE ATTEMPTED_AT BETWEEN ? AND ?", (start_date, end_date))
        login_records = cusror.fetchall()
        if len(login_records) >0:
            login_record_with_header = [("ID","USERNAME","STATUS","COMPUTERNAME", "EXTRA1","EXTRA2","ATTEMPT_AT")]+login_records
            data = pd.DataFrame(login_record_with_header)
            data.to_csv("login_record.csv")
            os.startfile("login_record.csv","print")
        else:
            self.msg.setText("No data Found !")

    
    def print_userrecord(self):
        cusror.execute("SELECT * FROM auth_user")
        login_records = cusror.fetchall()
        login_record_with_header = [("ID","USERNAME","STATUS","COMPUTERNAME", "EXTRA1","EXTRA2","ATTEMPT_AT")]+login_records
        data = pd.DataFrame(login_record_with_header)
        data.to_csv("users_record.csv")
        os.startfile("users_record.csv","print")


    def export_user_record(self):
        cusror.execute("SELECT * FROM auth_user")
        user_record = cusror.fetchall()
        user_record_with_header = [("ID","USERNAME","PASSWORD","USERGROUP", "ACTIVATED","CREATED_AT")]+user_record
        data = pd.DataFrame(user_record_with_header)
        data.to_csv("users_record.csv")
        self.msg.setText("User records successfully exported!")


    def insertuser(self):
        password = self.password.text()
        username = self.username.text()
        usergroup = self.user_group.currentText().lower()
        print(password, usergroup, username)
        try:
            password = md5(bytes(password,"utf-8")).hexdigest()          
            cusror.execute("INSERT INTO auth_user(USERNAME, PASSWORD, USERGROUP, ACTIVATED)VALUES(?,?,?,?)",(username,password,usergroup,True))
            database.commit()
            self.msg.setText("New User Added!")
            self.update_userlist()
            self.showUsers()
            return "inserted"
        except:
            self.msg.setText("There is a problem. Try later.")
            return "error "
    
    def changepassword(self):
        username =username =self.users.currentText()
        password = "12345678"
        password = md5(bytes(password,"utf-8")).hexdigest()
        try:
            cusror.execute("UPDATE auth_user SET PASSWORD= ? WHERE USERNAME= ? ",(password, username))
            database.commit()
            self.msg.setText(f"Password has been reset for user : {username}")
        except Exception as e:
            print(e)
            
    def active_or_deactivateuser(self):
        username =self.users.currentText()
        row=cusror.execute("SELECT * FROM auth_user WHERE USERNAME= ? ",( username, ))
        data = row.fetchall()
        if data[0][4] ==1:
            try:
                cusror.execute("UPDATE auth_user SET ACTIVATED= 0 WHERE USERNAME= ? ",( username,))
                self.msg.setText(f"Deactivated user : {username}")
                self.showUsers()
            except:
                pass
        else:
            try:
                cusror.execute("UPDATE auth_user SET ACTIVATED= 1 WHERE USERNAME= ? ",( username,))
                self.msg.setText(f"Activated user : {username}")
                self.showUsers()
            except:
                pass

        database.commit()
    
    def remove_user(self):
        username =self.users.currentText()
        try:
            cusror.execute("DELETE FROM auth_user WHERE username= ? ",(username,))
            database.commit()
            self.update_userlist()
            self.showUsers()
            self.msg.setText(f"User : {username} has been removed!")
        except Exception as e :
            print(e)

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
                        cusror.execute("INSERT INTO login_record (USERNAME, STATUS, COMPUTERNAME) VALUES(?,?,?)",(self.login_id.text(), 'Changed Password', platform.node()))
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
        cusror.execute(f"SELECT * FROM login_count WHERE HOST = '{platform.node()}'")
        host = cusror.fetchall()
        if not host :
            cusror.execute(f"INSERT INTO login_count (HOST, COUNT) VALUES ('{platform.node()}', '5')")
            database.commit()

        if self.username.text() == "" or self.password.text() == "":
            self.fail.setText("Enter Login Id and Password!")
        else:
            cusror.execute(f"SELECT COUNT FROM login_count WHERE HOST = '{platform.node()}'")
            count = cusror.fetchall()
            
            if count[0][0] > 0 :
                password = md5(bytes(self.password.text(),"utf-8")).hexdigest()
                cusror.execute(f"SELECT * FROM auth_user WHERE USERNAME = '{self.username.text()}' AND PASSWORD = '{password}' AND ACTIVATED = '1'")     
                user = cusror.fetchall()
                if user:
                    cusror.execute("INSERT INTO login_record (USERNAME, STATUS, COMPUTERNAME) VALUES(?,?,?)",(self.username.text(), 'Login Success', platform.node()))
                    cusror.execute(f"UPDATE login_count SET COUNT = '5' WHERE HOST = '{platform.node()}'")
                    database.commit()
                    if user[0][3] == 'admin':
                        self.adminPanel()
                    else :
                        print("Welcome to main app!")
                else :
                    cusror.execute(f"UPDATE login_count SET COUNT = '{count[0][0]-1}' WHERE HOST = '{platform.node()}'")
                    cusror.execute("INSERT INTO login_record (USERNAME, STATUS, COMPUTERNAME) VALUES(?,?,?)",(self.username.text(), 'Incorrect Credential', platform.node()))
                    database.commit()
                    self.fail.setText(f"Incorrect Credential! Attempts left : {count[0][0]-1}")    
            else :
                self.fail.setText("Attempts left : 0 Please ask admin to reset count!")

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