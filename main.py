from datetime import datetime, timezone

import requests
import yaml
from paho.mqtt.client import Client
from twisted.internet import reactor, task


def load_config(config_file):
    with open(config_file, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


def request_api(arg):
    url_api = arg[0]
    mqtt_client = arg[1]

    request = requests.get(url_api)
    request_json = request.json()

    if request.status_code == 200:
        location = request_json['name']
        temperature = request_json['main']["temp"]
        print('Localisation : %s\n' % location)
        print('Température : %s\n' % temperature)

        json_body = {
            "city": location,
            "source": "web",
            "time": datetime.now(timezone.utc).astimezone().isoformat(),
            "value": temperature
        }
        mqtt_client.publish("temperature", str(json_body))
    else:
        print('Erreur dans l\'accès à l\'API : ', request.status_code)


config = load_config("config.yaml")
owm = config['owm']
mqtt = config['mqtt']
interval = config['interval']

urlAPI = "http://api.openweathermap.org/data/2.5/weather?id=%s&units=%s&APPID=%s" % (
    owm['city_id'], owm['units'], owm['key'])

mqtt_client = Client(mqtt['client_id'])
mqtt_client.username_pw_set(mqtt['username'], mqtt['password'])
mqtt_client.connect(mqtt['host'], mqtt['port'], mqtt['keep_alive'])

if __name__ == '__main__':
    loop = task.LoopingCall(request_api, (urlAPI, mqtt_client))
    loop.start(interval)
    reactor.run()
