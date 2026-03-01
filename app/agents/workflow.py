import asyncio
import logging
from typing import Dict, Any
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT
from io import BytesIO
from app.utils.openrouter import research_topic, summarize_text, extract_key_points, generate_recommendations

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PDF_OUTPUT_PATH = "report_output.pdf"

class AIWorkflow:
    # workflow dengan 5 step
    # 1. fetch data
    # 2. clean data
    # 3. transform data
    # 4. store data
    # 5. notify user
    
    def __init__(self, task_id: str, user_id: str, topic: str):
        self.task_id = task_id
        self.user_id = user_id
        self.topic = topic
        self.logs = []
        self.context = {}
        
        self._add_log("INFO", "Workflow Started", f"AI Research for topic: {topic}")
    
    def _add_log(self, level: str, step: str, message: str):
        # tambahin log ke list
        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "level": level,
            "step": step,
            "message": message
        }
        self.logs.append(log_entry)
        logger.info(f"[{level}] {step}: {message}")
        self._update_pdf()  # update pdf setiap ada log baru
    
    def _update_pdf(self):
        # bikin pdf dari logs
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
            
            story = []
            styles = getSampleStyleSheet()
            
            # title
            title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=20, spaceAfter=20, alignment=TA_LEFT)
            story.append(Paragraph("AI Research Report", title_style))
            story.append(Spacer(1, 0.2*inch))
            
            # info dasar
            body_style = styles['BodyText']
            story.append(Paragraph(f"<b>Task ID:</b> {self.task_id}", body_style))
            story.append(Paragraph(f"<b>User ID:</b> {self.user_id}", body_style))
            story.append(Paragraph(f"<b>Topic:</b> {self.topic}", body_style))
            story.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", body_style))
            story.append(Spacer(1, 0.3*inch))
            
            # logs
            story.append(Paragraph("<b>Research Logs:</b>", styles['Heading2']))
            story.append(Spacer(1, 0.1*inch))
            
            for log in self.logs:
                log_text = f"[{log['timestamp']}] <b>{log['level']}</b> - {log['step']}: {log['message']}"
                story.append(Paragraph(log_text, body_style))
                story.append(Spacer(1, 0.05*inch))
            
            doc.build(story)
            
            # save ke file
            with open(PDF_OUTPUT_PATH, 'wb') as f:
                f.write(buffer.getvalue())
            
            buffer.close()
        except Exception as e:
            logger.error(f"Error updating PDF: {str(e)}")
    
    async def step1_fetch_data(self) -> Dict[str, Any]:
        # step 1: ambil data pake AI
        self._add_log("INFO", "Step 1: Fetch Data", f"Starting AI research for: {self.topic}")
        await asyncio.sleep(1)
        
        try:
            # panggil openrouter buat research
            research_result = research_topic(self.topic)
            
            self.context["research_data"] = research_result
            
            self._add_log("SUCCESS", "Step 1: Fetch Data", 
                         f"Research completed! Tokens used: {research_result.get('tokens', 0)}")
            
            return {
                "step": 1,
                "name": "Fetch Data (AI Research)",
                "status": "success",
                "tokens": research_result.get('tokens', 0)
            }
        except Exception as e:
            self._add_log("ERROR", "Step 1: Fetch Data", f"Failed: {str(e)}")
            raise
    
    async def step2_clean_data(self) -> Dict[str, Any]:
        # step 2: bersihin data, extract key points
        self._add_log("INFO", "Step 2: Clean Data", "Extracting key points from research...")
        await asyncio.sleep(1)
        
        try:
            research_data = self.context.get("research_data", {})
            research_text = research_data.get("research_result", "")
            
            # extract poin penting
            key_points = extract_key_points(research_text)
            
            self.context["key_points"] = key_points
            
            self._add_log("SUCCESS", "Step 2: Clean Data", 
                         f"Extracted {len(key_points)} key points")
            
            return {
                "step": 2,
                "name": "Clean Data (Extract Key Points)",
                "status": "success",
                "key_points_count": len(key_points)
            }
        except Exception as e:
            self._add_log("ERROR", "Step 2: Clean Data", f"Failed: {str(e)}")
            raise
    
    async def step3_transform_data(self) -> Dict[str, Any]:
        # step 3: transform data jadi summary
        self._add_log("INFO", "Step 3: Transform Data", "Summarizing research data...")
        await asyncio.sleep(1)
        
        try:
            research_data = self.context.get("research_data", {})
            research_text = research_data.get("research_result", "")
            
            # bikin summary
            summary = summarize_text(research_text, max_words=150)
            
            self.context["summary"] = summary
            
            self._add_log("SUCCESS", "Step 3: Transform Data", 
                         f"Summary generated ({len(summary.split())} words)")
            
            return {
                "step": 3,
                "name": "Transform Data (Summarize)",
                "status": "success",
                "summary_words": len(summary.split())
            }
        except Exception as e:
            self._add_log("ERROR", "Step 3: Transform Data", f"Failed: {str(e)}")
            raise
    
    async def step4_store_data(self) -> Dict[str, Any]:
        # step 4: simpen hasil ke file json
        self._add_log("INFO", "Step 4: Store Data", "Storing research results...")
        await asyncio.sleep(1)
        
        try:
            import json
            
            # bikin data yang mau disimpen
            output_data = {
                "task_id": self.task_id,
                "user_id": self.user_id,
                "topic": self.topic,
                "timestamp": datetime.now().isoformat(),
                "research": self.context.get("research_data", {}),
                "key_points": self.context.get("key_points", []),
                "summary": self.context.get("summary", "")
            }
            
            output_file = f"research_output_{self.task_id[:8]}.json"
            
            # save ke file
            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2)
            
            self.context["output_file"] = output_file
            
            self._add_log("SUCCESS", "Step 4: Store Data", 
                         f"Research saved to {output_file}")
            
            return {
                "step": 4,
                "name": "Store Data",
                "status": "success",
                "output_file": output_file
            }
        except Exception as e:
            self._add_log("ERROR", "Step 4: Store Data", f"Failed: {str(e)}")
            raise
        """Step 4: Store Data - Simpan hasil research"""
        self._add_log("INFO", "Step 4: Store Data", "Storing research results...")
        await asyncio.sleep(1)
        
        try:
            import json
            
            output_data = {
                "task_id": self.task_id,
                "user_id": self.user_id,
                "topic": self.topic,
                "timestamp": datetime.now().isoformat(),
                "research": self.context.get("research_data", {}),
                "key_points": self.context.get("key_points", []),
                "summary": self.context.get("summary", "")
            }
            
            output_file = f"research_output_{self.task_id[:8]}.json"
            
            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2)
            
            self.context["output_file"] = output_file
            
            self._add_log("SUCCESS", "Step 4: Store Data", 
                         f"Research saved to {output_file}")
            
            return {
                "step": 4,
                "name": "Store Data",
                "status": "success",
                "output_file": output_file
            }
        except Exception as e:
            self._add_log("ERROR", "Step 4: Store Data", f"Failed: {str(e)}")
            raise
    
    async def step5_notify_user(self) -> Dict[str, Any]:
        # step 5: kasih notif ke user + rekomendasi
        self._add_log("INFO", "Step 5: Notify User", "Generating recommendations...")
        await asyncio.sleep(1)
        
        try:
            research_data = self.context.get("research_data", {})
            research_text = research_data.get("research_result", "")
            
            # bikin rekomendasi
            recommendations = generate_recommendations(self.topic, research_text)
            
            self.context["recommendations"] = recommendations
            
            notification = {
                "user_id": self.user_id,
                "task_id": self.task_id,
                "topic": self.topic,
                "status": "completed",
                "message": f"AI Research completed for: {self.topic}",
                "recommendations": recommendations,
                "output_file": self.context.get("output_file"),
                "pdf_report": PDF_OUTPUT_PATH
            }
            
            self.context["notification"] = notification
            
            self._add_log("SUCCESS", "Step 5: Notify User", 
                         f"Generated {len(recommendations)} recommendations. Research completed!")
            
            return {
                "step": 5,
                "name": "Notify User (Recommendations)",
                "status": "success",
                "recommendations_count": len(recommendations)
            }
        except Exception as e:
            self._add_log("ERROR", "Step 5: Notify User", f"Failed: {str(e)}")
            raise
    
    async def run_workflow(self) -> Dict[str, Any]:
        """Jalankan semua 5 steps"""
        logger.info(f"🚀 Starting AI workflow for: {self.topic}")
        
        steps = [
            self.step1_fetch_data,
            self.step2_clean_data,
            self.step3_transform_data,
            self.step4_store_data,
            self.step5_notify_user
        ]
        
        results = []
        for i, step_func in enumerate(steps, 1):
            try:
                step_result = await step_func()
                results.append(step_result)
                logger.info(f"✅ Step {i}/5 completed")
            except Exception as e:
                self._add_log("ERROR", f"Step {i}", f"Failed: {str(e)}")
                logger.error(f"❌ Step {i}/5 failed: {str(e)}")
                raise
        
        self._add_log("INFO", "Workflow Completed", "AI Research workflow finished successfully!")
        logger.info(f"🎉 AI workflow completed for: {self.topic}")
        
        return {
            "task_id": self.task_id,
            "status": "completed",
            "topic": self.topic,
            "steps": results,
            "key_points": self.context.get("key_points", []),
            "summary": self.context.get("summary", ""),
            "recommendations": self.context.get("recommendations", []),
            "output_file": self.context.get("output_file"),
            "pdf_report": PDF_OUTPUT_PATH
        }
