# encoding:utf-8

import time
import json
from dify_client import ChatClient

from bot.dify.dify_session import SessionManager
from bot.bot import Bot
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger
from common.token_bucket import TokenBucket
from config import conf, load_config


class DifyBot(Bot):
    def __init__(self):
        super().__init__()
        # set the default api_key
        api_key = conf().get("dify_api_key")
        base_url = conf().get("dify_base_url")
        self.chat_client = ChatClient(api_key, base_url)
        self.sessionManager = SessionManager()

    def reply(self, query, context=None):
        logger.info("[DIFY] query={}".format(query))
        session_id = context["session_id"]
        nick_name = context.get("msg").from_user_nickname
        from_user_id = context.get("msg").from_user_id
        reply = None
        session_id = self.sessionManager.get_current_sessions(nick_name)

        # acquire reply content
        if context.type == ContextType.TEXT:          
            if query == "@使用说明":
                help_msg = """
输入 @新建会话 ，将新建会话。
输入 @清除所有会话 ，将清除所有会话。
                """                
                reply = Reply(ReplyType.INFO, help_msg)
            elif query == "@新建会话":
                self.sessionManager.set_current_session(nick_name, None)
                reply = Reply(ReplyType.INFO, "已新建会话")
            elif query == "@清除所有会话":
                self.sessionManager.clear_session(nick_name)
                reply = Reply(ReplyType.INFO, "所有会话已清除")
            if reply:
                return reply
            
            reply_content = self.reply_text(query, user=nick_name, session_id=session_id)
            logger.debug(
                "[DIFY] new_query={}, session_id={}, reply_cont={}, session_id={}".format(
                    query,
                    session_id,
                    reply_content["answer"],
                    reply_content["conversation_id"],
                )
            )
            session_id = reply_content["conversation_id"]
            self.sessionManager.add_session(nick_name, session_id)
            reply = Reply(ReplyType.TEXT, reply_content["answer"])
            return reply
        elif context.type == ContextType.SHARING:
            self._send_msg("我正在加紧阅读文章，请稍后...", context)

            reply_content = self.reply_text(query, user=nick_name, session_id=session_id)
            logger.debug(
                "[DIFY] new_query={}, session_id={}, reply_cont={}, session_id={}".format(
                    query,
                    session_id,
                    reply_content["answer"],
                    reply_content["conversation_id"],
                )
            )
            session_id = reply_content["conversation_id"]
            self.sessionManager.add_session(nick_name, session_id)
            reply = Reply(ReplyType.TEXT, reply_content["answer"] + "\n\n\n\n" + "# 如果想进一步了解文章内容，可以进一步提问。 #")
            return reply
        elif context.type == ContextType.ACCEPT_FRIEND:  # 好友申请，当前无默认逻辑
            welcome = f"""
终于等到你了， {nick_name}

我是<爱投资的小五>，你的专属投资顾问，主要用AI技术来帮你做好投资。
我还在不断学习中，投资中遇到什么问题你都可以随时问我，我全天24小时恭候。

使用方法上遇到什么问题，你可以输入
@使用说明
来获得帮助

注意，重要！！！
如果在使用时发现我有点不正常，甚至开始发神经，那可能是我病了，此时你可以输入
@新建会话
来重新开始一段新旅程。

祝你投资愉快，收获颇丰~            
            """
            self.sessionManager.set_current_session(nick_name, None)
            self._send_msg(welcome, context)
        else:
            reply = Reply(ReplyType.ERROR, "抱歉，暂不支持处理{}类型的消息".format(context.type))
            return reply

    def reply_text(self, query, user, session_id=None, inputs={}) -> dict:
        try:
            # Create Chat Message using ChatClient
            response_mode = "streaming"
            chat_response = self.chat_client.create_chat_message(
                inputs=inputs, 
                query=query, 
                user=user, 
                conversation_id=session_id,
                response_mode="streaming",
            )
            chat_response.raise_for_status()
            response = {
                "answer": "",
                "conversation_id": "",
            }

            if response_mode == "blocking":
                response = chat_response.json()
            else:
                for line in chat_response.iter_lines(decode_unicode=True):
                    lines = line.split('data:', 1)
                    if len(lines) > 1:
                        line = lines[-1].strip()
                        if line.startswith('{') and line.endswith('}'):
                            line = json.loads(line.strip())
                            answer = line.get('answer')
                            if(answer!=None):
                                response["answer"] += answer
                                response["conversation_id"] = line.get('conversation_id')
        except Exception as e:
            logger.error("[DIFY] chat error: {}".format(e))
            response = {"answer": "抱歉，出错了，等会儿再重新试试吧。"}         

        return response

    def _send_msg(self, msg, context):
        reply = Reply(ReplyType.TEXT, msg)
        channel = context["channel"]
        channel.send(reply, context)