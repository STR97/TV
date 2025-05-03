import json
from http import HTTPStatus

def main(event, context):
    try:
        # Читаем рабочие конфигурации из файла (предполагается, что файл обновляется GitHub Actions)
        with open('working_configs.json', 'r') as f:
            configs = json.load(f)
        return {
            'statusCode': HTTPStatus.OK,
            'body': json.dumps(configs),
            'headers': {'Content-Type': 'application/json'}
        }
    except FileNotFoundError:
        return {
            'statusCode': HTTPStatus.OK,
            'body': json.dumps([]),
            'headers': {'Content-Type': 'application/json'}
        }
    except Exception as e:
        return {
            'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR,
            'body': json.dumps({'error': str(e)}),
            'headers': {'Content-Type': 'application/json'}
        }
