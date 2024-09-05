from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import random
from datetime import datetime

app = Flask(__name__)

# 连接数据库
db = mysql.connector.connect(
    host="localhost",
    user="hrkq",
    passwd="Qaz1121zz",
    database="hrkq"
)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # 生成病例号
        case_number = datetime.now().strftime("%y%m%d") + str(random.randint(1000, 9999))
        
        # 获取表单数据
        name = request.form['name']
        telephone = request.form['telephone']
        implant = request.form['implant']
        position = request.form['position']
        quantity = request.form['quantity']
        total = request.form['total']
        notes = request.form['notes']
        # 获取当前日期
        creation_date = datetime.now().date()
        
        # 插入数据到数据库
        cursor = db.cursor()
        query = ("INSERT INTO invisible_bill (case_number, name, telephone, implant, position, quantity, total, notes, creation_date) "
                 "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")
        data = (case_number, name, telephone, implant, position, quantity, total, notes, creation_date)
        try:
            cursor.execute(query, data)
            db.commit()
            return redirect(url_for('index'))
        except mysql.connector.Error as err:
            print("Error: ", err)
            return "Error occurred"

    if request.method == 'POST':
        # 获取表单数据
        total = float(request.form['total'])
        notes = request.form['notes']
        
        # 检查总价是否为负数且备注为空
        if total < 0 and not notes.strip():
            return "请输入退款原因", 400
        
        # 插入数据到数据库的逻辑...
        # ...

        return redirect(url_for('index'))

    return render_template('index.html')

@app.route('/query_combined', methods=['GET'])
def query_combined():
    search_term = request.args.get('search')
    cursor = db.cursor()
    
    if search_term:
        try:
            # 构建查询条件
            query = """
            SELECT * FROM invisible_bill
            WHERE name = %s OR telephone = %s
            """
            cursor.execute(query, (search_term, search_term))
            results = cursor.fetchall()
            return render_template('query_results.html', results=results)
        except mysql.connector.Error as err:
            print("Error: ", err)
            return "查询失败", 500
    else:
        return "请输入搜索条件", 400

#@app.route('/query', methods=['GET'])
#def query():
#    name = request.args.get('name')
#    telephone = request.args.get('telephone')
#    cursor = db.cursor()

    # 构建查询条件
#    condition = []
#    params = []
#    if name:
#        condition.append("name = %s")
#        params.append(name)
#    if telephone:
#        condition.append("telephone = %s")
#        params.append(telephone)

#    if condition:
#        query = "SELECT * FROM invisible_bill WHERE " + " OR ".join(condition)
#        cursor.execute(query, tuple(params))
#        results = cursor.fetchall()
#        return render_template('query_results.html', results=results)
#    else:
#        return "No search terms provided", 400
    
@app.route('/delete', methods=['POST'])
def delete():
    case_number = request.form['case_number']
    cursor = db.cursor()

    try:
        delete_query = "DELETE FROM invisible_bill WHERE case_number = %s"
        cursor.execute(delete_query, (case_number,))
        db.commit()
        return redirect(url_for('index'))
    except mysql.connector.Error as err:
        print("Error: ", err)
        db.rollback()
        return "删除失败", 500
    
@app.route('/search_by_date', methods=['GET'])
def search_by_date():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    cursor = db.cursor()

    if start_date and end_date:
        try:
            # 构建查询条件
            query = """
            SELECT * FROM invisible_bill
            WHERE creation_date BETWEEN %s AND %s
            """
            cursor.execute(query, (start_date, end_date))
            results = cursor.fetchall()
            
            # 计算总价合计
            total_sum_query = "SELECT SUM(total) FROM invisible_bill WHERE creation_date BETWEEN %s AND %s"
            cursor.execute(total_sum_query, (start_date, end_date))
            total_sum = cursor.fetchone()[0] or 0  # 如果没有结果，则默认为0
            print(total_sum)  # 打印总价合计值
            
            return render_template('query_results.html', results=results, total_sum=total_sum)
        except mysql.connector.Error as err:
            print("Error: ", err)
            return "查询失败", 500
    else:
        return "请提供有效的日期范围", 400

if __name__ == '__main__':
    app.run(debug=True)