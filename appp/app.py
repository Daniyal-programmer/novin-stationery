from flask import redirect,Flask,render_template,request,make_response,url_for,session
import time
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
import requests
import os
app = Flask(__name__)
app.secret_key='fkmlbvkmdlbkmfglknmbportsyhj-ezrsfghbwA$45t46355y13651835517658543646$%&%^^#$TGVFNJGHUYKDRGFVSDGfg'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:@127.0.0.1/flask"
db = SQLAlchemy(app)
csrf = CSRFProtect(app)
#----mysql----
class User(db.Model):
    user_id= db.Column(db.Integer,primary_key=True)
    username= db.Column(db.String(20),nullable=False,unique=True)
    password= db.Column(db.String(20),nullable=False)
    cantact_bool= db.Column(db.String(10),nullable=False,default='False')
    order_bool= db.Column(db.String(10),nullable=False,default='False')
    orders= db.relationship('Orders',back_populates='user')
    cantact= db.relationship('Cantact',back_populates='user')
    payment= db.relationship('Payment',back_populates='user')

class Cantact(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,ForeignKey(User.user_id))
    user_phone_num= db.Column(db.String(11),nullable=False,unique=False)
    user_address= db.Column(db.String(200),nullable=False)
    user_post_cod= db.Column(db.String(10),nullable=False)
    user = db.relationship('User',back_populates='cantact')

class Orders(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,ForeignKey(User.user_id))
    item_name = db.Column(db.String(20),nullable=False)
    item_price = db.Column(db.Integer,nullable=False)
    number_of_item_want = db.Column(db.Integer,nullable=False)
    sent = db.Column(db.String(10),default='False')
    pay = db.Column(db.String(10),default='False')
    time = db.Column(db.Integer,nullable=False)
    user = db.relationship('User',back_populates='orders')



class Items(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(40),nullable=False,unique=True)
    price = db.Column(db.Integer,nullable=False)
    number = db.Column(db.Integer,nullable=False)
    type = db.Column(db.String(20),nullable=False)
    image_address= db.Column(db.String(200),nullable=False)
    description = db.Column(db.String(200),nullable=True)

class Payment(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,ForeignKey(User.user_id))
    token = db.Column(db.Integer)
    price = db.Column(db.Integer)
    status = db.Column(db.Integer)
    refid = db.Column(db.Integer)
    user = db.relationship('User',back_populates='payment')
    
#----home----
@app.route('/')
def home_redirect():
    return redirect('/home')
@app.route('/home',methods=['GET','POST'])
def home():
    if request.method=='GET':
        orders=Orders.query.all()
        timee=time.time()
        for order in orders:
            if timee - order.time >= 43200:
                return redirect('/delete-order/'+str(order.id))
        if session.get('username'):
            items=Items.query.all()
            lenth=len(items)
            num=0
            user_num=str(session.get('username'))
            return render_template('home.html',username=user_num,items=items,lenth=lenth,num=num)
        else:
            items=Items.query.all()
            lenth=len(items)
            num=0
            return render_template('home.html',username='False',items=items,lenth=lenth,num=num)
    else:
        itemname = request.form['item__name']
        session ['item__name'] = itemname

@app.route('/call_us')
def call_us():
        if session.get('username'):
            user_num=str(session.get('username'))
            return render_template('call_us.html',username=user_num)
        else:
            return render_template('call_us.html',username='False')
#----singin----

@app.route('/-singin-/<string>',methods=['GET','POST'])
def singin_(string):
    if request.method=='GET':
        if session.get('username'):
            user_num=str(session.get('username'))
            return render_template('singin.html',username=user_num)
        else:
            return render_template('singin.html',username='False')
    if request.method=='POST':
        user_name=request.form['username']
        pass_word=request.form['password']
        if pass_word=='' or user_name=='':
            return redirect('/singin')
        if len(pass_word) > 20:
            return render_template('singin.html',password='False')
        elif len(user_name) > 20:
            return render_template('singin.html',user__name='False')
        try:
            user=User(username=user_name,password=pass_word)
            db.session.add(user)
            db.session.commit()
            return redirect('/login')
        except:
            return render_template('singin.html',unique='False')


@app.route('/singin',methods=['GET','POST'])
def singin():
    if request.method=='GET':
        if session.get('username'):
            user_num=str(session.get('username'))
            return render_template('singin.html',username=user_num)
        else:
            return render_template('singin.html',username='False')
    if request.method=='POST':
        user_name=request.form['username']
        pass_word=request.form['password']
        if pass_word=='' or user_name=='':
            return redirect('/singin')
        if len(pass_word) > 20:
            return render_template('singin.html',password='False')
        elif len(user_name) > 20:
            return render_template('singin.html',user__name='False')
        try:
            user=User(username=user_name,password=pass_word)
            db.session.add(user)
            db.session.commit()
            return redirect('/login')
        except:
            return render_template('singin.html',unique='False')
    
