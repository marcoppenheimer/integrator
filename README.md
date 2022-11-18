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
juju deploy kafka-k8s-bundle --channel edge
# ensure all applications are marked as `active|idle`
# if not, run `juju scale-application <APPLICATION> 4` to wake up the stalled app
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
  bootstrap-server: kafka-k8s-1.kafka-k8s-endpoints:9093,kafka-k8s-0.kafka-k8s-endpoints:9093,kafka-k8s-2.kafka-k8s-endpoints:9093
  consumer-group-prefix: relation-11-
  password: QxMg41nvfEtvcJkYqI51GVGCnwsf8nmQ
  topic: demo
  username: relation-11
  security-protocol: SASL_SSL
status: completed
```

### Running Producer
There are multiple ways to get a producer running locally. Currently the Kafka K8s charm can only resolve internal K8s DNS (i.e `pod.statefulset-endpoints:port`), so the `utils/client.py` script requires running in a container.

In order to successfully run `client.py`, you will need:

- Python3.8+
    - `requests`
    - `kafka-python`
- Valid `cert.pem` + `ca.pem`
    - These can be copied and pasted from any active `kafka-k8s` unit, found in `/data/kafka/config/server.pem` and `/data/kafka/config/ca.pem` respectively
- Directory structure as follows:
    - `/.`
        - `client.py`
        - `certs/`
            - `ca.pem`
            - `cert.pem`
- You can then run something similar to:
    - `python3 ./client.py -u relation-9 -p UJgTBKVPNcykvLrY8Np9wN09EKysNQ2d -x SASL_SSL -t demo --producer -s kafka-k8s-1.kafka-k8s-endpoints:9093,kafka-k8s-0.kafka-k8s-endpoints:9093,kafka-k8s-2.kafka-k8s-endpoints:9093`
