#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

"""Integrator charm for connecting to Kafka."""

import logging
from typing import Any, Dict, List, Union

from ops.charm import ActionEvent, CharmBase, RelationEvent
from ops.main import main
from ops.model import ActiveStatus

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
        self.framework.observe(self.on[REL_NAME].relation_changed, self._set_data)
        self.framework.observe(getattr(self.on, "get_data_action"), self._get_data)

    @property
    def relation(self):
        return self.model.get_relation(PEER)

    @property
    def kafka_relation(self):
        return self.model.get_relation(REL_NAME)

    def _set_data(self, event: RelationEvent) -> None:
        if (
            not self.unit.is_leader()
            or not event.relation
            or not event.relation.app
            or not self.relation
        ):
            event.defer()
            return

        logger.info("Setting relation data to Kafka...")
        username = event.relation.data[event.relation.app].get("username", "")
        password = event.relation.data[event.relation.app].get("password", "")
        bootstrap_server = event.relation.data[event.relation.app].get("uris", "")
        consumer_group_prefix = event.relation.data[event.relation.app].get(
            "consumer-group-prefix", ""
        )
        tls = event.relation.data[event.relation.app].get("tls", "")

        event.relation.data[self.app].update(
            {"extra-user-roles": "admin,consumer,producer", "topic": TOPIC}
        )

        self.relation.data[self.app].update(
            {
                "username": username,
                "password": password,
                "bootstrap-server": bootstrap_server,
                "consumer-group-prefix": consumer_group_prefix,
                "topic": TOPIC,
                "tls": tls,
            }
        )

        self.unit.status = ActiveStatus()

    def _get_data(self, event: ActionEvent) -> None:
        if not self.relation:
            event.fail("peer relation not set")
            return

        if not self.kafka_relation:
            event.fail("integrator not related to kafka")
            return

        topic = self.relation.data[self.app].get("topic", "")
        username = self.relation.data[self.app].get("username", "")
        password = self.relation.data[self.app].get("password", "")
        bootstrap_server = self.relation.data[self.app].get("bootstrap-server", "")
        consumer_group_prefix = self.relation.data[self.app].get(
            "consumer-group-prefix", ""
        )
        tls = bool(self.relation.data[self.app].get("tls", "").lower() == "enabled")

        if not topic:
            event.fail("Topic not found...")
            return
        if not username:
            event.fail("Username not found...")
            return
        if not password:
            event.fail("Password not found...")
            return
        if not bootstrap_server:
            event.fail("BootstrapServer not found...")
            return

        event.set_results(
            {
                "username": username,
                "password": password,
                "bootstrap-server": bootstrap_server,
                "consumer-group-prefix": consumer_group_prefix,
                "topic": TOPIC,
                "security-protocol": "SASL_SSL" if tls else "SASL_PLAINTEXT",
            }
        )
        return


if __name__ == "__main__":
    main(IntegratorCharm)
