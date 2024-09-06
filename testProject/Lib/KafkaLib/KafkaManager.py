from testProject.Lib.KafkaLib.KafkaConnector import  push_on_kafka,push_on_kafka_with_key

class KafkaManager():    
    def push_csv_processing_data(self,body):
        push_on_kafka_with_key("topic-image-processing",body)   
    
