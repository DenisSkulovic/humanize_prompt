from fastapi import FastAPI
from api.controllers.humanization_controller import HumanizationController
from api.controllers.feedback_controller import FeedbackController
from api.controllers.management_controller import ManagementController
from database_service import DatabaseService
from services.message_queue_service import MessageQueueService

# Initialize FastAPI app
app = FastAPI(title="Humanization API", version="1.0.0")

# Instantiate shared services
db_service = DatabaseService()
message_queue = MessageQueueService()

# Instantiate controllers with shared services
humanization_controller = HumanizationController(db_service, message_queue)
feedback_controller = FeedbackController(db_service)
management_controller = ManagementController(db_service)

# Register routes from controllers
app.include_router(humanization_controller.router)
app.include_router(feedback_controller.router)
app.include_router(management_controller.router)