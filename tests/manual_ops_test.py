from agentops_investigator.clients.ops_client import OpsClient


client = OpsClient()

print("SERVICES")
print(client.list_services())

print()

print("ORDER HEALTH")
print(client.get_health("order-service"))

print()

print("ORDER METRICS")
print(client.get_metrics("order-service"))