#----login----

@app.route('/-login-/<string>',methods=['GET','POST'])
def login_(string):
    session ['itemname'] = string
    if string!='':
        if request.method=='GET':
            if session.get('username'):
                user_num=str(session.get('username'))
                return render_template('login.html',username=user_num,item='True',string=string)
            else:
                return render_template('login.html',username='False',item='True',string=string)
        if request.method=='POST':
            user_name=request.form['username']
            pass_word=request.form['password']
            user=User.query.filter(User.username==user_name).first_or_404()
            if user.password == pass_word:
                if session.get('username'):
                    return render_template('login.html',sesion='False',item='True',string=string)
                else:
                    session['username'] = user.username
            else:
                return render_template('login.html',login='False',item='True',string=string)
            user___name=str(session.get('username'))
            user__name=User.query.filter(User.username==user___name).first_or_404()
            return redirect("/add-order")
        else:
            return redirect('/home')
        
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='GET':
        if session.get('username'):
            user_num=str(session.get('username'))
            return render_template('login.html',username=user_num,item='False')
        else:
            return render_template('login.html',username='False',item='False')
    if request.method=='POST':
        user_name=request.form['username']
        pass_word=request.form['password']
        user=User.query.filter(User.username==user_name).first_or_404()
        if user.password == pass_word:
            if session.get('username'):
                return render_template('login.html',sesion='False',item='False')
            else:
                session['username'] = user.username
        else:
            return render_template('login.html',login='False',item='False')
        return redirect('/home')
#----logout----
        
@app.route('/logout',methods=['GET','POST'])
def logout():
    session.pop('username',None)
    return redirect('/home')

# -----------admin-----------
# -----------admin-----------
# -----------admin-----------

