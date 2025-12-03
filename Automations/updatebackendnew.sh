#!/bin/bash

INSTANCE_ID="i-04c4939726ad39578"

ipv4_address=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text)

file_to_find="../backend/.env.docker"

if [ ! -f "$file_to_find" ]; then
  echo "ERROR: $file_to_find not found."
  exit 1
fi

sed -i -e "s|FRONTEND_URL=.*|FRONTEND_URL=http://${ipv4_address}:3000|g" $file_to_find

echo "Updated backend FRONTEND_URL with: http://${ipv4_address}:3000"
