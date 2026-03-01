from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from scalar_fastapi import get_scalar_api_reference
from app.models.schemas import WorkflowRequest, WorkflowResponse, WorkflowStatus
from app.tasks.tasks import run_workflow, get_task_status, PDF_OUTPUT_PATH
from celery.result import AsyncResult
import logging
import os

# setup logging biar bisa debug
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# bikin fastapi app
app = FastAPI(
    title="AI Agentic Workflow API",
    description="AI Research Workflow dengan 5 steps: Fetch Data, Clean Data, Transform Data, Store Data, Notify User",
    version="1.0.0"
)

@app.get("/", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(openapi_url=app.openapi_url, title=app.title)

# endpoint buat start workflow
@app.post("/workflow", response_model=WorkflowResponse)
async def start_workflow(request: WorkflowRequest):
    """Start AI research workflow"""
    try:
        # jalanin task pake celery
        task = run_workflow.delay(user_id=request.user_id, topic=request.topic)
        
        logger.info(f"Workflow started: {task.id} for topic: {request.topic}")
        
        return WorkflowResponse(
            task_id=task.id,
            status="processing",
            message=f"AI research started for: {request.topic}"
        )
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# cek status task
@app.get("/status/{task_id}", response_model=WorkflowStatus)
async def get_status(task_id: str):
    """Cek status workflow"""
    try:
        task_result = AsyncResult(task_id, app=run_workflow.app)
        detailed_status = get_task_status.delay(task_id).get(timeout=5)
        
        # kalo masih pending
        if task_result.state == 'PENDING':
            return WorkflowStatus(task_id=task_id, status='pending', current_step=0, total_steps=5)
        
        # kalo lagi jalan
        elif task_result.state in ['STARTED', 'PROGRESS']:
            return WorkflowStatus(
                task_id=task_id,
                user_id=detailed_status.get('user_id'),
                topic=detailed_status.get('topic'),
                status='processing',
                current_step=detailed_status.get('current_step', 1),
                total_steps=5,
                pdf_path=PDF_OUTPUT_PATH
            )
        
        # kalo udah selesai
        elif task_result.state == 'SUCCESS':
            return WorkflowStatus(
                task_id=task_id,
                user_id=detailed_status.get('user_id'),
                topic=detailed_status.get('topic'),
                status='completed',
                current_step=5,
                total_steps=5,
                result=task_result.result,
                pdf_path=PDF_OUTPUT_PATH
            )
        
        # kalo error
        elif task_result.state == 'FAILURE':
            return WorkflowStatus(
                task_id=task_id,
                status='failed',
                current_step=0,
                total_steps=5,
                error=str(task_result.info)
            )
        else:
            return WorkflowStatus(task_id=task_id, status=task_result.state.lower(), current_step=0, total_steps=5)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# download pdf report
@app.get("/pdf")
async def download_pdf():
    """Download PDF report"""
    try:
        if not os.path.exists(PDF_OUTPUT_PATH):
            raise HTTPException(status_code=404, detail="PDF not found. Run workflow first!")
        
        return FileResponse(path=PDF_OUTPUT_PATH, media_type="application/pdf", filename="report_output.pdf")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# health check endpoint
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "AI Agentic Workflow API"}
