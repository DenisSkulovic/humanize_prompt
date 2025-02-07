from fastapi import FastAPI
from api.controller.humanization_controller import HumanizationController
from api.controller.feedback_controller import FeedbackController
from api.controller.management_controller import ManagementController
from database.database_service import DatabaseService
from message_queue.message_queue_service import MessageQueueService
from cache.cache_service import CacheService

# Initialize FastAPI app
app = FastAPI(title="Humanization API", version="1.0.0")

# Instantiate shared services
db_service = DatabaseService()
messaging_service = MessageQueueService()
cache_service = CacheService()

# Instantiate controllers with shared services
humanization_controller = HumanizationController(db_service=db_service, cache_service=cache_service, messaging_service=messaging_service)
feedback_controller = FeedbackController(db_service=db_service)
management_controller = ManagementController(db_service=db_service)
def register_routes(app: FastAPI):
    # Register routes from controllers
    app.include_router(humanization_controller.router)
    app.include_router(feedback_controller.router)
    app.include_router(management_controller.router)