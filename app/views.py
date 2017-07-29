from flask import render_template, flash, redirect, request, jsonify
from app import app, db
from .forms import LoginForm
from .models import AFP, Cuota, Patrimonio
from datetime import datetime, date, timedelta
from sqlalchemy import and_
import pygal

fondos = ["A", "B", "C", "D", "E"]
AFPs = ["capital", "cuprum", "habitat", "modelo", "planvital"]


@app.route('/')
@app.route('/index', methods=['GET'])
def index():
    usuario = {'nombre': 'Fernando'}

    return render_template('index.html', usuario=usuario)


@app.route('/afp/personalizado/req', methods=['POST'])
def request_personalizado():
    try:
        inicio_usuario = datetime.strptime(request.form['inicio'], '%Y-%m-%d')
        final_usuario = datetime.strptime(request.form['final'], '%Y-%m-%d')

        inicio = getUltimaFechaCuota("", inicio_usuario)
        final = getUltimaFechaCuota("", final_usuario)

        rentabilidadPer = {}
        AFPPersonalizado = []

        for afp in AFP.query.all():
            for f in fondos:
                cuotaFinal = afp.cuotas.filter(and_(Cuota.fecha == final,
                                               Cuota.fondo == f)).first()
                cuotaInicio = afp.cuotas.filter(and_(Cuota.fecha == inicio,
                                                     Cuota.fondo == f)).first()

                if cuotaFinal is None or cuotaInicio is None:
                    rentabilidadPer[f] = "S/I"
                else:
                    rentabilidadPer[f] = "%.2f" % round(((cuotaFinal.valor/cuotaInicio.valor)-1)*100,2) +"%"

            AFPPersonalizado.append({
            'nombre': afp.nombre.title(),
            'cuotaA': rentabilidadPer['A'],
            'cuotaB': rentabilidadPer['B'],
            'cuotaC': rentabilidadPer['C'],
            'cuotaD': rentabilidadPer['D'],
            'cuotaE': rentabilidadPer['E'],
            'inicio': inicio,
            'final': final
                })

    except Exception as e:
        render_template("500.html", error = str(e))

    return jsonify(AFPPersonalizado)

@app.route('/afp')
@app.route('/afp/<tab>')
def afp(tab = "hoy"):
    usuario = {'nombre':'Fernando'}

    # Hoy en realidad es el último día para el cual tenemos datos
    hoy = getUltimaFechaCuota()
    ayer = getUltimaFechaCuota("", hoy-timedelta(1))
    mesTD = getUltimaFechaCuota("",hoy.replace(day=1))
    anioTD = getUltimaFechaCuota("",hoy.replace(day=1).replace(month=1))

    AFPDiaria = []
    AFPMesTD = []
    AFPAnioTD = []

    rentabilidadDiaria = {}
    rentabilidadMensual = {}
    rentabilidadAnual = {}

    for afp in AFP.query.all():
        for f in fondos:
            cuotaHoy = afp.cuotas.filter(and_(Cuota.fecha == hoy, Cuota.fondo == f)).first()
            cuotaAyer = afp.cuotas.filter(and_(Cuota.fecha == ayer, Cuota.fondo == f)).first()
            cuotaMesTD = afp.cuotas.filter(and_(Cuota.fecha == mesTD, Cuota.fondo == f)).first()
            cuotaAnioTD = afp.cuotas.filter(and_(Cuota.fecha == anioTD, Cuota.fondo == f)).first()

            if cuotaHoy == None or cuotaAyer == None:
                rentabilidadDiaria[f]="S/I"
            else:
                rentabilidadDiaria[f] = "%.2f" % round(((cuotaHoy.valor/cuotaAyer.valor)-1)*100,2) +"%"

            if cuotaHoy == None or cuotaMesTD == None:
                rentabilidadMensual[f]="S/I"
            else:
                rentabilidadMensual[f] = "%.2f" % round(((cuotaHoy.valor/cuotaMesTD.valor)-1)*100,2) +"%"

            if cuotaHoy == None or cuotaAnioTD == None:
                rentabilidadAnual[f]="S/I"
            else:
                rentabilidadAnual[f] = "%.2f" % round(((cuotaHoy.valor/cuotaAnioTD.valor)-1)*100,2) +"%"

        AFPDiaria.append({
            'nombre': afp.nombre.title(),
            'cuotaA': rentabilidadDiaria['A'],
            'cuotaB': rentabilidadDiaria['B'],
            'cuotaC': rentabilidadDiaria['C'],
            'cuotaD': rentabilidadDiaria['D'],
            'cuotaE': rentabilidadDiaria['E']
                })
        AFPMesTD.append({
            'nombre': afp.nombre.title(),
            'cuotaA': rentabilidadMensual['A'],
            'cuotaB': rentabilidadMensual['B'],
            'cuotaC': rentabilidadMensual['C'],
            'cuotaD': rentabilidadMensual['D'],
            'cuotaE': rentabilidadMensual['E']
                })
        AFPAnioTD.append({
            'nombre': afp.nombre.title(),
            'cuotaA': rentabilidadAnual['A'],
            'cuotaB': rentabilidadAnual['B'],
            'cuotaC': rentabilidadAnual['C'],
            'cuotaD': rentabilidadAnual['D'],
            'cuotaE': rentabilidadAnual['E']
                })

    return render_template('afp.html',
                            usuario = usuario,
                            AFPDiaria = AFPDiaria,
                            AFPMensual = AFPMesTD,
                            mesTD =mesTD,
                            AFPAnual = AFPAnioTD,
                            anioTD = anioTD,
                            hoy = hoy,
                            ayer = ayer,
                            request=request,
                            active=tab)

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

# date: Date of refence. Empty: Last in the database
def getUltimaFechaCuota(afp = "", date= ""):
    if date:
        if afp:
            closest = Cuota.query.filter(_and(AFP.nombre == afp, Cuota.fecha<=date)).order_by(Cuota.fecha.desc()).first()
        else:
            closest = Cuota.query.filter(Cuota.fecha<=date).order_by(Cuota.fecha.desc()).first()

    else:
        if afp:
            closest = Cuota.query.filter(AFP.nombre == afp).order_by(Cuota.fecha.desc()).first()
        else:
            closest = Cuota.query.order_by(Cuota.fecha.desc()).first()

    return closest.fecha

#@app.route('/scrape_cuotas_svs')
def scrape_cuotas_svs():
    import mechanicalsoup

    browser = mechanicalsoup.StatefulBrowser(
    soup_config={'features': 'lxml'}    )

    browser.set_verbose(2)
    url = "http://www.safp.cl/safpstats/stats/apps/vcuofon/vcfAFP.php?tf=A"
    browser.open(url)
    browser.select_form("vcf")
    browser["ddVCF"]=19

    resp = browser.submit_selected()

    page = browser.get_current_page()

    return ffmm()

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

def crearGraficoLinea(titulo, nombresEjeX):
    try:
        graph = pygal.Line()
        graph.title = titulo
        graph.x_labels = nombresEjeX
    except Exception as e:
        render_template("500.html", error = str(e))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500



