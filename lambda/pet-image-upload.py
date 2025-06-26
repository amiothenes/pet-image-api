import json
import boto3
import base64
import uuid
import os

s3 = boto3.client('s3')
BUCKET = os.environ['BUCKET_NAME']

def lambda_handler(event, context):
    label = event['queryStringParameters'].get('label')
    weight = event.get('queryStringParameters', {}).get('weight', '1')  #default = 1

    print("EVENT:", json.dumps(event))

    if label not in ['cat', 'dog']:
        return {'statusCode': 400, 'body': 'Bad Request'}

    if not event.get('body'):
        return {'statusCode': 400, 'body': 'Bad Request'}

    # Decode image
    try:
        body = base64.b64decode(event['body'])
    except Exception:
        return {'statusCode': 400, 'body': 'Bad Request'}

    #png jpg webp strict validation
    if body.startswith(b'\xFF\xD8\xFF'):
        ext = 'jpg'
        content_type = 'image/jpeg'
    elif body.startswith(b'\x89PNG\r\n\x1a\n'):
        ext = 'png'
        content_type = 'image/png'
    elif body.startswith(b'RIFF') and b'WEBP' in body[8:16]:
        ext = 'webp'
        content_type = 'image/webp'
    else:
        return {'statusCode': 400, 'body': 'Bad Request'}

    # Save to S3
    filename = f"{label}/{uuid.uuid4()}.{ext}"
    s3.put_object(
        Bucket=BUCKET,
        Key=filename,
        Body=body,
        ContentType=content_type,
        Metadata={
            'weight': str(weight)})

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Upload successful',
            'file': filename,
            'weight': weight})
    }
