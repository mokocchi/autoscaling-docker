from logging import DEBUG
import re
import yaml
import requests
import json
from flask import Flask, request, jsonify
from flask_cors import CORS


def add_target(target):
    f = open("/etc/prometheus/prometheus.yml", "r")
    file_yaml = yaml.load(f, Loader=yaml.FullLoader)
    f.close()

    file_yaml["scrape_configs"].append({
        "job_name": ("nginx_vts_exporter-%s" % target),
        "metrics_path": "/status",
        "static_configs": [
            {"targets": [
                ("scaling-nginx-%s" % target)
            ]}
        ]
    })

    f = open("/etc/prometheus/prometheus.yml", "w")
    yaml.dump(file_yaml, f)
    f.close()

    f2 = open("/etc/prometheus/alert.rules.yml", "r")

    file_yaml2 = yaml.load(f2, Loader=yaml.FullLoader)

    f2.close()

    file_yaml2["groups"].append({
      "name": ("scaling-nginx-%s" % target),
      "rules": []
    })

    f2 = open("/etc/prometheus/alert.rules.yml", "w")
    yaml.dump(file_yaml2, f2)
    f2.close()


def find(lst, key, value):
    for i, dic in enumerate(lst):
        if dic[key] == value:
            return i
    return -1


def add_rule(rule_def):
    f = open("/etc/prometheus/alert.rules.yml", "r")
    file_yaml = yaml.load(f, Loader=yaml.FullLoader)
    f.close()

    rule = {
        "alert": ("%s_%s" % (rule_def['name'], rule_def['target'])),
        "expr": rule_def["expr"],
        "labels": {
            "severity": "warning"
        }
    }

    print(json.dumps(file_yaml))
    
    for group in file_yaml["groups"]:
        if(group["name"] == "scaling-nginx-%s" % rule_def["target"]):
            group["rules"].append(rule)

    f = open("/etc/prometheus/alert.rules.yml", "w")
    yaml.dump(file_yaml, f)
    f.close()


def remove_target(target):
    f = open("/etc/prometheus/prometheus.yml", "r")
    file_yaml = yaml.load(f, Loader=yaml.FullLoader)
    f.close()

    idx = find(file_yaml["scrape_configs"], "job_name",
               ("nginx_vts_exporter-%s" % target))

    if idx != -1:
        del file_yaml["scrape_configs"][idx]

    f = open("/etc/prometheus/prometheus.yml", "w")
    yaml.dump(file_yaml, f)
    f.close()


def fetch_rules():
    f = open("/etc/prometheus/alert.rules.yml", "r")
    rules_file = yaml.load(f, Loader=yaml.FullLoader)
    f.close()

    return jsonify(rules_file['groups'])


app = Flask(__name__)
CORS(app, allow_headers=["Content-Type"])


@app.route('/add-target', methods=['POST'])
def post_add_target():
    form_json = request.get_json()
    target = form_json['target']
    try:
        add_target(sanitize_server(target))
        return 'OK'
    except:
        return 'NG'


@app.route('/add-rule', methods=['POST'])
def post_add_rule():
    form_json = request.get_json()
    target = form_json['target']
    try:
        target = sanitize_server(target)
        rule = {}
        rule['name'] = form_json['name']
        rule['expr'] = form_json['expr']
        rule['target'] = target
        add_rule(rule)
        return 'OK'
    except:
        return 'NG'


@app.route('/remove-target', methods=['POST'])
def post_remove_target():
    form_json = request.get_json()
    target = form_json['target']
    try:
        (sanitize_server(target))
        return 'OK'
    except:
        return 'NG'


@app.route('/reload', methods=['POST'])
def reload():
    requests.post('http://localhost:9090/-/reload')
    return 'OK'


@app.route('/rules', methods=['GET'])
def get_rules():
    return fetch_rules()


def sanitize_server(target):
    if re.match("^[a-zA-Z]([a-zA-Z0-9\-])*?$", target):
        return target
    else:
        raise Exception('invalid target')
