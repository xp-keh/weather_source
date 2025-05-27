import json
import time
import requests
import logging
import os
from datetime import datetime
from config.logging import Logger
from kafka import KafkaProducer
from kafka.errors import KafkaError
from config.utils import get_env_value

logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger(__name__)

class Producer:
    def __init__(self, kafka_broker: str, kafka_topic: str) -> None:
        self._kafka_server = kafka_broker
        self._kafka_topic = kafka_topic
        self._instance = None
        self.logger = Logger().setup_logger(service_name='producer')
    

    def create_instance(self) -> KafkaProducer: 
        self.logger.info(" [*] Starting Kafka producer...")
        self._instance = KafkaProducer(
            bootstrap_servers=self._kafka_server,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            api_version=(0,11,5)
        )  # type: ignore
        return self._instance

    def is_kafka_connected(self) -> bool:
        try:
            metadata = self._instance.bootstrap_connected() # type: ignore
            if metadata:
                self.logger.info(" [*] Connected to Kafka cluster successfully!")
                return True
            else:
                self.logger.error(" [X] Failed to connect to Kafka cluster.")
                return False
        except KafkaError as e:
            self.logger.error(f" [X] Kafka connection error: {e}")
            return False
        
    def ensure_bytes(self, message) -> bytes:
        if not isinstance(message, bytes):
            return bytes(message, encoding='utf-8')
        return message
    
def produce(self) -> None:
    try:
        self.logger.info(" [*] Starting real-time Kafka producer.")
        api_key = get_env_value('OPENWEATHER_API_KEY')

        locations = {
            "TNTI": ("0.7718", "127.3667"),
            "PMBI": ("-2.9024", "104.6993"),
            "BKB": ("-1.1073", "116.9048"),
            "SOEI": ("-9.7553", "124.2672"),
            "MMRI": ("-8.6357", "122.2376"),
        }

        while True:
            for location, coords in locations.items():
                lat, lon = coords

                url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"

                try:
                    response = requests.get(url, timeout=5)
                    response.raise_for_status()
                    response_json = response.json()

                    response_json["location"] = location
                    response_json["raw_produce_dt"] = int(datetime.now().timestamp() * 1_000_000)
                    response_json["lat"] = lat
                    response_json["lon"] = lon

                    self._instance.send(self._kafka_topic, value=response_json)  # type: ignore

                    self.logger.info(f"Data sent to Kafka topic: {response_json}")

                except requests.exceptions.RequestException as e:
                    logger.error(f"Error fetching weather data for {location}: {e}")
                    continue

            time.sleep(1)

    except Exception as e:
        pass
        self.logger.error(f" Error in Kafka: {e}")
        self.logger.info(" [*] Stopping data generation.")
        os._exit(1)
    finally:
        self._instance.close()  # type: ignore