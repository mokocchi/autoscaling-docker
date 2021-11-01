from marshmallow import fields
from app.ext import ma
class ComponentSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    image_name = fields.String()
    container_name = fields.String()
    port_number = fields.Integer()
    instances_next_id = fields.Integer()
    instances = fields.Nested('InstanceSchema', many=True)
class InstanceSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    instance_number = fields.Integer()
    container = fields.Nested('ManagedContainerSchema')

class ManagedContainerSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    container_docker_id = fields.String()