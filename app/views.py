from flask import render_template, flash, redirect, request, jsonify
from app import app, db
from .forms import LoginForm
from .models import AFP, Cuota, Patrimonio
from datetime import datetime, date, timedelta
from sqlalchemy import and_, exc
import pygal

fondos = ["A", "B", "C", "D", "E"]
AFPs = ["capital", "cuprum", "habitat", "modelo", "planvital"]

@app.route('/')
@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

@app.route('/afp/personalizado/req/<int:decimales>', methods=['POST'])
def request_personalizado(decimales):
    data = []

    try:
        inicio_usuario = datetime.strptime(request.form['inicio'], '%Y-%m-%d')
        final_usuario = datetime.strptime(request.form['final'], '%Y-%m-%d')

        inicio = getUltimaFechaCuota(None, inicio_usuario)
        final = getUltimaFechaCuota(None, final_usuario)

        rentabilidadPer = {}
        AFPPersonalizado = []

        for afp in AFP.query.all():
            for f in fondos:
                cuotaFinal = afp.cuotas.filter(and_(Cuota.fecha == final,
                                               Cuota.fondo == f)).first()
                cuotaInicio = afp.cuotas.filter(and_(Cuota.fecha == inicio,
                                                     Cuota.fondo == f)).first()

                if cuotaFinal is None or cuotaInicio is None:
                    rentabilidadPer[f] = None
                else:
                    rentabilidadPer[f] = round(((cuotaFinal.valor/cuotaInicio.valor)-1)*100,decimales)

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

    grafico = crearGraficoBarraDesdeDict("Rentabilidad (%)", AFPPersonalizado)

    data.append(AFPPersonalizado)
    data.append(grafico.render())
    data.append([inicio, final])

    return jsonify(data)

@app.route('/afp')
@app.route('/afp/<tab>')
def afp(tab = "hoy"):
    usuario = {'nombre':'Fernando'}

    # Hoy en realidad es el último día para el cual tenemos datos
    hoy = getUltimaFechaCuota()
    ayer = getUltimaFechaCuota(None, hoy-timedelta(1))
    mesTD = getUltimaFechaCuota(None, hoy.replace(day=1))
    anioTD = getUltimaFechaCuota(None, hoy.replace(day=1).replace(month=1))

    AFPDiaria = []
    AFPMesTD = []
    AFPAnioTD = []

    rentabilidadDiaria = {}
    rentabilidadMensual = {}
    rentabilidadAnual = {}

    afps = AFP.query.all()
    for afp in afps:
        for f in fondos:
            cuotaHoy = afp.cuotas.filter(and_(Cuota.fecha == hoy, Cuota.fondo == f)).first()
            cuotaAyer = afp.cuotas.filter(and_(Cuota.fecha == ayer, Cuota.fondo == f)).first()
            cuotaMesTD = afp.cuotas.filter(and_(Cuota.fecha == mesTD, Cuota.fondo == f)).first()
            cuotaAnioTD = afp.cuotas.filter(and_(Cuota.fecha == anioTD, Cuota.fondo == f)).first()

            if cuotaHoy == None or cuotaAyer == None:
                rentabilidadDiaria[f]= None
            else:
                rentabilidadDiaria[f] = round(((cuotaHoy.valor/cuotaAyer.valor)-1)*100,3)

            if cuotaHoy == None or cuotaMesTD == None:
                rentabilidadMensual[f]= None
            else:
                rentabilidadMensual[f] = round(((cuotaHoy.valor/cuotaMesTD.valor)-1)*100,3)

            if cuotaHoy == None or cuotaAnioTD == None:
                rentabilidadAnual[f]= None
            else:
                rentabilidadAnual[f] = round(((cuotaHoy.valor/cuotaAnioTD.valor)-1)*100,3)

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

    graph_dia = crearGraficoBarraDesdeDict("Rentabilidad Diaria (%)", AFPDiaria).render()

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
                            active=tab,
                            graph_dia_data = graph_dia)

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
def getUltimaFechaCuota(afp=None, date= ""):
    if date:
        if afp:
            closest = Cuota.query.filter(_and(Cuota.AFP_id == afp.id, Cuota.fecha<=date)).order_by(Cuota.fecha.desc()).first()
        else:
            closest = Cuota.query.filter(Cuota.fecha<=date).order_by(Cuota.fecha.desc()).first()

    else:
        if afp:
            closest = Cuota.query.filter(Cuota.AFP_id == afp.idCuota.AFP_id == afp.id,).order_by(Cuota.fecha.desc()).first()
        else:
            closest = Cuota.query.order_by(Cuota.fecha.desc()).first()

    return closest.fecha

