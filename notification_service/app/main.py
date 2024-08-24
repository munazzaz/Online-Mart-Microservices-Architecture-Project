# Mannual sedning Notification_Service
from fastapi import FastAPI, BackgroundTasks
from app.config import MailBody
from app.mailer import send_email




from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.consumer import consume_order_topic
import asyncio



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start background tasks or any setup
    consumer_task = asyncio.create_task(consume_order_topic())
    yield
    # Perform cleanup
    await consumer_task

app = FastAPI(
    lifespan=lifespan,
    title="Notification Service API",
    version="0.0.1",
    description = "The Notification Service API is designed to streamline communication with your users by delivering timely and relevant notifications.",
    servers=[
        {
            "url": "http://127.0.0.1:8009/",
            "description": "Local Development Server"
        }
        ]
)




# app = FastAPI()

@app.get("/")
def index():
    return {"status":"fastapi mailserver is running"}



@app.post("/send_email")
def schedule_mail(req: MailBody, tasks: BackgroundTasks):
    data =  req.dict()
    tasks.add_task(send_email, data)
    return {"status": 200, "message":"email has been scheduled"}