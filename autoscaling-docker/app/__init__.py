from flask import Flask, jsonify
from flask_restful import Api
from flask_cors import CORS, cross_origin
from app.common.error_handling import ObjectNotFound, AppErrorBaseClass
from app.db import db
from app.autoscaling.api_v1_0.resources import autoscaling_v1_0_bp
from .ext import ma, migrate
from . import docker_init
import docker
from app.autoscaling.models import Component, Instance, ManagedContainer
import threading
import time
import requests

next_call = time.time()


def watch_alerts(ctx, muted_dict):
    global next_call

    data = requests.get(
        "http://localhost:9090/api/v1/alerts")
    alerts = data.json()['data']['alerts']
    print(alerts)
    with ctx:
        for alert in alerts:
            if alert['labels']['alertname'] not in muted_dict or muted_dict[alert['labels']['alertname']] != alert['activeAt']:
                name = alert['labels']['alertname']
                muted_dict[name] = alert['activeAt']
                data = requests.post("http://localhost:8181/v1/data/scaling/policy/course_of_action", json={
                    "input": {
                        "alert": name
                    }
                })
                jdata = data.json()
                print(jdata)
                action = jdata['result'][0]
                upscale = action.split(" ")[0] == "upscale"
                count = int(action.split(" ")[1])
                container_name = name.split("_")[1]
                for i in range(count):
                    if upscale:
                        upscale_component(container_name)
                    else:
                        downscale_component(container_name)
            else:
                print("alert muted")

    next_call = next_call+10
    threading.Timer(next_call - time.time(),
                    lambda: watch_alerts(ctx, muted_dict)).start()

def upscale_component(name):
    component = Component.simple_filter(container_name=name)[0]
    next_id = component.instances_next_id
    client = docker.from_env()
    new_instance = client.containers.run(component.image_name, detach=True, name=(
            "%s-%d" % (name, next_id)), network=("scaling-%s" % name))
    new_instance_mgd_container = ManagedContainer(new_instance.id)
    ManagedContainer.save(new_instance_mgd_container)
    component.instances.append(Instance(next_id, new_instance_mgd_container))
    component.instances_next_id += 1
    component.save()

def downscale_component(name):
    instances = Instance.get_all()
    if len(instances) > 1:
        client = docker.from_env()
        victim = instances[0]
        container = client.containers.get(victim.container.container_docker_id)
        container.stop()
        container.remove()
        Instance.delete(victim)

def create_app(settings_module):
    app = Flask(__name__)
    app.config.from_object(settings_module)
    CORS(app, origins="http://localhost:3000", allow_headers=[
        "Content-Type"])

    # Inicializa las extensiones
    db.init_app(app)

    with app.app_context():
        db.create_all()
        docker_init.init_app()
        watch_alerts(app.app_context(), {})

    ma.init_app(app)
    migrate.init_app(app, db)

    # Captura todos los errores 404
    Api(app, catch_all_404s=True)

    # Deshabilita el modo estricto de acabado de una URL con /
    app.url_map.strict_slashes = False

    # Registra los blueprints
    app.register_blueprint(autoscaling_v1_0_bp)

    # Registra manejadores de errores personalizados
    # register_error_handlers(app)

    return app


def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_exception_error(e):
        return jsonify({'msg': 'Internal server error'}), 500

    @app.errorhandler(405)
    def handle_405_error(e):
        return jsonify({'msg': 'Method not allowed'}), 405

    @app.errorhandler(403)
    def handle_403_error(e):
        return jsonify({'msg': 'Forbidden error'}), 403

    @app.errorhandler(404)
    def handle_404_error(e):
        return jsonify({'msg': 'Not Found error'}), 404

    @app.errorhandler(AppErrorBaseClass)
    def handle_app_base_error(e):
        return jsonify({'msg': str(e)}), 500

    @app.errorhandler(ObjectNotFound)
    def handle_object_not_found_error(e):
        return jsonify({'msg': str(e)}), 404
