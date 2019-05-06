import numpy as np 
import pandas as pd
from flask import Flask, url_for, request, redirect  ,render_template
from flask_login import  LoginManager,UserMixin, login_user, current_user, login_required, logout_user
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash



app=Flask(__name__)
# AML_table=pd.read_csv("txn_records_0411.csv")
#  會使用到session，故為必設。  
app.secret_key = 'AMLxDSTeam'  
#  login\_manager.init\_app(app)也可以  
#  假裝是我們的使用者  
conn=sqlite3.connect("test.db")
c=conn.cursor()
q=c.execute("select * from USER")
users={row[1]:{"password":str(row[2])} for row in q}
login_manager = LoginManager(app)  

# try the following code in terminal
# curl -d '{"acct_nbr":"0000269FB06B6C4D57747751"}' -H "Content-Type: application/json" -X POST http://172.22.142.213:5000/table_filter

@app.route("/")
def hello():
	return render_template("hello.html")

class User(UserMixin):  
    """  
 設置一： 只是假裝一下，所以單純的繼承一下而以 如果我們希望可以做更多判斷，
 如is_administrator也可以從這邊來加入 
 """
    
    pass  
  
  
@login_manager.user_loader  
def user_loader(email):  
    """  
 設置二： 透過這邊的設置讓flask_login可以隨時取到目前的使用者id   
 :param email:官網此例將email當id使用，賦值給予user.id    
 """
    if email not in users:  
        return  
  
    user = User()  
    user.id = email  
    return user  
  
  
@app.route('/login', methods=['GET', 'POST'])  
def login():  
    """  
 官網git很給力的寫了一個login的頁面，在GET的時候回傳渲染     
 """   
    if request.method == 'GET':  
           return render_template("login.html")

    email = request.form['email']  
    # if request.form['password'] == users[email]['password']:
    if check_password_hash(users[email]['password'],request.form['password']):    
        print(users[email]['password'])
        #  實作User類別  
        user = User()  
        #  設置id就是email  
        user.id = email  
        #  這邊，透過login_user來記錄user_id，如下了解程式碼的login_user說明。  
        login_user(user)  
        #  登入成功，轉址  
        return redirect(url_for('protected'))  
    
    return 'Bad login'  
  
  
@app.route('/protected')  
@login_required  
def protected():  
    """  
 在login_user(user)之後，我們就可以透過current_user.id來取得用戶的相關資訊了  
 """   
    #  current_user確實的取得了登錄狀態
    if current_user.is_active:  
        return 'Logged in as: ' + current_user.id + ' Login is_active:True <br>'+ """
        <form action='table_filter' method='POST'>
        <input type='password' name='acct_nbr' id='acct_nbr' placeholder='acct_nbr'/>
	     <input type='submit' name='submit'/>
	     </form>
        """
 
  
@app.route('/logout')  
def logout():  
    """  
 logout\_user會將所有的相關session資訊給pop掉 
 """ 
    logout_user()  
    return 'Logged out'  

@app.route("/table_filter",methods=['GET', 'POST'])
@login_required 
def Table_filter():
    try:
        if request.json:
            acct_nbr=request.json['acct_nbr']
            Target_acct=AML_table[AML_table['acct_nbr']==acct_nbr]['txn_acct'].unique().tolist()    
            output=AML_table[AML_table['acct_nbr'].isin(Target_acct)]
            return output.to_json(orient="records")
        elif request.form:
            acct_nbr=request.form['acct_nbr']
            Target_acct=AML_table[AML_table['acct_nbr']==acct_nbr]['txn_acct'].unique().tolist()
            output=AML_table[AML_table['acct_nbr'].isin(Target_acct)]
            return output.to_json(orient="records")
    except:
        return "Failed"

if __name__=="__main__":
    app.run(host="0.0.0.0")


