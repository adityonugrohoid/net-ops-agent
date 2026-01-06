import time
import random
from typing import Dict, Any

def get_service_health(service_name: str) -> Dict[str, Any]:
    """
    Retrieves the current health status and resource usage of a specific service.

    Args:
        service_name (str): The unique identifier or name of the service to check.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - 'service': The name of the service.
            - 'status': One of 'Running', 'Failed', 'Degraded'.
            - 'cpu_usage_percent': Simulated CPU usage (0-100).
            - 'memory_usage_mb': Simulated memory usage in MB.
    """
    statuses = ["Running", "Failed", "Degraded"]
    status = random.choice(statuses)
    
    # Simulate API latency
    time.sleep(0.5) 
    
    return {
        "service": service_name,
        "status": status,
        "cpu_usage_percent": round(random.uniform(5.0, 95.0), 2),
        "memory_usage_mb": random.randint(128, 4096)
    }

def restart_service(service_name: str, force: bool = False) -> Dict[str, Any]:
    """
    Initiates a restart sequence for a specified service.

    Args:
        service_name (str): The unique identifier or name of the service to restart.
        force (bool): If True, performs a hard restart (kill and start). 
                      If False, attempts a graceful restart. Defaults to False.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - 'service': The name of the service.
            - 'action': 'restart'.
            - 'mode': 'force' or 'graceful'.
            - 'status': 'Success'.
            - 'timestamp': Simulated timestamp of completion.
    """
    # Simulate restart duration
    duration = 2.0 if force else 1.0
    time.sleep(duration)
    
    return {
        "service": service_name,
        "action": "restart",
        "mode": "force" if force else "graceful",
        "status": "Success",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

def scale_cluster(cluster_id: str, replicas: int) -> Dict[str, Any]:
    """
    Scales the specified cluster to the desired number of replicas.

    Args:
        cluster_id (str): The unique identifier of the cluster to scale.
        replicas (int): The target number of replicas. Must be a non-negative integer.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - 'cluster_id': The ID of the cluster.
            - 'previous_replicas': Simulated previous count.
            - 'current_replicas': The new replica count.
            - 'status': 'Scaled'.
    """
    # Simulate scaling delay
    time.sleep(1.0)
    
    # Simulate previous state (randomly slightly different from target)
    previous = max(1, replicas + random.randint(-2, 2))
    
    return {
        "cluster_id": cluster_id,
        "previous_replicas": previous,
        "current_replicas": replicas,
        "status": "Scaled"
    }
