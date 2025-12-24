import httpx
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.config import settings
import structlog

logger = structlog.get_logger()

class PrometheusClient:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or settings.prometheus_url
    
    async def query_instant(self, query: str) -> Optional[Dict[str, Any]]:
        """Execute instant query against Prometheus"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/query",
                    params={"query": query}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error("prometheus_query_error", query=query, error=str(e))
            return None
    
    async def query_range(self, query: str, start: datetime, end: datetime, step: str = "15s") -> Optional[Dict[str, Any]]:
        """Execute range query against Prometheus"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/query_range",
                    params={
                        "query": query,
                        "start": int(start.timestamp()),
                        "end": int(end.timestamp()),
                        "step": step
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error("prometheus_range_query_error", query=query, error=str(e))
            return None
    
    async def get_host_metrics(self, hostname: str) -> Optional[Dict[str, Any]]:
        """Fetch all metrics for a specific host"""
        try:
            metrics = {}
            
            # CPU
            cpu_result = await self.query_instant(f'node_cpu_seconds_total{{instance="{hostname}:9100"}}')
            if cpu_result and cpu_result.get('data', {}).get('result'):
                metrics['cpu_count'] = len(cpu_result['data']['result'])
            
            # Memory
            mem_result = await self.query_instant(f'node_memory_MemTotal_bytes{{instance="{hostname}:9100"}}')
            if mem_result and mem_result.get('data', {}).get('result'):
                mem_total = float(mem_result['data']['result'][0]['value'][1])
                metrics['memory_total_gb'] = mem_total / (1024**3)
            
            # Disk
            disk_result = await self.query_instant(f'node_filesystem_size_bytes{{instance="{hostname}:9100", fstype="ext4"}}')
            if disk_result and disk_result.get('data', {}).get('result'):
                disk_total = sum(float(r['value'][1]) for r in disk_result['data']['result'])
                metrics['disk_total_gb'] = disk_total / (1024**3)
            
            # Uptime
            uptime_result = await self.query_instant(f'node_boot_time_seconds{{instance="{hostname}:9100"}}')
            if uptime_result and uptime_result.get('data', {}).get('result'):
                boot_time = float(uptime_result['data']['result'][0]['value'][1])
                uptime_seconds = datetime.now().timestamp() - boot_time
                metrics['uptime_seconds'] = int(uptime_seconds)
            
            return metrics if metrics else None
        except Exception as e:
            logger.error("get_host_metrics_error", hostname=hostname, error=str(e))
            return None

prometheus_client = PrometheusClient()
