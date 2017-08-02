#!/home/flaskuser/myprojectenv/bin/python
from app import app, db
from app.models import AFP, Cuota, Patrimonio
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
import mechanicalsoup
import locale
from datetime import datetime, timedelta
import requests
import json

fondos = ["A", "B", "C", "D", "E"]

id_afp = {'capital': 1,
          'cuprum': 2,
          'habitat': 3,
          'modelo': 4,
          'planvital': 5,
          'provida': 6}

def scrapeProvida(browser):
    try:
        print("Inicia Provida")
        url = "https://w3.provida.cl/Sitio/personastridion/valor_cuota_por_tipo_fondo.asp"
        browser.open(url)
        page = browser.get_current_page()

        fechaDisponible = page.find("p", class_="mBot15") # Fuente: Valor Futuro, 31-07-2017
        fechaDisponible = fechaDisponible.get_text().split(",")[1].strip()
        fechaDisponible = datetime.strptime(fechaDisponible,'%d-%m-%Y').date()

        cuotas = page.find_all("td", class_="cBlack")

        for f, cuota in zip(fondos,cuotas):
            closest_cuota = Cuota.query.filter(
                             and_(Cuota.AFP_id == id_afp['provida'], Cuota.fondo == f)).order_by(Cuota.fecha.desc()).first()

            if closest_cuota.fecha < fechaDisponible:
                valorCuota = float(cuota.get_text().strip().replace(".","").replace(",","."))
                guardarCuota(fechaDisponible, closest_cuota, valorCuota, f, id_afp['provida'], "Web Provida")

        print(fechaDisponible)
    except Exception as e:
        print(e)

def scrapeCuprum(browser):
    try:
        print("Inicia Cuprum")
        url = "https://www.cuprum.cl/ApiSitiopublico/SeriesValorCuota/ValorCuotaDiario"
        r = requests.get(url)

        json_acceptable_string = r.text.replace("'", "\"")
        d = json.loads(json_acceptable_string)

        fechaDisponible = d['valores_cuota']['fecha_actualizacion'].replace("T00:00:00","")
        fechaDisponible = datetime.strptime(fechaDisponible,'%Y-%m-%d').date()

        for f in fondos:
            closest_cuota = Cuota.query.filter(
                            and_(Cuota.AFP_id == id_afp['cuprum'], Cuota.fondo == f)).order_by(Cuota.fecha.desc()).first()

            if closest_cuota.fecha < fechaDisponible:
                llave = "fondo_"+f.lower()
                valorCuota = float(d['valores_cuota'][llave].replace(",","."))
                guardarCuota(fechaDisponible, closest_cuota, valorCuota, f, id_afp['cuprum'], "Web Cuprum")

    except Exception as e:
        print("Error Cuprum: "+str(e))

def guardarCuota(fecha, closest_cuota, valorCuota, f, id_AFP, origen):
    dia_de_la_semana = fecha.weekday()
    dia_anterior = fecha - timedelta(days=1)
    dia_antesdeayer = fecha - timedelta(days=2)
    cuota = False
    finde = False

    if(dia_de_la_semana == 5 and closest_cuota.fecha < dia_anterior):
        # Viernes
        cuota_a_guardar = Cuota(fecha=dia_anterior,AFP_id=id_AFP,valor=valorCuota,fondo=f)
        db.session.add(cuota_a_guardar)
        cuota = True
        finde = True
    elif(dia_de_la_semana == 6 and closest_cuota.fecha < dia_antesdeayer):
        # Viernes
        cuota_a_guardar = Cuota(fecha=dia_antesdeayer,AFP_id=id_AFP,valor=valorCuota,fondo=f)
        db.session.add(cuota_a_guardar)
        cuota = True
        finde = True
    elif(dia_de_la_semana < 5):
        cuota_a_guardar = Cuota(fecha=fecha,AFP_id=id_AFP,valor=valorCuota,fondo=f) 
        db.session.add(cuota_a_guardar)
        cuota = True

    if cuota:
        try:
            db.session.commit()
            print(origen+": Guardado Cuota. "+str(cuota_a_guardar))
            if finde:
                print("Se guardó viernes desde el finde")

        except Exception as e:
            print(origen+": ERROR: "+str(e))
            db.session.rollback()

