import argparse
import json
import logging
import time
from typing import List

import requests
from kafka import KafkaConsumer, KafkaProducer

logger = logging.getLogger(__name__)


class KafkaClient:
    def __init__(
        self,
        servers: List[str],
        username: str,
        password: str,
        topic: str,
        consumer_group_prefix: str,
    ) -> None:
        self.servers = servers
        self.username = username
        self.password = password
        self.topic = topic
        self.consumer_group_prefix = consumer_group_prefix

    def run_consumer(self):
        consumer = KafkaConsumer(
            self.topic,
            bootstrap_servers=self.servers,
            sasl_plain_username=self.username,
            sasl_plain_password=self.password,
            sasl_mechanism="SCRAM-SHA-512",
            group_id=self.consumer_group_prefix + "1",
            enable_auto_commit=True,
            auto_offset_reset="earliest",
            consumer_timeout_ms=15000,
        )

        for message in consumer:
            logger.info(message.decode("utf-8"))

    def run_producer(self) -> KafkaProducer:
        producer = KafkaProducer(
            bootstrap_servers=self.servers,
            sasl_plain_username=self.username,
            sasl_plain_password=self.password,
            sasl_mechanism="SCRAM-SHA-512",
            ssl_check_hostname=False,
        )

        while True:
            logger.info("Requesting NewStories from HN...")
            response = requests.get(
                url="https://hacker-news.firebaseio.com/v0/newstories.json?print=pretty"
            )
            content = (
                json.loads(response._content.decode("utf-8"))
                if response._content
                else {}
            )

            if content:
                logger.info("Successfully retrieved NewStories...")
            else:
                logger.warning("Failed retrieving NewStories...")
                time.sleep(5)

            for content_id in content:
                response = requests.get(
                    url=f"https://hacker-news.firebaseio.com/v0/item/{content_id}.json"
                )
                item_content = response._content or b""
                item_id = json.loads(item_content.decode("utf-8")).get("id", None)
                title = json.loads(item_content.decode("utf-8")).get("title", None)
                url = json.loads(item_content.decode("utf-8")).get("url", None)

                if item_id:
                    future = producer.send(self.topic, item_content)
                    future.get(timeout=60)
                    logger.info(
                        f"Message published to topic={self.topic}, item_id={item_id}, title={title}, url={url}"
                    )
                else:
                    logger.warning(f"Missing item_id for content_id={content_id}")

                time.sleep(5)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Handler for running a Kafka client")
    parser.add_argument(
        "-t", "--topic", help="Kafka topic provided by Kafka Charm", type=str
    )
    parser.add_argument(
        "-u", "--username", help="Kafka username provided by Kafka Charm", type=str
    )
    parser.add_argument(
        "-p", "--password", help="Kafka password provided by Kafka Charm", type=float
    )
    parser.add_argument(
        "-c",
        "--consumer-group-prefix",
        help="Kafka consumer-group-prefix provided by Kafka Charm",
        type=str,
    )
    parser.add_argument(
        "-s",
        "--servers",
        help="comma delimited list of Kafka bootstrap-server strings",
        type=str,
    )
    parser.add_argument("--producer", action="store_true", default=False)
    parser.add_argument("--consumer", action="store_true", default=False)

    args = parser.parse_args()

    servers = args.servers.split(",")

    client = KafkaClient(
        servers=servers,
        username=args.username,
        password=args.password,
        topic=args.topic,
        consumer_group_prefix=args.consumer_group_prefix,
    )

    # producer = client.run_producer()
    # consumer = client.run_consumer()
