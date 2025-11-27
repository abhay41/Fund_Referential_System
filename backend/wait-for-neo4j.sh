#!/bin/bash
set -e

host="$1"
port="$2"
shift 2
cmd="$@"

echo "Waiting for Neo4j at $host:$port to be ready..."

until nc -z $host $port; do
  echo "Neo4j is unavailable - sleeping"
  sleep 5
done

echo "Neo4j is up and running! Executing command."
exec $cmd
