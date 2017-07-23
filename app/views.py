from flask import render_template, flash, redirect, request
from app import app
from .forms import LoginForm

@app.route('/')
@app.route('/index', methods=['GET'])
def index():
    usuario = {'nombre':'Fernando'}

    return render_template('index.html',
                            usuario=usuario)

@app.route('/afp')
def afp():

    usuario = {'nombre':'Fernando'}


    AFPDiaria = [  # fake array of AFPs
        { 
            'nombre': 'Modelo',
            'cuotaA': '30',
            'cuotaB': '20',
            'cuotaC': '10',
            'cuotaD': '10',
            'cuotaE': '30'
        },
        { 
            'nombre': 'Capital',
            'cuotaA': '100',
            'cuotaB': '70',
            'cuotaC': '70',
            'cuotaD': '70',
            'cuotaE': '70'
        }]

    return render_template('afp.html',
                            usuario = usuario,
                            AFPDiaria = AFPDiaria, request=request)    


@app.route('/ffmm')
def ffmm():
    usuario = {'nombre':'Fernando'}

    BancoChile = [  # fake array of AFPs
        { 
            'nombre': 'Modelo',
            'cuotaA': '30',
            'cuotaB': '20',
            'cuotaC': '10',
            'cuotaD': '10',
            'cuotaE': '30'
        },
        { 
            'nombre': 'Capital',
            'cuotaA': '100',
            'cuotaB': '70',
            'cuotaC': '70',
            'cuotaD': '70',
            'cuotaE': '70'
        }]

    return render_template('ffmm.html',
                            usuario = usuario,
                            BancoChile = BancoChile, request=request)    


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for OpenID="%s", remember_me=%s' %
              (form.openid.data, str(form.remember_me.data)))
        return redirect('/index')
    return render_template('login.html', 
                           title='Sign In',
                           form=form,
                           providers=app.config['OPENID_PROVIDERS'])

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500



