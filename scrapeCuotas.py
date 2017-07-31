#!/home/flaskuser/myprojectenv/bin/python
from app import app, db
from app.models import AFP, Cuota, Patrimonio
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
import mechanicalsoup
import locale
from datetime import datetime

fondos = ["A", "B", "C", "D", "E"]

try:
    print("Iniciando. Hora: "+str(datetime.now()))
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    browser = mechanicalsoup.StatefulBrowser(soup_config={'features': 'lxml'})
    afps = AFP.query.all()

    for f in fondos:
        print("Fondo: "+f)
        url = "http://www.safp.cl/safpstats/stats/apps/vcuofon/vcfAFP.php?tf="+f
        browser.open(url)
        page = browser.get_current_page()

        fechaDisponible = page.find_all("td", class_="CONTENIDOdos")
        fechaDisponible = fechaDisponible[1].get_text()
        fechaDisponible = datetime.strptime(fechaDisponible, '%d-%b-%Y').date()

        cuotas = page.find_all("td", class_="CONTENIDOcuatro")

        tableFechas = page.find_all("table", class_="tw")
        fecha = tableFechas[1].find("td", class_="EPIGRAFE")
        fecha_str = fecha.get_text()
        fecha_str = fecha_str.split(' ')[0].strip()

        print("Fecha disponible: "+str(fecha_str))
        fecha = datetime.strptime(fecha_str, '%d-%B-%Y').date()
        
        for afp in afps:
            closest_cuota = Cuota.query.filter(
                      and_(Cuota.AFP_id == afp.id, Cuota.fondo == f)).order_by(Cuota.fecha.desc()).first()

            closest_patrimonio = Patrimonio.query.filter(
                      and_(Patrimonio.AFP_id == afp.id, Patrimonio.fondo == f)).order_by(Patrimonio.fecha.desc()).first()

            if closest_cuota.fecha < fechaDisponible:
                indice_cuota = (afp.id - 1) * 2

                try:
                    valorCuota = float(cuotas[indice_cuota].get_text().replace(".", "").replace(",", "."))
                except ValueError:
                    print("Not a float")
                    continue

                cuota_a_guardar = Cuota(fecha=fecha,AFP_id=afp.id,valor=valorCuota,fondo=f) 
                db.session.add(cuota_a_guardar)

                try:
                    db.session.commit()
                    print("Guardado Cuota: "+str(cuota_a_guardar))

                except Exception as e:
                    print("Duplicado u otro error: "+str(e))
                    db.session.rollback()
                    continue

            if closest_patrimonio.fecha < fechaDisponible:
                indice_patrimonio = (afp.id * 2) - 1
                valorPatrimonio = int(cuotas[indice_patrimonio].get_text().replace(".",""))
                patrimonio_a_guardar = Patrimonio(fecha=fecha,AFP_id=afp.id,valor=valorPatrimonio, fondo=f)
                db.session.add(patrimonio_a_guardar)

                try:
                    db.session.commit()
                    print("Guardado Patrimonio: "+str(patrimonio_a_guardar))

                except Exception as e:
                    print("Duplicado u otro error: "+str(e))
                    continue
            # else:
            #     print("Esa fecha ya está: "+str(closest.fecha))

except Exception as e:
    print("ERROR:"+str(e))