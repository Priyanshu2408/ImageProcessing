import json
from customers_orders.settings import KAFKA_BOOTSTRAP_SERVER
from kafka import KafkaConsumer
from customers_orders.ThirdParty.CrFileLogger import CrFileLogger as CnFileLogger
import traceback
from customers_orders.Lib.KafkaLib.KafkaConfig import KafkaProducerSingleton
kafka_producer = KafkaProducerSingleton()
import time

def push_on_kafka(topic,body):
    st=time.time()
    producer=kafka_producer.get_instance()
    try:
        producer.produce_message(topic,body)
        #print("time taken prodcing ",time.time()-st)
    except Exception as e:
        tb =traceback.format_exc()
        CnFileLogger.log('kafka_producer_logs','topic: {topic}, body: {body}, except {e}'.format(topic=str(topic), body = str(body), e = str(tb)))

def push_on_kafka_with_key(topic,body,key):
    st=time.time()
    producer = kafka_producer.get_instance()
    key = str(key)
    try:
        producer.produce_message(topic, body,key)
        #print("time taken prodcing ",time.time()-st)
    except Exception as e:
        tb = traceback.format_exc()
        #print(tb)
        CnFileLogger.log('kafka_producer_logs','topic: {topic}, body: {body}, except {e}'.format(topic=str(topic), body = str(body), e = str(tb)))
    
def get_kafka_consumer(topic,group_id,server=KAFKA_BOOTSTRAP_SERVER,auto_commit=False,max_poll_records=500,max_poll_interval=300000):
    """
    function to get consumer Kafka
    """
    consumer = KafkaConsumer(topic,bootstrap_servers=server,group_id=group_id,value_deserializer = lambda v: json.loads(v.decode('utf-8')),enable_auto_commit= auto_commit,auto_offset_reset="latest",max_poll_records=max_poll_records,max_poll_interval_ms=max_poll_interval)
    return consumer
