from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from starlette_prometheus import metrics, PrometheusMiddleware
from starlette.requests import Request
#from starlette.middleware.cors import CORSMiddleware

from google.cloud import pubsub_v1
import requests
from requests.exceptions import ConnectionError

from image_processor import settings


from . import VERSION, PREFIX
from .routers import processor
from .utils import check_liveness, check_readiness

from image_processor.logger import logger

app = FastAPI(
    title='image-processor',
    description='Microservice for processing images',
    version=VERSION,
    openapi_url='/openapi.json',
    docs_url=None,
    redoc_url=None
)

# origins = [
#     "http://localhost",
#     "http://localhost:3000",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

@app.get('/docs', include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=f'https://34.65.148.232/{app.title + app.openapi_url}',
        # openapi_url=f'/{app.title + app.openapi_url}',
        title=app.title + ' - Swagger UI'
    )


@app.middleware('http')
async def logger_middleware(request: Request, call_next):
    path = PrometheusMiddleware.get_path_template(request)
    logger.info(f'{path} ENTRY', extra={'unique_log_id': request.headers.get('unique_log_id', 'Not provided')})
    response = await call_next(request)
    logger.info(f'{path} EXIT', extra={'unique_log_id': request.headers.get('unique_log_id', 'Not provided')})
    return response


app.add_middleware(PrometheusMiddleware)
app.add_route('/metrics/', metrics)

app.include_router(
    processor.router, prefix=PREFIX, responses={404: {'description': 'Not found'}},
)

app.add_route('/health/live', check_liveness)
app.add_route('/health/ready', check_readiness)



subscriber = pubsub_v1.SubscriberClient()
publisher = pubsub_v1.PublisherClient()

topic_name = 'projects/{project_id}/topics/{topic}'.format(
    project_id='forward-leaf-258910',
    topic='image_processed',
)
subscription_name = 'projects/{project_id}/subscriptions/{sub}'.format(
    project_id='forward-leaf-258910',
    sub='image-processor',
)


def callback(message):
    url = message.attributes["image_url"]
    image_id = message.attributes["image_id"]
    req_data = { 'url': url }
    print("Processing image")
    try:
        res = requests.post('https://rso-image-classifier.cognitiveservices.azure.com/vision/v2.0/describe', json=req_data, headers={'Ocp-Apim-Subscription-Key': settings.AZURE_KEY, 'Content-Type': 'application/json'})
    except ConnectionError:
        message.nack()
    else:
        message.ack()
        try:
            x = res.json()
            #print(x)
            image_tags = ", ".join(x["description"]["tags"])
            publisher.publish(topic_name, b'', image_id=image_id, image_tags=image_tags)
        except:
            pass

future = subscriber.subscribe(subscription_name, callback)
