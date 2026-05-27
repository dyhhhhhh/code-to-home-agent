from __future__ import annotations

from .adapters import DryRunHomeAssistantAdapter
from .audit import AuditLog
from .models import ExecutionResult, HomeGraph
from .planner import RulePlanner
from .policy import PolicyEngine
from .verifier import Verifier


class HomeAgentRuntime:
    def __init__(self, home: HomeGraph) -> None:
        self.home = home
        self.planner = RulePlanner()
        self.policy = PolicyEngine()
        self.adapter = DryRunHomeAssistantAdapter()
        self.verifier = Verifier()
        self.audit = AuditLog(home.policy.audit_log)

    def handle(self, request: str) -> ExecutionResult:
        intent = self.planner.plan(request, self.home)
        policy_result = self.policy.evaluate(intent, self.home)
        if not policy_result.accepted:
            self._audit(request, intent, policy_result)
            return policy_result

        execution_result = self.adapter.execute(intent, self.home)
        if not execution_result.accepted:
            self._audit(request, intent, execution_result)
            return execution_result

        verification_result = self.verifier.verify(intent, self.home)
        self._audit(request, intent, verification_result, execution_result.details)
        return verification_result

    def _audit(
        self,
        request: str,
        intent: object,
        result: ExecutionResult,
        execution_details: dict | None = None,
    ) -> None:
        self.audit.write(
            {
                "request": request,
                "intent": getattr(intent, "__dict__", str(intent)),
                "result": result.__dict__,
                "execution": execution_details or {},
            }
        )
