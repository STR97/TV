import asyncio
import json
import re
import subprocess
import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONFIG_URL = "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/splitted/mixed"
WORKING_CONFIGS_FILE = "working_configs.json"

def parse_config(line):
    """Parse a configuration line and extract protocol, IP, and port."""
    try:
        if line.startswith(('vless://', 'vmess://', 'trojan://', 'ss://', 'tuic://', 'hy2://')):
            protocol = line.split('://')[0]
            match = re.search(r'@([\[\]0-9a-f.:]+):(\d+)', line)
            if match:
                ip = match.group(1)
                port = match.group(2)
                return {'protocol': protocol, 'ip': ip, 'port': port, 'config': line}
    except Exception as e:
        logger.error(f"Error parsing config {line}: {e}")
    return None

async def test_config(config):
    """Test a configuration using Xray-core."""
    try:
        # Создаем временный конфиг для Xray
        xray_config = {
            "log": {"loglevel": "warning"},
            "inbounds": [{"port": 10808, "protocol": "socks", "settings": {"auth": "noauth"}}],
            "outbounds": [{"protocol": config['protocol'], "settings": {}}]
        }
        with open("temp_config.json", "w") as f:
            json.dump(xray_config, f)

        # Запускаем Xray
        process = await asyncio.create_subprocess_exec(
            "./xray", "-c", "temp_config.json",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        try:
            await asyncio.wait_for(process.communicate(), timeout=10)
            return process.returncode == 0
        except asyncio.TimeoutError:
            process.kill()
            return False
    except Exception as e:
        logger.error(f"Error testing config {config['config']}: {e}")
        return False

async def fetch_and_check_configs():
    """Fetch and check configurations."""
    logger.info("Fetching configurations...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(CONFIG_URL)
            response.raise_for_status()
            lines = response.text.splitlines()
        except Exception as e:
            logger.error(f"Error fetching configs: {e}")
            return

    working_configs = []
    for line in lines:
        config = parse_config(line)
        if config and await test_config(config):
            working_configs.append(config)
            logger.info(f"Working config found: {config['protocol']} {config['ip']}:{config['port']}")

    # Сохраняем рабочие конфигурации
    with open(WORKING_CONFIGS_FILE, 'w') as f:
        json.dump(working_configs, f, indent=2)
    logger.info(f"Saved {len(working_configs)} working configs")

if __name__ == "__main__":
    asyncio.run(fetch_and_check_configs())
