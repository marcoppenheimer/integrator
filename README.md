## Kafka Integrator Charm

### Installation

Ensure you have MicroK8s set up correctly:

```bash
sudo snap install microk8s --classic
microk8s enable dns hostpath-storage
```

Ensure you have Juju set up correctly, and bootstrap MicroK8s:

```bash
sudo snap install juju --classic
juju bootstrap microk8s k8s

# after setup is complete

juju add-model dev
```

Ensure you have Charmcraft installed correctly:

```bash
sudo snap install charmcraft --classic --channel=edge
charmcraft login
```

### Set-Up

Ensure you have KafkaK8s and ZooKeeperK8s charms installed:

```bash
juju deploy zookeeper-k8s --channel edge --revision 16 -n 3
juju deploy kafka-k8s --channel edge --revision 13 -n 3

# after both applications mark as `waiting`|`active` and `idle` 

juju relate zookeeper-k8s kafka-k8s
```

Ensure you have built and deployed a local integrator charm:

```
cd /tmp
git clone git@github.com:marcoppenheimer/integrator.git
cd integrator
charmcraft pack
juju deploy ./*.charm -n 1

# after deployed

juju relate kafka-k8s integrator
```

### Getting data

```bash
juju run-action integrator/0 get-data

# keep the number returned, e.g Action queued with id: "2"
# In this case, 2

juju show-action-output 2
```

### Output

```bash
UnitId: integrator/0
id: "14"
results:
  bootstrap-server: kafka-k8s-1.kafka-k8s-endpoints:9092,kafka-k8s-0.kafka-k8s-endpoints:9092,kafka-k8s-2.kafka-k8s-endpoints:9092
  consumer-group-prefix: relation-11-
  password: QxMg41nvfEtvcJkYqI51GVGCnwsf8nmQ
  topic: demo
  username: relation-11
status: completed
```

