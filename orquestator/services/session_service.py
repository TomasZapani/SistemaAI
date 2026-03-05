from datetime import datetime


class SessionService:
    def __init__(self):
        self.sessions = {}
    
    def create_session(self, call_sid: str, initial_messages: list):
        self.sessions[call_sid] = {
            "messages": initial_messages,
            "created_at": datetime.now()
        }
    
    def get_session(self, call_sid: str):
        return self.sessions.get(call_sid)
    
    def add_message(self, call_sid: str, role: str, content: str):
        if call_sid in self.sessions:
            self.sessions[call_sid]["messages"].append({
                "role": role,
                "content": content
            })
    
    def delete_session(self, call_sid: str):
        self.sessions.pop(call_sid, None)