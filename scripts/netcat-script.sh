RESPONSE=$(echo "Testing Message" | nc "server:12345")
echo "$RESPONSE"
