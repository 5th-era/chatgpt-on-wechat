import json

class SessionManager:
    def __init__(self, sessionfile='sessions.json'):
        self.sessionfile = sessionfile
        self.sessions = self.load_sessions()

    def load_sessions(self):
        try:
            with open(self.sessionfile, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def add_session(self, nickname, session_id):
        if nickname not in self.sessions:
            self.sessions[nickname] = {"current_session": None, "sessions": []}
        if session_id not in self.sessions[nickname]["sessions"]:
            self.sessions[nickname]["sessions"].append(session_id)
            self.sessions[nickname]["current_session"] = session_id
            self.save_sessions()

    def save_sessions(self):
        with open(self.sessionfile, 'w', encoding='utf-8') as file:
            json.dump(self.sessions, file, ensure_ascii=False, indent=4)

    def retrieve_session(self, nickname):
        if nickname in self.sessions:
            return self.sessions[nickname]
        return None

    def get_current_sessions(self, nickname):
        if nickname in self.sessions:
            return self.sessions[nickname]["current_session"]
        return None

    def clear_sessions(self):
        self.sessions = {}
        self.save_sessions()

    def clear_session(self, nickname):
        if nickname in self.sessions:
            self.sessions[nickname] = {"current_session": None, "sessions": []}
            self.save_sessions()

    def set_current_session(self, nickname, session_id=None):
        if nickname in self.sessions:
            self.sessions[nickname]["current_session"] = session_id
            self.save_sessions()

# 使用示例
if __name__=="__main__":
    session = SessionManager()

    # 添加数据
    session.add_session("用户1", "thread_id_1")
    session.add_session("用户1", "thread_id_2")
    session.add_session("用户2", "thread_id_3")

    # 检索数据
    print(session.retrieve_session("用户1"))  # 应输出 未找到匹配的数据
    print(session.retrieve_session("用户2"))  # 应输出 未找到匹配的数据

    print(session.get_current_sessions("用户1"))  # 应输出 未找到匹配的数据
    print(session.get_current_sessions("用户2"))  # 应输出 未找到匹配的数据

    # 清除数据
    # session.clear_sessions()
    session.set_current_session("用户1", None)
    # 检索数据
    print(session.retrieve_session("用户1"))  # 应输出 未找到匹配的数据
    print(session.retrieve_session("用户2"))  # 应输出 未找到匹配的数据

    print(session.get_current_sessions("用户1"))  # 应输出 未找到匹配的数据
    print(session.get_current_sessions("用户2"))  # 应输出 未找到匹配的数据