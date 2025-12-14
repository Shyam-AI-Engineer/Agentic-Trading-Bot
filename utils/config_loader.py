import yaml

def load_config(config_path: str = r"D:\\GITHUB Projects\\Agentic-Trading-Bot\\config\\config.yaml") -> dict:
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    return config