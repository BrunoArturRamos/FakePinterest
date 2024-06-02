# criar as rotas do nosso site (os link)
from flask import render_template, url_for, redirect
from fakePinterest import app, database, bcrypt
from flask_login import login_required, login_user, logout_user, current_user
from fakePinterest.forms import formLogin, formCriarConta, FormFotos
from fakePinterest.models import Usuario, Foto
import os
from werkzeug.utils import secure_filename

@app.route("/", methods=['GET', 'POST'])
def homepage():
    form_login = formLogin()
    if form_login.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
            login_user(usuario)
            return redirect(url_for("perfil", id_usuario=usuario.id))
    return render_template("homepage.html", form=form_login)


@app.route("/criarconta", methods=['GET', 'POST'])
def criarconta():
    form_criar_conta = formCriarConta()
    if form_criar_conta.validate_on_submit():
        print("entrou")
        senha = bcrypt.generate_password_hash(form_criar_conta.senha.data)
        usuario = Usuario(username=form_criar_conta.username.data,
                          senha=senha, email=form_criar_conta.email.data,)
        database.session.add(usuario)
        database.session.commit()
        login_user(usuario, remember=True)
        return redirect(url_for("perfil", id_usuario=usuario.id))
    return render_template("criarConta.html", form=form_criar_conta)


@app.route("/perfil/<id_usuario>", methods=["GET", "POST"])
@login_required
def perfil(id_usuario):
    if int(id_usuario) == int(current_user.id):
        # Usuario ta vendo o perfil dele
        form_foto = FormFotos()
        if form_foto.validate_on_submit():
            arquivo = form_foto.foto.data
            nome_seguro = secure_filename(arquivo.filename)
            #salvar o arquivo na pasta form_post
            caminho = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                              app.config['UPLOAD_FOLDER'], nome_seguro)
            arquivo.save(caminho)
             #registrar esse arquivo no banco de dados
            foto = Foto(imagem=nome_seguro, id_usuario=current_user.id)
            database.session.add(foto)
            database.session.commit()
        return render_template("perfil.html", usuario=current_user, form=form_foto)
    else:
        usuario = Usuario.query.get(int(id_usuario))
        return render_template("perfil.html", usuario=usuario, form=None)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("homepage"))

@app.route("/feed")
@login_required
def feed():
    fotos = Foto.query.order_by(Foto.data_criacao).all()
    return render_template("feed.html", fotos=fotos)