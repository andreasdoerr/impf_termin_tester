import paho.mqtt.client as mqtt

from impf_termin_tester.notifiers import NotificationService


class MQTTNotification(NotificationService):
    def __init__(self, broker):
        super().__init__(name="MQTT client")
        self.mqtt_client = mqtt.Client()
        self.mqtt_topic = "impf_termin"
        self.mqtt_broker = broker

    def initialize(self):
        self.mqtt_client.connect(
            self.mqtt_broker, port=1883, keepalive=60, bind_address=""
        )

    def _send_notification(self, result):
        mqtt_payload = "Appointment available: " + result.url
        ret = self.mqtt_client.publish(
            self.mqtt_topic, mqtt_payload, qos=0, retain=False
        )
        return True
