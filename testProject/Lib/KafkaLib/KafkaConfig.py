from kafka import KafkaProducer
from customers_orders.settings import KAFKA_BOOTSTRAP_SERVER
import json

class KafkaProducerSingleton:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None or cls._instance.producer._closed:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        bootstrap_servers = KAFKA_BOOTSTRAP_SERVER 
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers
        )

    def produce_message(self, topic, body,key = 0):
        if key:
            key_bytes = key.encode('utf-8') if isinstance(key, str) else key
            value_bytes = bytes(json.dumps(body),encoding='utf-8')
            self.producer.send(topic, value=value_bytes,key=key_bytes)
        else:    
            value_bytes = bytes(json.dumps(body),encoding='utf-8')
            self.producer.send(topic, value=value_bytes)    
        self.producer.flush()