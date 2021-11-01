from flask import request, Blueprint, make_response
from flask.json import jsonify
from flask_restful import Api, Resource
import docker
import requests

from .schemas import ComponentSchema
from ..models import Component, Instance, ManagedContainer

autoscaling_v1_0_bp = Blueprint('autoscaling_v1_0_bp', __name__)

component_schema = ComponentSchema()

api = Api(autoscaling_v1_0_bp)


class ComponentListResource(Resource):
    def get(self):
        components = Component.get_all()
        result = component_schema.dump(components, many=True)
        return result

    def post(self):
        data = request.get_json()
        # TODO: validate data
        component_dict = component_schema.load(data)
        dict_image = component_dict['image_name']
        dict_container = component_dict['container_name']
        dict_port = component_dict['port_number']

        client = docker.from_env()
        image_found = False
        for image in client.images.list():
            if(len(image.tags) == 0):
                continue
            if image.tags[0].split(":")[0] == dict_image:
                image_found = True
                break
        if not image_found:
            return make_response(jsonify({'msg': 'Image not found'}), 400)
        images = Component.simple_filter(image_name=dict_image)
        if len(images) > 0:
            return jsonify({'msg': "Component already exists"}), 400
        networks = client.networks.list()
        found = False
        for net in networks:
            if net.name == ("scaling-%s" % dict_container):
                found = True
                break
        if not found:
            client.networks.create(("scaling-%s" % dict_container))

        first_instance = client.containers.run(dict_image, detach=True, name=(
            "%s-0" % dict_container), network=("scaling-%s" % dict_container))
        first_instance_mgd_container = ManagedContainer(first_instance.id)
        ManagedContainer.save(first_instance_mgd_container)

        proxy = client.containers.run("scaling-nginx", detach=True, name=("scaling-nginx-%s" % dict_container), network=(
            "scaling-%s" % dict_container), ports={"80/tcp": dict_port}, environment=["start_server=%s-0:%d" % (dict_container, dict_port)])
        client.networks.get("scaling").connect(proxy)
        proxy_mgd_container = ManagedContainer(proxy.id)
        ManagedContainer.save(proxy_mgd_container)

        component = Component(image_name=component_dict['image_name'],
                              container_name=component_dict['container_name'],
                              port_number=component_dict['port_number'],
                              )
        component.instances.append(Instance(0, first_instance_mgd_container))
        component.save()
        resp = component_schema.dump(component)
        return resp, 201


class ComponentResource(Resource):
    def get(self, component_id):
        component = Component.get_by_id(component_id)
        if component is None:
            raise ObjectNotFound('Component does not exist')
        resp = component_schema.dump(component)
        return jsonify({'msg': 'Shutting down...'}), 404

class ShutDownResource(Resource):
    def get(self):
        client = docker.from_env()
        mgd_containers = ManagedContainer.get_all()  
        for mgd_container in mgd_containers:   
            container = client.containers.get(mgd_container.container_docker_id)
            container.stop()
            container.remove()
            ManagedContainer.delete(mgd_container)
            components = Component.get_all()
            for component in components: Component.delete(component)
        return 

def init_app():
  client = docker.from_env()
  recreate_scaling_network(client)
  delete_scaling_containers(client)
  run_prometheus(client)
  run_open_policy_agent(client)
  initialize_open_policy_agent()


def recreate_scaling_network(client):
  networks = client.networks.list()
  found = False
  for net in networks:
    if net.name == "scaling":
      found = True
      break
  if not found: client.networks.create("scaling")


def delete_scaling_containers(client):
  mgd_containers = ManagedContainer.get_all()
  for mgd_container in mgd_containers:
    container = client.containers.get(mgd_container.container_docker_id)
    container.stop()
    container.remove()
    ManagedContainer.delete(mgd_container)
    components = Component.get_all()
    for component in components: Component.delete(component)


def run_prometheus(client):
  prometheus = client.containers.run("scaling-prometheus", ports={
                                     "9090/tcp": 9090, "3031/tcp": 5000}, network="scaling", detach=True, name="scaling-prometheus")
  prometheus_mgd_container = ManagedContainer(prometheus.id)
  ManagedContainer.save(prometheus_mgd_container)


def run_open_policy_agent(client):
  opa = client.containers.run("openpolicyagent/opa", network="scaling", detach=True, name="scaling-opa", command=["run", "--server"])
  opa_mgd_container = ManagedContainer(opa.id)
  ManagedContainer.save(opa_mgd_container)

  opa_nginx = client.containers.run("scaling-opa-nginx", network="scaling", detach=True, name="scaling-opa-nginx", ports={
                              "80/tcp": 8181})
  opa_nginx_mgd_container = ManagedContainer(opa_nginx.id)
  ManagedContainer.save(opa_nginx_mgd_container)


def initialize_open_policy_agent():
  requests.put("http://localhost:8181/v1/data/scaling/alerts", data="{}")
  requests.put("http://localhost:8181/v1/policies/scaling", data="""
  package scaling.policy

  import data.scaling.alerts
  import input

  course_of_action[action] {
      action:= alerts[input.alert]
  }
  """)
class RestartResource(Resource):
    def get(self):
        init_app()

api.add_resource(ComponentListResource, '/api/v1.0/components/',
                 endpoint='component_list_resource')
api.add_resource(ComponentResource, '/api/v1.0/components/<int:component_id>',
                 endpoint='component_resource')
api.add_resource(ShutDownResource, '/api/v1.0/shutdown/',
                 endpoint='shutdown_resource')
api.add_resource(RestartResource, '/api/v1.0/restart/',
                 endpoint='restart_resource')