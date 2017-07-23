from flask import render_template, flash, redirect, request
from app import app, db
from .forms import LoginForm
from .models import AFP, Cuota, Patrimonio
from datetime import datetime, date, timedelta
from sqlalchemy import and_,or_

fondos = ["A","B","C","D","E"]
AFPs = ["capital","cuprum","habitat","modelo","planvital"]

@app.route('/')
@app.route('/index', methods=['GET'])
def index():
    usuario = {'nombre':'Fernando'}

    return render_template('index.html',
                            usuario=usuario)

@app.route('/afp')
def afp():
 
    usuario = {'nombre':'Fernando'}
    hoy = date(2017, 6, 30)
    ayer = date(2017, 6, 30)-timedelta(1)
    mes = date(2017, 6, 30)-timedelta(30)
    
    AFPDiaria = []
    for afp in AFP.query.all():
        cuotaAHoy = afp.cuotas.filter(and_(Cuota.fecha == hoy, Cuota.fondo =="A")).first()
        cuotaAAyer = afp.cuotas.filter(and_(Cuota.fecha == ayer, Cuota.fondo =="A")).first()
        rentA = round(((cuotaAHoy.valor/cuotaAAyer.valor)-1)*100,2) 


        AFPDiaria.append({ 
            'nombre': afp.nombre.title(),
            'cuotaA': rentA,
            'cuotaB': '20',
            'cuotaC': '1',
            'cuotaD': '10',
            'cuotaE': '30'
                })

    return render_template('afp.html',
                            usuario = usuario,
                            AFPDiaria = AFPDiaria, 
                            hoy = hoy,
                            ayer = ayer,
                            request=request)    


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

@app.route('/load_csv')
def load_csv():
    import csv

    baseVacia = True

    if baseVacia == True:
        capital = AFP(id=1, nombre="capital")
        cuprum = AFP(id=2, nombre="cuprum")
        habitat = AFP(id=3, nombre="habitat")
        modelo = AFP(id=4, nombre="modelo")
        planvital = AFP(id=5, nombre="planvital")
        provida = AFP(id=6, nombre="provida")

        db.session.add(capital)
        db.session.add(cuprum)
        db.session.add(habitat)
        db.session.add(modelo)
        db.session.add(planvital)
        db.session.add(provida)

        db.session.commit()

    else:
        capital = AFP.query.filter_by(nombre="capital").first()
        cuprum = AFP.query.filter_by(nombre="cuprum").first()
        habitat = AFP.query.filter_by(nombre="habitat").first()
        modelo = AFP.query.filter_by(nombre="modelo").first()
        planvital = AFP.query.filter_by(nombre="planvital").first()
        provida = AFP.query.filter_by(nombre="provida").first()

    for f in fondos:       
        with open('csv/vcf'+f+'2012-2017.csv', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            for row in reader:
                if len(row)>12:
                    if row[0] != "":
                        print('Fecha: '+row[0]+" . Cuota Capital: "+row[1]+" Cuota Cuprum: "+
                        row[3]+" Cuota Habitat: "+row[5]+" Cuota Modelo: "+row[7]+" Cuota PlanV: "+row[9]+" PROVIDA:"+row[11])

                        fecha = datetime.strptime(row[0], '%Y-%m-%d').date()

                        row[1] = float(row[1].replace(".","").replace(",","."))
                        row[3] = float(row[3].replace(".","").replace(",","."))
                        row[5] = float(row[5].replace(".","").replace(",","."))
                        row[7] = float(row[7].replace(".","").replace(",","."))
                        row[9] = float(row[9].replace(".","").replace(",","."))
                        row[11] = float(row[11].replace(".","").replace(",","."))

                        print(capital)
                        cuotaCapital = Cuota(fecha=fecha,AFP_id=capital.id,valor=row[1],fondo=f)
                        cuotaCuprum = Cuota(fecha=fecha,AFP_id=cuprum.id,valor=row[3],fondo=f)
                        cuotaHabitat = Cuota(fecha=fecha,AFP_id=habitat.id,valor=row[5],fondo=f)
                        cuotaModelo = Cuota(fecha=fecha,AFP_id=modelo.id,valor=row[7],fondo=f)
                        cuotaPlanvital = Cuota(fecha=fecha,AFP_id=planvital.id,valor=row[9],fondo=f)
                        cuotaProvida = Cuota(fecha=fecha,AFP_id=provida.id,valor=row[11],fondo=f)
                        
                        db.session.add(cuotaCapital)
                        db.session.add(cuotaCuprum)
                        db.session.add(cuotaHabitat)
                        db.session.add(cuotaModelo)
                        db.session.add(cuotaPlanvital)
                        db.session.add(cuotaProvida)

                        patrimonioCapital = Patrimonio(fecha=fecha,AFP_id=capital.id,valor=int(row[2]), fondo=f)
                        patrimonioCuprum = Patrimonio(fecha=fecha,AFP_id=cuprum.id,valor=int(row[4]), fondo=f)
                        patrimonioHabitat = Patrimonio(fecha=fecha,AFP_id=habitat.id,valor=int(row[6]), fondo=f)
                        patrimonioModelo = Patrimonio(fecha=fecha,AFP_id=modelo.id,valor=int(row[8]), fondo=f)
                        patrimonioPlanvital = Patrimonio(fecha=fecha,AFP_id=planvital.id,valor=int(row[10]), fondo=f)
                        patrimonioProvida = Patrimonio(fecha=fecha,AFP_id=provida.id,valor=int(row[12]), fondo=f)
                        
                        db.session.add(patrimonioCapital)
                        db.session.add(patrimonioCuprum)
                        db.session.add(patrimonioHabitat)
                        db.session.add(patrimonioModelo)
                        db.session.add(patrimonioPlanvital)
                        db.session.add(patrimonioProvida)

                        db.session.commit()

    return render_template('index.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500



