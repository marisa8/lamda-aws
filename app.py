import json
import boto3
import os
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_NAME', 'Todos')
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    method = event.get('httpMethod')

    if method == 'POST':
        return create_todo(event)
    elif method == 'GET':
        return list_todos()
    elif method == 'DELETE':
        return delete_todo(event)
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Unsupported method'})
        }

def create_todo(event):
    body = json.loads(event.get('body', '{}'))
    todo_id = str(uuid.uuid4())
    item = {
        'id': todo_id,
        'title': body.get('title', ''),
        'description': body.get('description', ''),
        'created_at': datetime.utcnow().isoformat()
    }
    table.put_item(Item=item)
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'ToDo created', 'item': item})
    }

def list_todos():
    response = table.scan()
    items = response.get('Items', [])
    return {
        'statusCode': 200,
        'body': json.dumps(items)
    }

def delete_todo(event):
    todo_id = event.get('pathParameters', {}).get('id')
    if not todo_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Missing ID'})
        }
    table.delete_item(Key={'id': todo_id})
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'ToDo deleted', 'id': todo_id})
    }