# car-data

```bash
docker run -v /config_on_host:/config_in_container -v /data_on_host:/data_in_container  <IMAGE_NAME> python read_car.py -c /config_in_container/config.json -f /data_in_container/f.json
```

