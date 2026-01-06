import pytest
import time
from src.tools import get_service_health, restart_service, scale_cluster

def test_get_service_health_structure():
    """Tests that get_service_health returns correct structure."""
    result = get_service_health("test-service")
    
    assert isinstance(result, dict)
    assert "service" in result
    assert "status" in result
    assert "cpu_usage_percent" in result
    assert "memory_usage_mb" in result
    
    assert result["service"] == "test-service"
    assert result["status"] in ["Running", "Failed", "Degraded"]

def test_get_service_health_values():
    """Tests that get_service_health returns valid values."""
    result = get_service_health("api-gateway")
    
    # CPU should be between 5 and 95
    assert 5.0 <= result["cpu_usage_percent"] <= 95.0
    
    # Memory should be between 128 and 4096 MB
    assert 128 <= result["memory_usage_mb"] <= 4096

def test_restart_service_graceful():
    """Tests graceful restart mode."""
    start_time = time.time()
    result = restart_service("web-server", force=False)
    duration = time.time() - start_time
    
    assert result["service"] == "web-server"
    assert result["action"] == "restart"
    assert result["mode"] == "graceful"
    assert result["status"] == "Success"
    assert "timestamp" in result
    
    # Graceful should take ~1 second
    assert 0.9 <= duration <= 1.5

def test_restart_service_force():
    """Tests force restart mode."""
    start_time = time.time()
    result = restart_service("database", force=True)
    duration = time.time() - start_time
    
    assert result["service"] == "database"
    assert result["mode"] == "force"
    assert result["status"] == "Success"
    
    # Force should take ~2 seconds
    assert 1.9 <= duration <= 2.5

def test_restart_service_default():
    """Tests that restart_service defaults to graceful."""
    result = restart_service("cache-service")
    
    # Should default to graceful (force=False)
    assert result["mode"] == "graceful"

def test_scale_cluster_structure():
    """Tests that scale_cluster returns correct structure."""
    result = scale_cluster("prod-cluster", 5)
    
    assert isinstance(result, dict)
    assert "cluster_id" in result
    assert "previous_replicas" in result
    assert "current_replicas" in result
    assert "status" in result
    
    assert result["cluster_id"] == "prod-cluster"
    assert result["current_replicas"] == 5
    assert result["status"] == "Scaled"

def test_scale_cluster_values():
    """Tests that scale_cluster produces valid replica counts."""
    result = scale_cluster("test-cluster", 10)
    
    # Previous should be close to target (within ±2, minimum 1)
    assert result["previous_replicas"] >= 1
    assert abs(result["previous_replicas"] - 10) <= 2

def test_scale_cluster_scale_up():
    """Tests scaling up scenario."""
    result = scale_cluster("east-cluster", 20)
    
    assert result["cluster_id"] == "east-cluster"
    assert result["current_replicas"] == 20

def test_scale_cluster_scale_down():
    """Tests scaling down scenario."""
    result = scale_cluster("west-cluster", 3)
    
    assert result["cluster_id"] == "west-cluster"
    assert result["current_replicas"] == 3
    assert result["previous_replicas"] >= 1  # Can't go below 1

def test_scale_cluster_timing():
    """Tests that scale_cluster has appropriate delay."""
    start_time = time.time()
    scale_cluster("timing-test", 5)
    duration = time.time() - start_time
    
    # Should take ~1 second
    assert 0.9 <= duration <= 1.5

def test_get_service_health_multiple_calls():
    """Tests that multiple calls return valid but different results."""
    results = [get_service_health("multi-test") for _ in range(3)]
    
    # All should have valid structure
    for r in results:
        assert r["service"] == "multi-test"
        assert r["status"] in ["Running", "Failed", "Degraded"]
    
    # CPU values should vary (with very high probability)
    cpu_values = [r["cpu_usage_percent"] for r in results]
    assert len(set(cpu_values)) >= 2  # At least 2 different values

def test_restart_service_timestamp_format():
    """Tests that timestamp is properly formatted."""
    result = restart_service("time-test")
    
    # Should be in format YYYY-MM-DD HH:MM:SS
    timestamp = result["timestamp"]
    assert len(timestamp) == 19
    assert timestamp[4] == "-"
    assert timestamp[7] == "-"
    assert timestamp[10] == " "
    assert timestamp[13] == ":"
    assert timestamp[16] == ":"

if __name__ == "__main__":
    import sys
    try:
        test_get_service_health_structure()
        print("test_get_service_health_structure passed")
        test_get_service_health_values()
        print("test_get_service_health_values passed")
        test_restart_service_graceful()
        print("test_restart_service_graceful passed")
        test_restart_service_force()
        print("test_restart_service_force passed")
        test_scale_cluster_structure()
        print("test_scale_cluster_structure passed")
        test_scale_cluster_values()
        print("test_scale_cluster_values passed")
        test_scale_cluster_timing()
        print("test_scale_cluster_timing passed")
        test_restart_service_timestamp_format()
        print("test_restart_service_timestamp_format passed")
    except AssertionError as e:
        print(f"Test failed: {e}")
        sys.exit(1)