@app.route('/admin-login',methods=['GET','POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin_login.html')
    if request.method == 'POST':
        username=request.form['username']
        password=request.form['password']
        if username == 'Mitra' and password == 'Mitra.1369':
            session['admin_bool'] = 'True'
            return redirect('/admin-page')
        else:
            return 'goodbye'
        
@app.route('/admin-logout')
def admin_logout():
    session.pop('admin_bool',None)
    return 'have good day'

@app.route('/admin-page')
def admin_page():
    if session.get('admin_bool') == 'True':
        return render_template('admin_page.html')
    else:
        return 'good bye'

@app.route('/admin-add-item',methods=['GET','POST'])
def admin_add_item():
    if session.get('admin_bool') == 'True':
        if request.method == 'GET':
            return render_template('admin_add_item.html')
        if request.method == 'POST':
            name = request.form['item_name']
            price = request.form['item_price']
            number = request.form['item_number']
            description = request.form['item_description']
            type = request.form['item_type']
            image = request.files['file']
            if image:
                img_address = '../static/uploads/'+str(name)+'.jpg'
                image.save('static/uploads/'+str(name)+'.jpg')
                item=Items(name=name,price=price,number=number,type=type,image_address=img_address,description=description)
                db.session.add(item)
                db.session.commit()
                return redirect('/admin-add-item')
            else:
                return redirect('/admin-add-item')
    else:
        return 'good bye'

@app.route('/admin-update-item',methods=['GET','POST'])
def admin_update_item():
    if session.get('admin_bool') == 'True':
        if request.method == 'GET':
            return render_template('admin_update_item.html',name='True')
        if request.method == 'POST':
            last_name=request.form['last_name']
            item=Items.query.filter(Items.name==last_name).first_or_404()

            new_name=request.form['new_name']
            if new_name!='':
                item.name=new_name
                db.session.commit()

            price = request.form['price']
            if price!='':
                item.price=price
                db.session.commit()

            number = request.form['number']
            if number!='':
                item.number=number
                db.session.commit()

            description = request.form['description']
            if description!='':
                item.description=description
                db.session.commit()
            return redirect('/admin-page')
    else:
        return 'good bye'
@app.route('/admin-delete-item',methods=['GET','POST'])
def admin_delete_item():
    if session.get('admin_bool') == 'True':
        if request.method=='GET':
            return render_template('admin_delete_item.html')
        else:
            item_name=request.form['item_name']
            item=Items.query.filter(Items.name==item_name).first_or_404()
            db.session.delete(item)
            db.session.commit()
            return redirect('/admin-page')
    else:
        return 'good bye'
@app.route('/admin')
def admin_redirect():
    return redirect('/admin-login')


@app.route('/admin-orders')
def admin_orders():
    if session.get('admin_bool') == 'True':
        users=User.query.all()
        for user in users:
            orders=Orders.query.filter(Orders.user_id==user.user_id).all()
            for order in orders:
                if order.pay=='True' and order.sent=='False':
                    user.order_bool='True'
                    db.session.commit()
                else:
                    user.order_bool='False'
                    db.session.commit()
        userss=User.query.all()
        
        return render_template('admin_orders.html',users=userss)
    else:
        return 'good bye'

@app.route('/admin-order-page/<user_id>')
def admin_order_page(user_id):
    if session.get('admin_bool') == 'True':
        user=User.query.filter(User.user_id==user_id).first_or_404()
        orders=Orders.query.filter(Orders.user_id==user.user_id).all()
        cantact=Cantact.query.filter(Cantact.user_id==user.user_id).first_or_404()
        return render_template('admin_order_page.html',user=user,orders=orders,cantact=cantact)
    else:
        return 'good bye'



@app.route('/item/<string>')
def item(string):
    if session.get('username'):
        user_num=str(session.get('username'))
        if string == 'bag':
            items = Items.query.filter(Items.type=='bag')
            return render_template('item.html',items=items,type='True',user__name=str(session.get('username')))
        elif string == 'bottle':
            items = Items.query.filter(Items.type=='bottle')
            return render_template('item.html',items=items,type='True',user__name=user_num)
        elif string == 'Stationery':
            items = Items.query.filter(Items.type=='Stationery')
            return render_template('item.html',items=items,type='True',user__name=user_num)
        elif string == 'gift':
            items = Items.query.filter(Items.type=='gift')
            return render_template('item.html',items=items,type='True',user__name=user_num)
        elif string == 'book':
            items = Items.query.filter(Items.type=='book')
            return render_template('item.html',items=items,type='True',user__name=user_num)
    else:
        if string == 'bottle':
            items = Items.query.filter(Items.type=='bottle')
            return render_template('item.html',items=items,type='True',user__name='False')
        elif string == 'Stationery':
            items = Items.query.filter(Items.type=='Stationery')
            return render_template('item.html',items=items,type='True',user__name='False')
        elif string == 'gift':
            items = Items.query.filter(Items.type=='gift')
            return render_template('item.html',items=items,type='True',user__name='False')
        elif string == 'book':
            items = Items.query.filter(Items.type=='book')
            return render_template('item.html',items=items,type='True',user__name='False')
        elif string == 'bag':
            items = Items.query.filter(Items.type=='bag')
            return render_template('item.html',items=items,type='True',user__name='False')


@app.route('/item-shower/<string>',methods=['GET','POST'])
def item_shower(string):
    item = Items.query.filter(Items.name==string).first_or_404()
    if session.get('username'):
        user_name=session.get('username')
        session['itemname'] = string
        if item.number==0:
            return render_template('item_shower.html',item=item,username=user_name,item_num='False')
        else:
            return render_template('item_shower.html',item=item,username=user_name,item_num='True')
    else:
        return render_template('item_shower.html',item=item,username='False')

@app.route('/add-order')
def add__order():
    user_name=str(session.get('username'))
    user=User.query.filter(User.username==user_name).first_or_404()
    item_name=str(session.get('itemname'))
    item=Items.query.filter(Items.name==item_name).first_or_404()
    return render_template('add_order.html',item_name=item.name,username=user_name,user_name=user.username,num='True')

@app.route('/add_order',methods=['GET','POST'])
def add_order():
    user_name=str(session.get('username'))
    item_name=str(session.get('itemname'))
    item_number=int(request.form['number'])
    user=User.query.filter(User.username==user_name).first_or_404()
    user__name=user.username
    item=Items.query.filter(Items.name==item_name).first_or_404()
    item__name=item.name
    if (item_number) > int(item.number):
        return render_template('add_order.html',item_name=item__name,user_name=user__name,num='False')
    else:
        item_price=item.price
        order=Orders(item_name=item__name,item_price=item_price,number_of_item_want=item_number,time=time.time())
        item.number = int(int(item.number) - int(item_number))
        user.orders.append(order)
        db.session.add(order)
        db.session.commit()
        session.pop('itemname',None)
        return redirect('/orders')

@app.route('/orders')
def orders():
    item_address_list=[]
    user_name=session.get('username')
    user=User.query.filter(User.username==user_name).first_or_404()
    orders=Orders.query.filter(Orders.user_id==user.user_id).all()
    all_price=0
    for order in orders:
        order_price=order.item_price*order.number_of_item_want
        all_price=all_price+order_price
    if user.cantact_bool!=False:
        try:
            Orders.query.filter(Orders.user_id==user.user_id).first_or_404()
            return render_template('orders.html',all_price=all_price,orders=orders,list=item_address_list,username=user_name,cantact=False,peyk_price='حضوری',order='True')
        except:
            return render_template('orders.html',all_price=all_price,orders=orders,list=item_address_list,username=user_name,cantact=False,peyk_price='حضوری',order='False')
    else:
        try:
            Orders.query.filter(Orders.user_id==user.user_id).first()==''
            return render_template('orders.html',all_price=all_price,orders=orders,list=item_address_list,username=user_name,cantact=True,peyk_price='حضوری',order='True')
        except:
            return render_template('orders.html',all_price=all_price,orders=orders,list=item_address_list,username=user_name,cantact=True,peyk_price='حضوری',order='False')

@app.route('/delete-order/<order_id>')
def delete_order(order_id):
    username=session.get('username')
    user=User.query.filter(User.username==username).first_or_404()
    order=Orders.query.filter(Orders.id==order_id).first_or_404()
    item=Items.query.filter(Items.name==order.item_name).first_or_404()
    item.number=item.number+order.number_of_item_want
    db.session.delete(order)
    db.session.commit()
    return redirect('/orders')

@app.route('/cantact',methods=['GET','POST'])
def cantact():
    user_name=session.get('username')
    user=User.query.filter(User.username==user_name).first_or_404()
    if request.method == 'GET':
        try:
            can=Cantact.query.filter(Cantact.user_id==user.user_id).first_or_404()
            return render_template('cantact.html',user=user,username=user.username,complete='True',cantact=can)
        except:
            return render_template('cantact.html',user=user,username=user.username,complete='True',cantact='False')
    else:
        try:
            can=Cantact.query.filter(Cantact.user_id==user.user_id).first_or_404()
            cans=Cantact.query.all()
            user_phone=str(request.form['phone'])
            user_address=request.form['address']
            user_post_cod=str(request.form['post_cod'])
            if user_phone=='' or user_address=='' or user_post_cod=='':
                return render_template('cantact.html',user=user,username=user_name,complete='False',cantact=can)
            for ct in cans :
                if user_phone==ct.number:
                    return redirect('/cantact')
            can.user_phone_num=user_phone
            can.user_address=user_address
            can.user_post_cod=user_post_cod
            db.session.commit()
            return redirect('/orders-pay')
        except:
            cans=Cantact.query.all()
            user_phone=str(request.form['phone'])
            user_address=request.form['address']
            user_post_cod=str(request.form['post_cod'])
            if user_phone=='' or user_address=='' or user_post_cod=='':
                return render_template('cantact.html',user=user,username=user_name,complete='False',cantact='False')
            for ct in cans :
                if user_phone==ct.number:
                    return redirect('/cantact')
            cantact=Cantact(user_phone_num=user_phone,user_address=user_address,user_post_cod=user_post_cod)
            user.cantact.append(cantact)
            user.cantact_bool='True'
            db.session.add(cantact)
            db.session.commit()
            return redirect('/orders-pay')
    
@app.route('/send/<user_id>')
def admin_send(user_id):
    user=User.query.filter(User.user_id==user_id).first_or_404()
    orders=Orders.query.filter(Orders.user_id==user.user_id).all()
    for order in orders:
        if order.pay=='True' and order.sent=='False':
            order.sent='True'
            db.session.commit()
    return redirect('/admin-orders')

@app.route('/orders-pay')
def orders_pay():
    username=session.get('username')
    user=User.query.filter(User.username==username).first_or_404()
    orders=Orders.query.filter(Orders.user_id==user.user_id).all()
    all_price=0
    orders_id=[]
    for order in orders:
        order_price=order.item_price*order.number_of_item_want
        orders_id.append(order.id)
        all_price=all_price+order_price
    all_price=int(all_price)
    r= requests.post('https://next.zarinpal.com/api/v4/graphql/', 
        data={
            'api':'sandbox',
            'amount': all_price,
            'callback':'http://localhost:5000/verify',
            'mobile':'09137034232'
        })
    session ['orders_id'] = orders_id
    token = r.json()['result']['token']
    url = r.json()['result']['url']
    payment=Payment(token=token,price=all_price)
    user.payment.append(payment)
    db.session.add(payment)
    db.session.commit()
    return redirect(url)



@app.route('/verify')
def verify():
    username=session.get('username')
    token_really=request.args.get('token')
    user=User.query.filter(User.username==username).first_or_404()
    orders=Orders.query.filter(Orders.user_id==user.user_id).all()
    orders_id = session.get('orders_id')
    pay=Payment.query.filter(Payment.token==token_really).first_or_404()
    r= requests.post('https://merchant.shepa.com/api/v1/verify', 
        data={
            'api':'sandbox',
            'amount': pay.price,
            'token': token_really
        })
    refid = r.text()['result']['token']
    status = bool(r.text()['success'])
    if status:
        pay.status=status
        pay.refid=refid
        db.session.commit()
        for order in orders:
            if order.id in orders_id:
                order.pay='True'
                db.session.commit()
        return redirect('/orders')
    else:
        pay.status=status
        db.session.commit
        return redirect('/orders')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True , port = 5000)
