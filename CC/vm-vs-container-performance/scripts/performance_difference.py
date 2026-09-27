vm_throughput = 608.0550
container_throughput = 624.9875

difference = (
    (container_throughput - vm_throughput)
    / vm_throughput
) * 100

print(
    f"Throughput difference: {difference:.2f}%"
)
