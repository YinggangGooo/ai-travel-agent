import streamlit as st
import asyncio
import os
import random
from datetime import datetime
from openai import OpenAI
import json

# 尝试加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
    ENV_LOADED = True
except ImportError:
    ENV_LOADED = False

# 页面配置
st.set_page_config(
    page_title="AI旅行规划代理 - OpenAI版",
    page_icon="🏖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .user-message {
        background-color: #e3f2fd;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 5px solid #2196f3;
    }
    .assistant-message {
        background-color: #f0f8ff;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 5px solid #4dabf7;
    }
    .system-message {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0;
        border-left: 3px solid #6c757d;
        font-size: 0.9em;
    }
    .stButton button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

class OpenAITravelAgent:
    def __init__(self):
        self.client = None
        self.initialized = False
        
    def initialize(self):
        """初始化OpenAI客户端"""
        try:
            # 从环境变量或secrets获取配置
            api_key = os.environ.get("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
            
            if not api_key:
                return False, "❌ 未设置OpenAI API密钥"
            
            self.client = OpenAI(api_key=api_key)
            self.initialized = True
            return True, "✅ OpenAI客户端初始化成功"
            
        except Exception as e:
            return False, f"❌ 初始化失败: {str(e)}"
    
    def get_random_destination(self):
        """获取随机目的地"""
        destinations = [
            "巴塞罗那, 西班牙", "巴黎, 法国", "东京, 日本", 
            "纽约, 美国", "伦敦, 英国", "悉尼, 澳大利亚",
            "罗马, 意大利", "京都, 日本", "新加坡",
            "开普敦, 南非", "里约热内卢, 巴西", "迪拜, 阿联酋",
            "北京, 中国", "上海, 中国", "香港, 中国", "台北, 台湾"
        ]
        return random.choice(destinations)
    
    def get_travel_tips(self):
        """获取旅行贴士"""
        tips = [
            "📋 提前办理签证和购买旅行保险",
            "💵 准备一些当地货币现金，方便小额支付", 
            "🗺️ 下载离线地图和翻译应用",
            "🚨 了解当地的紧急联系电话",
            "💊 准备常用药品和防晒用品",
            "🔌 带上合适的电源转换插头",
            "📞 保存大使馆联系方式",
            "🎒 复印重要证件并分开存放"
        ]
        return "\n".join(tips)
    
    def process_request(self, user_input):
        """处理用户请求"""
        if not self.initialized:
            return "❌ 代理未初始化，请先在侧边栏点击初始化按钮"
        
        try:
            # 智能工具调用检测
            tools_used = []
            enhanced_prompt = user_input
            
            if any(keyword in user_input for keyword in ["随机", "推荐", "不知道去哪", "随便"]):
                destination = self.get_random_destination()
                tools_used.append(f"🎲 随机选择了: {destination}")
                enhanced_prompt = f"{user_input}\n\n随机选择的目的地: {destination}"
            
            if any(keyword in user_input for keyword in ["贴士", "建议", "提示", "注意", "准备"]):
                tips = self.get_travel_tips()
                tools_used.append("💡 提供了旅行贴士")
                enhanced_prompt = f"{user_input}\n\n参考旅行贴士: {tips}"
            
            # 完整的系统提示词
            system_message = """你是一个专业、友好、经验丰富的旅行规划专家。请用中文回复，遵循以下原则：

1. **个性化服务**：根据用户需求提供定制化建议
2. **详细具体**：提供具体的景点、餐厅、交通方式
3. **实用建议**：包括预算、时间安排、注意事项
4. **格式清晰**：使用适当的标题、列表和分段
5. **热情友好**：保持积极、鼓励的语气

请为用户创造难忘的旅行体验！"""
            
            # 调用OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # 可以改为 gpt-4, gpt-3.5-turbo 等
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": enhanced_prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            ai_response = response.choices[0].message.content
            
            # 如果使用了工具，在回复开头说明
            if tools_used:
                tools_info = " | ".join(tools_used)
                ai_response = f"🔧 {tools_info}\n\n{ai_response}"
            
            return ai_response
            
        except Exception as e:
            return f"❌ 处理请求时出错: {str(e)}"

# 初始化session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent" not in st.session_state:
    st.session_state.agent = OpenAITravelAgent()
if "agent_status" not in st.session_state:
    st.session_state.agent_status = "未初始化"
if "conversation_count" not in st.session_state:
    st.session_state.conversation_count = 0

# 标题和介绍
st.markdown('<h1 class="main-header">🏖️ AI 智能旅行规划代理</h1>', unsafe_allow_html=True)

# 侧边栏
with st.sidebar:
    st.header("🚀 控制面板")
    
    # 系统状态
    st.subheader("📊 系统状态")
    if not ENV_LOADED:
        st.warning("环境变量未加载")
    else:
        st.success("环境正常")
    
    # 初始化代理按钮
    if st.button("🔄 初始化AI代理", use_container_width=True, type="primary"):
        with st.spinner("初始化中..."):
            success, status = st.session_state.agent.initialize()
            st.session_state.agent_status = status
            if success:
                st.success("初始化成功！")
            else:
                st.error("初始化失败")
            st.rerun()
    
    # 显示代理状态
    st.subheader("🔧 代理状态")
    if "成功" in st.session_state.agent_status:
        st.success(st.session_state.agent_status)
    elif "失败" in st.session_state.agent_status:
        st.error(st.session_state.agent_status)
    else:
        st.warning(st.session_state.agent_status)
    
    st.markdown("---")
    st.subheader("⚡ 快速操作")
    
    quick_actions = [
        ("🎲 随机目的地", "推荐一个随机旅行目的地并详细规划"),
        ("📅 三日游", "帮我规划一个精彩的三天旅行行程"),
        ("🌅 单日游", "规划一个充实的一日游行程"),
        ("💡 旅行贴士", "给我全面的旅行准备建议和贴士"),
        ("🏨 周末之旅", "规划一个放松的周末短途旅行"),
        ("💰 预算旅行", "推荐经济实惠的旅行方案")
    ]
    
    for text, command in quick_actions:
        if st.button(text, use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": command})
            st.rerun()
    
    if st.button("🔄 清空对话", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.subheader("📈 会话统计")
    st.info(f"对话轮次: {st.session_state.conversation_count}")
    
    st.markdown("---")
    st.subheader("💡 使用提示")
    st.markdown("""
    - 🎯 **具体需求**获得更好结果
    - 🌍 **指定偏好**如预算、兴趣
    - 💬 **多轮对话**完善计划
    - ⚡ **先初始化**代理再使用
    """)

# 主对话区域
chat_container = st.container()

with chat_container:
    # 显示欢迎信息
    if len(st.session_state.messages) == 0:
        st.markdown('<div class="system-message">🚀 欢迎使用 AI 旅行规划代理！</div>', unsafe_allow_html=True)
        st.markdown('<div class="system-message">💡 我可以帮您：规划旅行行程、推荐目的地、提供旅行建议、制定预算等</div>', unsafe_allow_html=True)
        st.markdown('<div class="system-message">👇 请在侧边栏点击"初始化AI代理"，然后开始使用</div>', unsafe_allow_html=True)
    
    # 显示对话历史
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="user-message">👤 您: {message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="assistant-message">🤖 AI: {message["content"]}</div>', unsafe_allow_html=True)

# 用户输入区域
st.markdown("---")
st.subheader("💬 与AI旅行专家对话")

input_col1, input_col2 = st.columns([4, 1])

with input_col1:
    user_input = st.text_input(
        "输入您的旅行需求:",
        placeholder="例如：帮我规划一个巴黎三日游，预算中等..." if st.session_state.agent.initialized else "请先在侧边栏初始化AI代理...",
        label_visibility="collapsed",
        disabled=not st.session_state.agent.initialized
    )

with input_col2:
    send_button = st.button("发送", use_container_width=True, disabled=not st.session_state.agent.initialized)

# 处理用户输入
if send_button and user_input and st.session_state.agent.initialized:
    # 添加用户消息
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.conversation_count += 1
    
    # 显示AI响应
    with st.spinner("🤔 AI旅行专家思考中..."):
        try:
            ai_response = st.session_state.agent.process_request(user_input)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            st.rerun()
            
        except Exception as e:
            error_msg = f"抱歉，处理请求时出错: {str(e)}"
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            st.rerun()

# 页脚
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #6c757d;'>"
    "🤖 基于 OpenAI GPT-4 构建 | 🏖️ AI 旅行规划代理 | 🌐 部署于 Streamlit Cloud"
    "</div>",
    unsafe_allow_html=True
)