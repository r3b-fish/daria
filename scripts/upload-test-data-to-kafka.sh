#!/usr/bin/env bash

docker exec agent-kafka bash -c "kafka-console-producer.sh --broker-list localhost:9092 --topic test_csv < /home/test.csv"
docker exec agent-kafka bash -c "kafka-console-producer.sh --broker-list localhost:9092 --topic test_kfk < /home/test_json_items_for_kafka"
docker exec agent-kafka bash -c "kafka-console-producer.sh --broker-list localhost:9092 --compression-codec zstd --topic test_running_counters < /home/test_running_counter.txt"
docker exec agent-kafka bash -c "kafka-console-producer.sh --broker-list localhost:9092 --compression-codec zstd --topic test_json_arrays < /home/test_with_arrays.json"
