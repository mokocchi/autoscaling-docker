import docker
import requests
from .autoscaling.models import Component, ManagedContainer

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
