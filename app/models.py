from app import db
from sqlalchemy import UniqueConstraint

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)

    def __repr__(self):
        return '<Usuario %r>' % (self.nombre)

class AFP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(64), index=True, unique=True, nullable=False)
    cuotas = db.relationship('Cuota', backref='afp', lazy='dynamic')
    patrimonio = db.relationship('Patrimonio', backref='afp', lazy='dynamic')

    def __repr__(self):
        return '<AFP %r>' % (self.nombre)

class Cuota(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.Date, index=True, nullable=False)
    fondo = db.Column(db.String(1), index=True, nullable=False)
    AFP_id = db.Column(db.Integer, db.ForeignKey('AFP.id'))
    __table_args__ = (UniqueConstraint("fecha", "fondo","AFP_id"),)

    def __repr__(self):
        return '<Fondo %r. Valor: %r . AFP: %r. Fecha: %r>' % (self.fondo, self.valor, self.AFP_id, self.fecha)

class Patrimonio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.BigInteger,nullable=False)
    fecha = db.Column(db.Date, index=True,nullable=False)
    fondo = db.Column(db.String(1), index=True,nullable=False)
    AFP_id = db.Column(db.Integer, db.ForeignKey('AFP.id'),nullable=False)
    __table_args__ = (UniqueConstraint("fecha","fondo","AFP_id"),)

    def __repr__(self):
        return '<Patrimonio Valor: %r >' % (self.valor)