def scrapeSVS(browser):
    try:
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
        afps = AFP.query.all()
        print("Inicia SVS: ")

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
            dia_de_la_semana = fecha.weekday()
            dia_anterior = fecha - timedelta(days=1)
            dia_antesdeayer = fecha - timedelta(days=2)

            for afp in afps:
                closest_cuota = Cuota.query.filter(
                          and_(Cuota.AFP_id == afp.id, Cuota.fondo == f)).order_by(Cuota.fecha.desc()).first()

                closest_patrimonio = Patrimonio.query.filter(
                          and_(Patrimonio.AFP_id == afp.id, Patrimonio.fondo == f)).order_by(Patrimonio.fecha.desc()).first()

                if closest_cuota.fecha < fechaDisponible:
                    indice_cuota = (afp.id - 1) * 2

                    cuota = False
                    finde = False

                    try:
                        valorCuota = float(cuotas[indice_cuota].get_text().replace(".", "").replace(",", "."))
                    except ValueError:
                        print("Not a float")
                        continue

                    if(dia_de_la_semana == 5 and closest_cuota.fecha < dia_anterior):
                        # Viernes
                        cuota_a_guardar = Cuota(fecha=dia_anterior,AFP_id=afp.id,valor=valorCuota,fondo=f)
                        db.session.add(cuota_a_guardar)
                        cuota = True
                        finde = True
                    elif(dia_de_la_semana == 6 and closest_cuota.fecha < dia_antesdeayer):
                        # Viernes
                        cuota_a_guardar = Cuota(fecha=dia_antesdeayer,AFP_id=afp.id,valor=valorCuota,fondo=f)
                        db.session.add(cuota_a_guardar)
                        cuota = True
                        finde = True
                    elif(dia_de_la_semana < 5):
                        cuota_a_guardar = Cuota(fecha=fecha,AFP_id=afp.id,valor=valorCuota,fondo=f) 
                        db.session.add(cuota_a_guardar)
                        cuota = True


                    if cuota:
                        try:
                            db.session.commit()
                            print("Guardado Cuota: "+str(cuota_a_guardar))
                            if finde:
                                print("Se guardó viernes desde el finde")

                        except Exception as e:
                            print("Duplicado u otro error: "+str(e))
                            db.session.rollback()

                if closest_patrimonio.fecha < fechaDisponible:
                    indice_patrimonio = (afp.id * 2) - 1
                    
                    try:
                        valorPatrimonio = int(cuotas[indice_patrimonio].get_text().replace(".",""))
                    except ValueError:
                        print("Not a int")
                        continue

                    cuota = False
                    finde = False


                    if valorPatrimonio>0:
                        if(dia_de_la_semana == 5 and closest_patrimonio.fecha < dia_anterior):
                            # Viernes
                            patrimonio_a_guardar = Patrimonio(fecha=dia_anterior,AFP_id=afp.id,valor=valorPatrimonio, fondo=f)
                            db.session.add(patrimonio_a_guardar)
                            cuota = True
                            finde = True

                        elif(dia_de_la_semana == 6 and closest_patrimonio.fecha < dia_antesdeayer):
                            # Viernes
                            patrimonio_a_guardar = Patrimonio(fecha=dia_antesdeayer,AFP_id=afp.id,valor=valorPatrimonio, fondo=f)
                            db.session.add(patrimonio_a_guardar)
                            cuota = True
                            finde = True
                        elif(dia_de_la_semana < 5):
                            patrimonio_a_guardar = Patrimonio(fecha=fecha,AFP_id=afp.id,valor=valorPatrimonio, fondo=f)
                            db.session.add(patrimonio_a_guardar)
                            cuota = True

                        if cuota:
                            try:
                                db.session.commit()
                                print("Guardado Patrimonio: "+str(patrimonio_a_guardar))
                                if finde:
                                    print("Se guardó viernes desde el finde")

                            except Exception as e:
                                print("Duplicado u otro error: "+str(e))
                                continue
                # else:
                #     print("Esa fecha ya está: "+str(closest.fecha))

    except Exception as e:
        print("ERROR:"+str(e))

if __name__ == "__main__":
    print("------------------------------------------ Iniciando. Hora: "+str(datetime.now())+" -----------------------")
    browser = mechanicalsoup.StatefulBrowser(soup_config={'features': 'lxml'})
    scrapeCuprum(browser)
    scrapeProvida(browser)
    scrapeSVS(browser)

    print("------------------------------------------ Terminó: "+str(datetime.now())+" -----------------------")