#@app.route('/scrape_cuotas_svs')
def scrape_cuotas_svs():
    import mechanicalsoup

    try:
        browser = mechanicalsoup.StatefulBrowser(
        soup_config={'features': 'lxml'}    )

        browser.set_verbose(2)

        for f in fondos:
            for i in range(1,28):
                if len(str(i)) == 1:
                    dia ="0"+str(i)
                if len(str(i)) == 2:
                    dia = str(i)

                url = "http://www.safp.cl/safpstats/stats/apps/vcuofon/vcfAFP.php?tf="+f
                browser.open(url)
                browser.select_form("#main form")

                browser["ddVCF"] = dia
                resp = browser.submit_selected()

                page = browser.get_current_page()


                table = page.find_all("table", class_="tw")
                fecha = table[1].find("td", class_="EPIGRAFE")

                if fecha is None:
                    continue

                fecha_str = fecha.get_text()
                fecha_str = fecha_str.split(' ')[0].strip()

                print(fecha_str)

                # fecha_str = fecha_str.split('-')
                # dia_scrape = fecha_str[0]
                # mes_scrape = fecha_str[1]
                # ano_scrape = fecha_str[2]

                import locale
                locale.setlocale(locale.LC_TIME, 'es_ES')

                fecha = datetime.strptime(fecha_str, '%d-%B-%Y').date()

                if fecha.weekday() >= 5:
                    print(fecha)
                    print("Skipped!")
                    continue

                cuotas = page.find_all("td", class_="CONTENIDOcuatro")


                valorCuotaCapital = float(cuotas[0].get_text().replace(".","").replace(",","."))
                valorCuotaCuprum = float(cuotas[2].get_text().replace(".","").replace(",","."))
                valorCuotaHabitat = float(cuotas[4].get_text().replace(".","").replace(",","."))
                valorCuotaModelo = float(cuotas[6].get_text().replace(".","").replace(",","."))
                valorCuotaPlanvital = float(cuotas[8].get_text().replace(".","").replace(",","."))
                valorCuotaProvida = float(cuotas[10].get_text().replace(".","").replace(",","."))

                cuotaCapital = Cuota(fecha=fecha,AFP_id=1,valor=valorCuotaCapital,fondo=f)
                cuotaCuprum = Cuota(fecha=fecha,AFP_id=2,valor=valorCuotaCuprum,fondo=f)
                cuotaHabitat = Cuota(fecha=fecha,AFP_id=3,valor=valorCuotaHabitat,fondo=f)
                cuotaModelo = Cuota(fecha=fecha,AFP_id=4,valor=valorCuotaModelo,fondo=f)
                cuotaPlanvital = Cuota(fecha=fecha,AFP_id=5,valor=valorCuotaPlanvital,fondo=f)
                cuotaProvida = Cuota(fecha=fecha,AFP_id=6,valor=valorCuotaProvida,fondo=f)

                db.session.add(cuotaCapital)
                db.session.add(cuotaCuprum)
                db.session.add(cuotaHabitat)
                db.session.add(cuotaModelo)
                db.session.add(cuotaPlanvital)
                db.session.add(cuotaProvida)

                patrimonioCapital = Patrimonio(fecha=fecha,AFP_id=1,valor=int(cuotas[1].get_text().replace(".","")), fondo=f)
                patrimonioCuprum = Patrimonio(fecha=fecha,AFP_id=2,valor=int(cuotas[3].get_text().replace(".","")), fondo=f)
                patrimonioHabitat = Patrimonio(fecha=fecha,AFP_id=3,valor=int(cuotas[5].get_text().replace(".","")), fondo=f)
                patrimonioModelo = Patrimonio(fecha=fecha,AFP_id=4,valor=int(cuotas[7].get_text().replace(".","")), fondo=f)
                patrimonioPlanvital = Patrimonio(fecha=fecha,AFP_id=5,valor=int(cuotas[9].get_text().replace(".","")), fondo=f)
                patrimonioProvida = Patrimonio(fecha=fecha,AFP_id=6,valor=int(cuotas[11].get_text().replace(".","")), fondo=f)

                db.session.add(patrimonioCapital)
                db.session.add(patrimonioCuprum)
                db.session.add(patrimonioHabitat)
                db.session.add(patrimonioModelo)
                db.session.add(patrimonioPlanvital)
                db.session.add(patrimonioProvida)


                for cuota in cuotas:
                    print(cuota.get_text())

                try:
                    db.session.commit()

                except Exception as e:
                    print("Duplicado")
                    continue

    except Exception as e:
        raise(e)

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

def crearGraficoBarra(titulo, datosEjeX, datosBarra):
    try:
        custom_style = pygal.style.Style(label_font_size=20, title_font_size=30, legend_font_size =20 , tooltip_font_size=20     )
        graph = pygal.Bar(legend_at_bottom=True, legend_box_size=30, style=custom_style, disable_xml_declaration=True)
        graph.title = titulo
        graph.x_labels = datosEjeX

        for columna in datosBarra:
            graph.add(columna[0].title(), columna[1])

        return graph

    except Exception as e:
        raise(e)

def crearGraficoBarraDesdeDict(titulo, dictionarioDatos):
    datosGraficoDiario = []
    for afp in dictionarioDatos:
        rentA = afp['cuotaA']
        rentB = afp['cuotaB']
        rentC = afp['cuotaC']
        rentD = afp['cuotaD']
        rentE = afp['cuotaE']

        if rentA == None:
            rentA = 0

        if rentB == None:
            rentB = 0

        if rentC == None:
            rentC = 0

        if rentD == None:
            rentD = 0

        if rentE == None:
            rentE = 0

        datosGraficoDiario.append([afp['nombre'],[rentA,rentB,rentC,rentD,rentE]])

    return crearGraficoBarra(titulo, ["A","B","C","D","E"], datosGraficoDiario)

@app.errorhandler(404)
def not_found_error(error):
    app.logger.error(exception)
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    app.logger.error(error)
    return render_template('500.html'), 500



