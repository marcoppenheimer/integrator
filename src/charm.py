#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""Integrator charm for connecting to Kafka."""

import logging
from typing import Any, Dict, List, Union

from ops.charm import ActionEvent, CharmBase, RelationEvent
from ops.main import main

logger = logging.getLogger(__name__)


CHARM_KEY = "integrator"
PEER = "cluster"
REL_NAME = "kafka-client"
TOPIC = "demo"

JSONType = Union[Dict[str, Any], List[Any]]


class IntegratorCharm(CharmBase):
    """Application charm that produces to Kafka charm."""

    def __init__(self, *args):
        super().__init__(*args)
        self.name = CHARM_KEY

        self.framework.observe(self.on[REL_NAME].relation_created, self._set_data)
        self.framework.observe(getattr(self.on, "get_topic_action"), self._get_topic)
        self.framework.observe(
            getattr(self.on, "get_bootstrap_server_action"), self._get_bootstrap_server
        )

    @property
    def relation(self):
        return self.model.get_relation(PEER)

    @property
    def kafka_relation(self):
        return self.model.get_relation(REL_NAME)

    def _set_data(self, event: RelationEvent) -> None:
        if not self.unit.is_leader() or not event.relation:
            event.defer()
            return

        logger.info("Setting relation data to Kafka...")
        event.relation.data[self.app].update(
            {"extra-user-roles": "admin,consumer,producer", "topic": TOPIC}
        )

    def _get_topic(self, event: ActionEvent) -> None:
        if not self.kafka_relation:
            event.fail("integrator not related to kafka")
            return

        topic = self.kafka_relation.data[self.app].get("topic", "")

        if not topic:
            event.fail("Topic not found...")
            return

        event.log("Topic found...")
        event.set_results({"topic": topic})
        return

    def _get_bootstrap_server(self, event: ActionEvent) -> None:
        if not self.kafka_relation or not self.kafka_relation.app:
            event.fail("integrator not related to kafka")
            return

        bootstrap_server = self.kafka_relation.data[self.kafka_relation.app].get(
            "uris", ""
        )

        if not bootstrap_server:
            event.fail("Bootstrap-Server not found...")
            return

        event.log("Bootstrap-Server found...")
        event.set_results({"bootstrap-server": bootstrap_server})
        return

    def _get_username(self, event: ActionEvent) -> None:
        if not self.kafka_relation or not self.kafka_relation.app:
            event.fail("integrator not related to kafka")
            return

        username = self.kafka_relation.data[self.kafka_relation.app].get("username", "")

        if not username:
            event.fail("Username not found...")
            return

        event.log("Username found...")
        event.set_results({"username": username})
        return

    def _get_password(self, event: ActionEvent) -> None:
        if not self.kafka_relation or not self.kafka_relation.app:
            event.fail("integrator not related to kafka")
            return

        password = self.kafka_relation.data[self.kafka_relation.app].get("password", "")

        if not password:
            event.fail("Password not found...")
            return

        event.log("Password found...")
        event.set_results({"password": password})
        return


if __name__ == "__main__":
    main(IntegratorCharm)
