import json
import boto3
import os
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_NAME', 'Todos')
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    print("EVENT:", json.dumps(event, ensure_ascii=False))  # デバッグ用

    method = event.get('httpMethod')
    path_params = event.get('pathParameters') or {}

    if method == 'POST':
        return create_todo(event)
    elif method == 'GET':
        if path_params and 'id' in path_params:
            return get_todo_by_id(path_params['id'])
        else:
            return list_todos()
    elif method == 'DELETE':
        return delete_todo(event)
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Unsupported method'}, ensure_ascii=False)
        }

def get_todo_by_id(todo_id):
    print("GET_TODO_BY_ID called with ID:", todo_id)
    response = table.get_item(Key={'id': todo_id})
    print("DynamoDB GET response:", response)
    item = response.get('Item')
    if item:
        return {
            'statusCode': 200,
            'body': json.dumps(item, ensure_ascii=False)
        }
    else:
        return {
            'statusCode': 404,
            'body': json.dumps({'message': 'ToDo not found'}, ensure_ascii=False)
        }

def create_todo(event):
    print("EVENT BODY:", event.get('body'))  # デバッグ
    body_str = event.get('body', '{}')
    body = json.loads(body_str)
    print("PARSED BODY:", body)  # デバッグ

    todo_id = str(uuid.uuid4())
    item = {
        'id': todo_id,
        'title': body.get('title', ''),
        'description': body.get('description', ''),
        'created_at': datetime.utcnow().isoformat()
    }
    print("PUT ITEM:", item)  # デバッグ

    table.put_item(Item=item)
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'ToDo created', 'item': item}, ensure_ascii=False)
    }


def list_todos():
    response = table.scan()
    items = response.get('Items', [])
    return {
        'statusCode': 200,
        'body': json.dumps(items, ensure_ascii=False)
    }

def delete_todo(event):
    todo_id = event.get('pathParameters', {}).get('id')
    if not todo_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Missing ID'}, ensure_ascii=False)
        }
    table.delete_item(Key={'id': todo_id})
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'ToDo deleted', 'id': todo_id}, ensure_ascii=False)
    }
