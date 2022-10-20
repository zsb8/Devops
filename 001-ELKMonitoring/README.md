# Project Name: ELK Monitoring
This instruction shows how I setup a ELK (Elasticsearch/Logstash/Kibana) stack to monitor a server.

# Project Goal
Learn how to deploy a ELK with docker-compose, as well as configuring metricbeat service to collect the system metric from a server and present them in Kibana.

# Learning Resources
https://www.elastic.co/training/free

# Prerequisites
- Ubuntu 20.04 OS     
- [Docker](https://docs.docker.com/engine/install/ubuntu/)      
- [Docker Compose](https://docs.docker.com/compose/install/)      

# Project Steps
## 1. Deploy a ELK stack
Clone the github repo and run the docker compose to start up the ELK stack
```
git clone https://github.com/zsb8/Devops.git
cd devops/001-ELKMonitoring
sudo sysctl -w vm.max_map_count=262144
sudo docker-compose up -d
```

## 2. Add Elasticsearch CA certificates     
As the communication between Elasticsearch and metricbeat is using tls, you need to add the Elasticsearch CA into the server which is going to be monitored.

a. Copy the CA certificate from one of Elasticsearch containers
First, you run `docker ps` to find the CONTAINER ID of the elasticsearch, then past in this command.     
![image](https://user-images.githubusercontent.com/75282285/197023313-a16995b4-eaf0-446e-8ca2-86263145f8b1.png)      
If it is 3d6b1762e254, then write such as:    
```
docker exec -it 3d6b1762e254 openssl x509 -fingerprint -sha256 -in /usr/share/elasticsearch/config/certs/ca/ca.crt
```
You will see the CA certificate content.
![image](https://user-images.githubusercontent.com/75282285/197024320-97ababa7-2227-4360-bf45-78b8ad4e0db2.png)


b.  Go to the host which you want to monitor and run below command:       
We will place the Elasticsearch's public certification to the trust host's ca folder, then this host can communicate with Elasticsearch server by TLS.
```
sudo apt-get install -y ca-certificates
cd /usr/local/share/ca-certificates/
sudo vi elasticsearch-ca.crt
# Paste the CA certificate you copied in above step and then run below command to add it to the host
sudo update-ca-certificates
```

## 3. Deploy metricbeat service 
Deploy a metricbeat service in the monitored server to collect the metric data.
> Note: In this example, we are monitoring the local host. For other hosts, you just need to update the ELK host IP address in the `metricbeat.yaml` to make sure the metricbeat can reach the Elasticsearch.
```
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-7.x.list
sudo apt update
sudo apt install metricbeat
sudo vim /etc/metricbeat/metricbeat.yml
# Note: Make sure below section is updated in `metricbeat.yml`
setup.kibana:
  host: "127.0.0.1:5601"
output.elasticsearch:
  hosts: ["127.0.0.1:9200"]
  protocol: "https"
  username: "elastic"
  password: "changeme"

sudo metricbeat setup -e
sudo systemctl start metricbeat
sudo systemctl status metricbeat
```


## 4. Go to Kibana. In Dashboard, select "[Metricbeat System] Host overview ECS"

a. Open your browser and go to [http://0.0.0.0:5601/](http://0.0.0.0:5601/) (if the metricbeat is installed in your local host). Enter the username/passwors set in `docker-compose.yaml`.

b. Click the menu icon in the top left and go to "Dashboard"

c. Select "[Metricbeat System] Host overview ECS" and you should be able to see all metric data from your local host presented in the dashboard.
![image](https://user-images.githubusercontent.com/75282285/197031785-4bf9962e-dbcb-4f31-b1ab-927c6afff948.png)

# Reference
https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html

https://kifarunix.com/monitor-linux-system-metrics-with-elk-stack/

https://logging.dev.pilot.indocresearch.org/app/home#/tutorial/nginxLogs

https://github.com/elastic/beats/issues/29175
