import datetime
import os
from requests import post, get

from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_user, logout_user, login_required
from flask_restful import Api

from data import db_session, shoes_api
from data.users import User
from forms.ShoeForm import ShoeForm
from forms.loginForm import LoginForm
from forms.registerForm import RegisterForm

#   создаём приложение
app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.permanent_session_lifetime = datetime.timedelta(days=365)

#   добавляем авторизацию
login_manager = LoginManager()
login_manager.init_app(app)


#   загружаем пользователя
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


#   обработчик входа
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template("login.html", message="Incorrect login or password", form=form)
    return render_template("login.html", form=form, title="Login")


#   обработчик для выхода из аккаунта
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")


#   обработчик для выполнения регистрации
@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        #   добавление в пользователя в бд
        user = User(
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


#   обработчик добавления кроссовка
@app.route("/add_shoe", methods=["POST", "GET"])
def add_shoe():
    form = ShoeForm()
    if form.validate_on_submit():
        for i in form.images.data:
            path = f"static/img/{form.name.data}"   # создаёт новую папку для фото если её нету
            if not os.path.exists(path):
                os.makedirs(path)
            with open(path + "/" + i.filename, "wb") as new_image:
                new_image.write(i.read())
        post("https://flask-production-fcd9.up.railway.app/api/shoes", json={"name": form.name.data,
                                                      "category": form.category.data,
                                                      "price": form.price.data})    # используется API \
                                                                                    # для добавления кроссовка
        return redirect("/")
    return render_template("shoe.html", form=form)


# обработчик для пред просмотра кроссовка
@app.route("/show_shoe/<int:shoe_id>")
def show_shoe(shoe_id):
    shoe = get(f"https://flask-production-fcd9.up.railway.app/api/shoe/{shoe_id}").json()  # запрос к API для получения нужного кроссовка по id
    return render_template("shoe_preview.html", shoe=shoe["shoe"])


# обработчик для главной страницы
@app.route("/")
def index():
    shoes_data = get("https://flask-production-fcd9.up.railway.app/api/shoes").json()["shoes"]    # запрос к API для получения всех кроссовок
    return render_template("shoes_list.html", shoes_data=shoes_data)


if __name__ == '__main__':
    # подключаемся к бд
    db_session.global_init("db/users_data.db")
    # добавляем ресурсы
    # для списка объектов
    api.add_resource(shoes_api.ShoeResource, '/api/shoe/<int:shoe_id>')

    # для одного объекта
    api.add_resource(shoes_api.ShoesListResource, '/api/shoes')
    app.run(host="0.0.0.0", port=5000, debug=True)
