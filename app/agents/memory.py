import datetime
from google.cloud import firestore
import os

project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "aurix-ai-489816")
db = firestore.Client(project=project_id)

class MemoryManager:
    def store_feedback(self, company: str, report: str, feedback: str):
        db.collection("feedback_loop").add({
            "timestamp": datetime.datetime.utcnow(),
            "company": company,
            "report": report,
            "feedback": feedback
        })

    def get_recent_feedback(self, company: str, limit=5):
        docs = db.collection("feedback_loop").where("company", "==", company).order_by("timestamp", direction=firestore.Query.DESCENDING).limit(limit).stream()
        return [doc.to_dict() for doc in docs]
