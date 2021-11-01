import re
import os
from flask import Flask, request

def update_ips(server_list):
  f = open("/etc/nginx/conf.d/default.conf", "r")
  old = f.read()
  f.close()

  new_servers = ""
  for serv in server_list:
    new_servers = format("%s    server %s;\n" % (new_servers, serv))
  new = re.sub('#servers-begin.*?#servers-end', format('#servers-begin\n%s    #servers-end' % new_servers), old,
      flags=re.DOTALL)

  f = open("/etc/nginx/conf.d/default.conf", "w")
  f.write(new)
  f.close()
  os.system("nginx -s reload")


app = Flask(__name__)

# TODO: agregar autenticación para el endpoint
@app.route('/updated-ips', methods=['POST'])
def index():
  server_str = request.form['servers']
  server_list = server_str.split(",")
  update_ips(sanitize_servers(server_list))
  return 'OK'

def sanitize_servers(str_list):
  result = []
  for str in str_list:
    if re.match("^[a-zA-Z]([a-zA-Z0-9\-])*(:[0-9]{1,4})?$", str):
      result.append(str)
  return result

def valid_char(char):
  return (char.isalnum() | (["-", ":"].count(char) == 1))