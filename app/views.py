from app import app, db
from flask import render_template, request, flash, redirect, session, url_for,abort
from .models import User, News, Service, Orders
from hashlib import md5
from  sqlalchemy.sql.expression import func
from cloudipsp import Api, Checkout

import qrcode
import uuid
import os
from werkzeug.utils import secure_filename


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/auth',methods=['GET','POST'])
def auth():
    if request.method == 'POST':
        email = request.form.get('email')
        password = md5(request.form.get('password').encode()).hexdigest()
        user = User.query.filter_by(email=email,password=password).first()
        if user:
            session['name'] = User.query.filter_by(email=email).first().email
            return redirect(url_for("index"))
        else:
            flash("Неправильная почта или пароль!", category="bad")
            return redirect(url_for("auth"))
    return render_template("auth.html")


@app.route('/reg',methods=['GET','POST'])
def reg():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            surname = request.form.get('surname')
            phone = request.form.get('phone')
            email = request.form.get('email')
            password = request.form.get('password')
            user = User.query.filter_by(email=email).first()
            user = User(name=name,surname=surname,email=email,phone=phone,password=md5(password.encode()).hexdigest())
            db.session.add(user)
            db.session.commit()
            flash("Регистрация прошла успешно!", category="ok")
        except:
            flash("Произошла ошибка! Проверьте введенные данные!", category="bad")
            db.session.rollback()
    return render_template("reg.html")


@app.route('/contacts',methods=['GET','POST'])
def contacts():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
    return render_template("contacts.html")


@app.route('/news',methods=['GET','POST'])
def news():
    news = News.query.order_by(News.date.desc()).all()
    if request.method == 'POST':
        try:
            title = request.form.get('title')
            category = request.form.get('category')
            text = request.form.get('ckeditor')
            image = request.files['image']
            filename = secure_filename(image.filename)
            pic_name = str(uuid.uuid4()) + "_" + filename
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
            news = News(title=title,category=category,text=text,image_name=pic_name)
            db.session.add(news)
            db.session.commit()
            flash("Запись добавлена!", category="ok")
            return redirect(url_for("news"))
        except:
            flash("Произошла ошибка!", category="bad")

    if request.method == 'GET':
        seach = request.args.get('seach')
        if seach:
            seach= seach.capitalize()
            seach = "%{}%".format(seach)
            news_category = News.query.filter(News.category.like(seach) | News.title.like(seach)).all()
            return render_template("news.html",news=news_category)
        else:
             return render_template("news.html",news=news)
    return render_template("news.html",news=news)


@app.route('/news-page/<int:id>')
def news_page(id):
    news = News.query.get(id)
    if news:
        all_news = News.query.filter(News.id!=news.id, News.category==news.category).order_by(func.random()).limit(3).all()
    else:
        abort(404)
    return render_template("news-page.html",news=news,all_news=all_news)

@app.route('/edit-news/<int:id>',methods=['GET','POST'])
def edit_news(id):
    if request.method == 'POST':
        try:
            title = request.form.get('title')
            category = request.form.get('category')
            text = request.form.get('ckeditor')
            image = request.files['image']
            news = News.query.filter_by(id=id).first()
            news.title = title
            news.category = category
            news.text = text
            if image:
                filename = secure_filename(image.filename)
                pic_name = str(uuid.uuid4()) + "_" + filename
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
                news.image_name = pic_name
            db.session.commit()
            flash("Запись обновлена!", category="ok")
            return redirect(url_for("news"))
        except:
            flash("Произошла ошибка!", category="bad")
    return redirect('/news')


@app.route('/delete-news/<int:id>')
def delete_news(id):
    obj = News.query.filter_by(id=id).first()
    db.session.delete(obj)
    db.session.commit()
    return redirect('/news')

@app.route('/services')
def services():
    service = Service.query.all()

    return render_template("services.html",service=service)


@app.route('/user_service_list')
def user_service_list():
    user = User.query.filter_by(email=session['name']).first()
    orders = Orders.query.filter_by(user_id=user.id).all()
    return render_template("user_service_list.html",orders=orders)


@app.route('/buy_service/<int:price>/<string:service_name>/<string:service_type>')
def buy_service(price,service_name,service_type):
    if 'name' in session:
        user = User.query.filter_by(email=session['name']).first()
        list_qr = [str(price),service_name,service_type,user.name,user.surname,user.email]
        separator = "/"
        data = separator.join(list_qr)
        qr_image = qrcode.make(data)
        qr_name = str(uuid.uuid4()) + ".png"
        qr_image.save("app/static/qr/" +  qr_name)

        orders = Orders(price=price,service_name=service_name,service_type=service_type,qr_image_name=qr_name,user_id = user.id)
        db.session.add(orders)
        db.session.commit()
        api = Api(merchant_id=1396424,secret_key='test')
        checkout = Checkout(api=api)
        data = {
            "currency": "BYN",
            "amount": str(price) + "00"
        }
        url = checkout.url(data).get('checkout_url')
        return redirect(url)
    else:
        return redirect('/auth')

@app.route('/shop')
def shop():
    return render_template("shop.html")


@app.route('/shop-page')
def shop_page():
    return render_template("shop-page.html")


@app.route('/logout')
def logout():
    session.pop('name', None)
    return redirect('/')
    

@app.context_processor
def inject_user():
    def get_user_name():
        if 'name' in session:
            return User.query.filter_by(email=session['name']).first()
    return dict(active_user=get_user_name())


@app.context_processor
def inject_user():
    return dict(
    category=db.session.query(News.category).distinct().all(),
    )


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

@app.errorhandler(401)
def  error_unauthorized(e):
    # note that we set the 404 status explicitly
    return render_template('401.html'), 401

@app.errorhandler(403)
def forbidded(e):
    # note that we set the 404 status explicitly
    return render_template('403.html'), 403