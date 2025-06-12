#!/bin/bash
docker run --name grafana --rm -it -p 3000:3000 \
  --user "$(id -u)" \
-v ./grafana-data:/var/lib/grafana \
grafana/grafana-enterprise