"""
Agent 编排器
参考 ai-agent-gateway/src/core/orchestrator.ts
"""
import uuid
from typing import Dict, List, Optional, Any

from xiaohongshu_agent.gateway.types import (
    Agent, AgentHandler, AgentContext, UnifiedMessage, Session
)


class SubTask:
    """子任务"""

    def __init__(
        self,
        task_id: str,
        description: str,
        agent_id: str,
        depends_on: Optional[List[str]] = None
    ):
        self.id = task_id
        self.description = description
        self.agent_id = agent_id
        self.depends_on = depends_on or []
        self.status = "pending"
        self.result: Optional[str] = None
        self.error: Optional[str] = None


class OrchestrationPlan:
    """编排计划"""

    def __init__(self, plan_id: str, original_task: str):
        self.id = plan_id
        self.original_task = original_task
        self.tasks: List[SubTask] = []
        self.status = "planning"


class AgentOrchestrator:
    """Agent 编排器 - 多 Agent 协同"""

    def __init__(
        self,
        agent_registry: Any,
        tool_gateway: Any,
        session_manager: Any,
        logger: Optional[Any] = None,
        config: Optional[Dict] = None
    ):
        self.agent_registry = agent_registry
        self.tool_gateway = tool_gateway
        self.session_manager = session_manager
        self.logger = logger
        self.config = config or {}
        self.plans: Dict[str, OrchestrationPlan] = {}

        # 配置项
        self.auto_decompose = self.config.get("autoDecompose", True)
        self.max_concurrent = self.config.get("maxConcurrent", 3)

    def create_plan(self, task: str) -> OrchestrationPlan:
        """创建编排计划"""
        plan_id = f"plan_{uuid.uuid4().hex[:8]}"
        plan = OrchestrationPlan(plan_id, task)

        if self.auto_decompose:
            plan.tasks = self._decompose_task(task)

        self.plans[plan_id] = plan
        self._log("info", "Orchestration plan created", plan_id=plan_id, task_count=len(plan.tasks))

        return plan

    def _decompose_task(self, task: str) -> List[SubTask]:
        """分解任务（简化版）"""
        task_lower = task.lower()
        agents = self.agent_registry.get_online()
        tasks = []

        # 简单关键词匹配
        if any(kw in task_lower for kw in ["代码", "开发", "写", "code"]):
            tasks.append(SubTask(
                task_id=f"task_{len(tasks) + 1}",
                description="编写代码",
                agent_id=self._find_agent_by_capability(agents, "code") or "assistant"
            ))

        if any(kw in task_lower for kw in ["测试", "验证", "test"]):
            tasks.append(SubTask(
                task_id=f"task_{len(tasks) + 1}",
                description="编写测试",
                agent_id=self._find_agent_by_capability(agents, "test") or "assistant"
            ))

        if any(kw in task_lower for kw in ["部署", "发布", "deploy"]):
            tasks.append(SubTask(
                task_id=f"task_{len(tasks) + 1}",
                description="部署发布",
                agent_id=self._find_agent_by_capability(agents, "deploy") or "assistant"
            ))

        if any(kw in task_lower for kw in ["文档", "说明", "docs"]):
            tasks.append(SubTask(
                task_id=f"task_{len(tasks) + 1}",
                description="编写文档",
                agent_id=self._find_agent_by_capability(agents, "docs") or "assistant"
            ))

        # 默认任务
        if not tasks:
            tasks.append(SubTask(
                task_id="task_1",
                description=task,
                agent_id="assistant"
            ))

        return tasks

    def _find_agent_by_capability(self, agents: List[Agent], capability: str) -> Optional[str]:
        """根据能力查找 Agent"""
        for agent in agents:
            if agent.capabilities:
                for cap in agent.capabilities:
                    if capability.lower() in cap.name.lower():
                        return agent.id
        return None

    async def execute_plan(
        self,
        plan_id: str,
        message: UnifiedMessage
    ) -> Dict[str, Any]:
        """执行编排计划"""
        plan = self.plans.get(plan_id)
        if not plan:
            return {"content": f"Plan not found: {plan_id}", "metadata": {"plan_id": plan_id}}

        plan.status = "executing"
        self._log("info", "Executing plan", plan_id=plan_id, task_count=len(plan.tasks))

        completed = set()

        for task in plan.tasks:
            # 检查依赖
            if task.depends_on:
                pending = [d for d in task.depends_on if d not in completed]
                if pending:
                    continue

            task.status = "running"

            try:
                agent = self.agent_registry.get(task.agent_id)
                if not agent:
                    raise Exception(f"Agent not found: {task.agent_id}")

                # 构建子任务消息
                sub_message = UnifiedMessage(
                    id=uuid.uuid4().hex,
                    userId=message.userId,
                    channel=message.channel,
                    content=f"Subtask: {task.description}\n\nOriginal: {plan.original_task}",
                    sessionId=message.sessionId
                )

                context = AgentContext(
                    session=message.sessionId and self.session_manager.get(message.sessionId) or Session(
                        id=message.sessionId or uuid.uuid4().hex,
                        userId=message.userId,
                        channel=message.channel
                    ),
                    sessionManager=self.session_manager,
                    toolGateway=self.tool_gateway,
                    logger=self.logger
                )

                response = await agent.handler(sub_message, context)
                task.result = response.content
                task.status = "completed"
                completed.add(task.id)

            except Exception as e:
                task.status = "failed"
                task.error = str(e)
                self._log("error", "Task failed", task_id=task.id, error=str(e))

        # 更新计划状态
        plan.status = "completed" if all(t.status == "completed" for t in plan.tasks) else "failed"

        # 生成汇总
        summary = self._generate_summary(plan)

        return {
            "content": summary,
            "metadata": {"plan_id": plan_id, "results": [
                {"id": t.id, "description": t.description, "status": t.status}
                for t in plan.tasks
            ]}
        }

    def _generate_summary(self, plan: OrchestrationPlan) -> str:
        """生成汇总"""
        lines = [f"📋 任务编排完成: {plan.original_task}", "", "--- 执行结果 ---", ""]

        for task in plan.tasks:
            icon = "✅" if task.status == "completed" else "❌" if task.status == "failed" else "⏳"
            lines.append(f"{icon} [{task.agent_id}] {task.description}")
            if task.result:
                lines.append(f"   └─ {task.result[:100]}...")
            if task.error:
                lines.append(f"   └─ ❌ Error: {task.error}")
            lines.append("")

        all_done = all(t.status == "completed" for t in plan.tasks)
        lines.append("🎉 所有子任务已完成！" if all_done else "⚠️ 部分任务执行失败")

        return "\n".join(lines)

    async def execute(self, task: str, message: UnifiedMessage) -> Dict[str, Any]:
        """一步执行"""
        plan = self.create_plan(task)
        return await self.execute_plan(plan.id, message)

    def create_orchestrator_agent(self) -> Agent:
        """创建编排器 Agent"""

        async def handler(message: UnifiedMessage, context: AgentContext) -> Any:
            content = message.content

            if content.startswith("/orch "):
                task = content[6:].strip()
                return await self.execute(task, message)

            if content.startswith("/plan "):
                task = content[6:].strip()
                plan = self.create_plan(task)
                return {
                    "content": f"📋 编排计划已创建\n\n任务: {plan.original_task}\n子任务: {len(plan.tasks)}\n\nPlan ID: {plan.id}\n\n使用 /execute {plan.id} 执行"
                }

            if content.startswith("/execute "):
                plan_id = content[9:].strip()
                return await self.execute_plan(plan_id, message)

            if content == "/plans":
                plans = list(self.plans.values())
                summary = "\n".join(
                    f"- {p.id}: {p.original_task} ({p.status}, {len(p.tasks)} tasks)"
                    for p in plans
                )
                return {"content": f"📋 当前计划:\n\n{summary or '无'}"}

            return {
                "content": "使用 /orch <task> 直接执行\n使用 /plan <task> 创建计划\n使用 /execute <planId> 执行计划"
            }

        return Agent(
            id="orchestrator",
            name="Orchestrator Agent",
            description="多 Agent 协同编排器",
            version="1.0.0",
            status="online",
            capabilities=[],
            handler=handler
        )

    def _log(self, level: str, message: str, **kwargs):
        if self.logger:
            getattr(self.logger, level)(message, **kwargs)
