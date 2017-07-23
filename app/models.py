from app import db

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)

    def __repr__(self):
        return '<Usuario %r>' % (self.nombre)

class AFP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(64), index=True, unique=True)
    cuotas = db.relationship('Cuota', backref='afp', lazy='dynamic')


    def __repr__(self):
        return '<AFP %r>' % (self.nombre)

class Cuota(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Float)
    fecha = db.Column(db.Date)
    fondo = db.Column(db.String(1))
    AFP_id = db.Column(db.Integer, db.ForeignKey('AFP.id'))
    def __repr__(self):
        return '<Fondo %r. Valor: %r >' % (self.nombre, self.valor)


