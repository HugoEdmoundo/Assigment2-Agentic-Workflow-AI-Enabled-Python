from celery import Task
from app.celery_app import app
from app.agents.workflow import AIWorkflow, PDF_OUTPUT_PATH
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

task_store = {}

class WorkflowTask(Task):
    abstract = True
    
    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        if task_id in task_store:
            task_store[task_id]['status'] = status
            task_store[task_id]['completed_at'] = datetime.now().isoformat()

@app.task(bind=True, name='run_workflow', base=WorkflowTask)
def run_workflow(self, user_id: str, topic: str):
    """
    AI Research Workflow
    
    Args:
        user_id: ID user
        topic: Topic untuk di-research
    """
    task_id = self.request.id
    
    task_store[task_id] = {
        'task_id': task_id,
        'user_id': user_id,
        'topic': topic,
        'status': 'started',
        'current_step': 0,
        'total_steps': 5,
        'started_at': datetime.now().isoformat()
    }
    
    try:
        logger.info(f"🚀 Starting AI workflow for: {topic}")
        
        workflow = AIWorkflow(task_id=task_id, user_id=user_id, topic=topic)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(workflow.run_workflow())
        loop.close()
        
        task_store[task_id].update({
            'status': 'completed',
            'current_step': 5,
            'result': result,
            'pdf_path': PDF_OUTPUT_PATH
        })
        
        logger.info(f"✅ AI workflow completed for: {topic}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ AI workflow failed: {str(e)}")
        task_store[task_id].update({
            'status': 'failed',
            'error': str(e),
            'failed_at': datetime.now().isoformat()
        })
        raise

@app.task(name='get_task_status')
def get_task_status(task_id: str):
    return task_store.get(task_id, {
        'task_id': task_id,
        'status': 'not_found',
        'error': 'Task ID not found'
    })
