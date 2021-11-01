from sqlalchemy.orm import backref
from app.db import db, BaseModelMixin


class Component(db.Model, BaseModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String)
    container_name = db.Column(db.String)
    port_number = db.Column(db.Integer)
    instances_next_id = db.Column(db.Integer)
    instances = db.relationship('Instance', backref='component', lazy=False, cascade='all, delete-orphan')

    def __init__(self, image_name, container_name, port_number, instances=[]):
        self.image_name = image_name
        self.container_name = container_name
        self.port_number = port_number
        self.instances = instances
        self.instances_next_id = 1

    def __repr__(self):
        return f'Component({self.container_name})'

    def __str__(self):
        return f'{self.container_name}'


class Instance(db.Model, BaseModelMixin):
    id = db.Column(db.Integer, primary_key=True)
    instance_number = db.Column(db.Integer)
    component_id = db.Column(db.Integer, db.ForeignKey('component.id'), nullable=False)
    container_id = db.Column(db.Integer, db.ForeignKey('managedcontainer.id'))
    container = db.relationship('ManagedContainer', single_parent=True, backref=backref("instance"), uselist=False, cascade='all, delete-orphan')

    def __init__(self, instance_number, container):
        self.instance_number = instance_number
        self.container = container

    def __repr__(self):
        return f'Instance({self.component_id}-{self.instance_number})'

    def __str__(self):
        return f'{self.component_id}-{self.instance_number}'

class ManagedContainer(db.Model, BaseModelMixin):
    __tablename__ = 'managedcontainer'
    id = db.Column(db.Integer, primary_key=True)
    container_docker_id = db.Column(db.String)

    def __init__(self, container_docker_id):
        self.container_docker_id = container_docker_id

    def __repr__(self):
        return f'Container({self.container_docker_id})'

    def __str__(self):
        return f'{self.container_docker_id}'