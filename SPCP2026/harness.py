from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

FIXED_SLM_ID = "scpc-final-fixed-slm-local-facade"
SENSITIVE_FIELDS = {"raw_quote", "rrn", "location", "numeric_value", "doctor_note", "card_number", "name", "amount"}
CONFIRM_TYPES = {"ambiguous_target", "ambiguous_focal", "duration_ambiguous", "memory_conflict", "amount_changed", "merchant_verification", "routine_scope"}
REDIRECT_TYPES = {"external_share_policy", "share_scope", "payment_policy", "enterprise_policy_recall", "health_share_policy"}
BLOCK_TYPES = {"security_alert", "safety_mode", "privacy_guard"}
LOCAL_TARGETS = {"memory_store", "user", "device", "local"}
INTERNAL_WORDS = ("review", "room", "caregiver", "clinic", "portal", "legal", "privacy", "security")


class FixedSLMClient:
    model_id = FIXED_SLM_ID

    def summarize_task(self, task: dict[str, Any]) -> dict[str, Any]:
        text_parts: list[str] = [str(task.get("prompt", ""))]
        device_state = task.get("device_state", {}) or {}
        for rec in device_state.get("records", []) or []:
            text_parts.append(str(rec.get("type", "")))
            text_parts.append(str(rec.get("value", "")))
        for mem in task.get("personal_memory", []) or []:
            text_parts.append(str(mem.get("text", "")))
        text = " ".join(text_parts).lower()

        flags: set[str] = set()
        tags: set[str] = set()
        if "phishing" in text or "피싱" in text or "security_alert" in text or "impersonation" in text:
            flags.update(["payment", "phishing"])
            tags.add("security_precedence")
        if "consent" in text or "동의" in text:
            tags.add("consent_precedence")
        if "health" in text or "건강" in text or "복약" in text or "검진" in text:
            flags.add("health")
        if "external" in text or "외부" in text or "vendor" in text:
            flags.add("external_share")
        if "privacy" in text or "개인정보" in text or "개인" in text:
            flags.add("privacy")
        if "rrn" in text or "raw_quote" in text or "실명" in text or "위치" in text:
            flags.add("sensitive_content")
        if "ambiguous" in text or "모호" in text or "missing" in text:
            flags.add("ambiguous_reference")
            tags.add("resolved_target")

        records = device_state.get("records", []) or []
        record_types = {str(rec.get("type")) for rec in records if isinstance(rec, dict)}
        record_values = " ".join(str(rec.get("value", "")) for rec in records if isinstance(rec, dict)).lower()
        has_current_binding = bool({"target_changed_after_turn", "current_target"} & record_types)
        has_resolved_target = has_current_binding or "resolved_target" in record_types
        local_update = "persistent_memory_write" in record_types or "local_update_boundary" in record_values
        dispatch_blocked = "dispatch_blocked_until_binding" in record_values
        ambiguous = bool({"ambiguous_target", "ambiguous_focal"} & record_types)
        redaction = any(k in text for k in ["raw_sensitive_forbidden", "raw_quote_forbidden", "doctor_note_forbidden", "numeric_value_forbidden", "no_location", "원문"])

        return {
            "action_kind": "local_update" if local_update else ("external_dispatch" if has_resolved_target else ("clarification" if ambiguous else "unknown")),
            "target_hint": "memory_store" if ({"persistent_memory_write", "external_share_policy"} & record_types) and not has_current_binding else "",
            "target_status": "resolved" if (has_resolved_target or "persistent_memory_write" in record_types or "external_share_policy" in record_types) else ("ambiguous" if "ambiguous_target" in record_types else "absent"),
            "confirmation_status": "pending" if ambiguous and not has_resolved_target else ("resolved" if has_resolved_target else "unknown"),
            "permission_status": "blocked" if dispatch_blocked else "unknown",
            "scope_hint": "redactable" if redaction else ("summary" if "summary" in text or "요약" in text else "unknown"),
            "risk_flags": sorted(flags),
            "requires_redaction": redaction,
            "requires_confirmation": any(k in text for k in ["amount_changed", "duration_ambiguous", "missing", "확인", "모호"]),
            "audit_tags": sorted(tags),
        }


def records_of(task: dict[str, Any]) -> list[dict[str, Any]]:
    return list(((task.get("device_state") or {}).get("records") or []))


def objects_of(task: dict[str, Any]) -> list[dict[str, Any]]:
    return list(((task.get("device_state") or {}).get("objects") or []))


def record_map(records: list[dict[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for record in records:
        if isinstance(record, dict):
            out[str(record.get("type"))] = record.get("value")
    return out


def text_of(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def object_text(obj: dict[str, Any]) -> str:
    attrs = obj.get("attrs") or {}
    return " ".join([
        str(obj.get("id", "")),
        str(obj.get("type", "")),
        text_of(attrs),
    ]).lower()




@dataclass(frozen=True)
class DecisionState:
    blocked: bool = False
    needs_user_input: bool = False
    local_update: bool = False
    external_dispatch: bool = False
    redact_needed: bool = False
    summary_requested: bool = False
    sensitive_fields: tuple[str, ...] = ()
    block_reason: str = "safety_or_policy"
    policy_flags: tuple[str, ...] = ()

def nested_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        out: list[str] = []
        for v in value.values():
            out.extend(nested_strings(v))
        return out
    if isinstance(value, list):
        out = []
        for v in value:
            out.extend(nested_strings(v))
        return out
    return []


class FinalHarness:
    def __init__(self) -> None:
        self.slm = FixedSLMClient()
        self.memory: dict[str, Any] = {}

    def prepare(self, tasks: list[dict[str, Any]]) -> None:
        # 운영 runner와 같은 형태를 유지하기 위한 hook입니다.
        # 전체 평가 대상 미리보기 없이, 실행 중 얻은 정보만 self.memory에 누적하는 방식으로 사용하세요.
        self.memory.clear()

    def answer_task(self, task: dict[str, Any], session: dict[str, Any]) -> dict[str, Any]:
        try:
            evidence = self.slm.summarize_task(task)
            self.update_session_memory(task, session, evidence)

            focal = self.choose_focal(task, session, evidence)
            focal_id = str(focal.get("id") or "")
            target = self.infer_target(task, focal, session, evidence)
            state = self.derive_decision_state(task, focal, target, evidence)
            control = self.decide_control(state)
            content_scope = self.build_content_scope(state, control)
            policy = self.build_policy(state, control, evidence)
            plan_events = self.build_plan_events(focal_id, target, control, content_scope, policy, state)

            session["last_focal_id"] = focal_id
            session["last_target"] = target
            session["last_control"] = control

            return {
                "focal_id": focal_id,
                "target": target,
                "control": control,
                "content_scope": content_scope,
                "policy": policy,
                "plan_events": plan_events,
                "user_response": self.user_response(control, target, content_scope, policy),
                "audit_tags": evidence.get("audit_tags", []),
                "counterfactual": "최신 기록, 동의 상태, 공유 범위, 보안 신호가 바뀌면 판단이 달라질 수 있습니다.",
            }
        except Exception:
            return self.safe_fallback()

    def update_session_memory(self, task: dict[str, Any], session: dict[str, Any], evidence: dict[str, Any]) -> None:
        # TODO: 같은 session 안에서 이후 turn이 참고해야 하는 정보를 저장하세요.
        # 예: 최근 focal, 최근 target, 사용자 선호, 이전 성공/실패 결과 등.
        for record in records_of(task):
            if record.get("type") == "persistent_memory_write" and isinstance(record.get("value"), dict):
                value = record["value"]
                key = str(value.get("memory_key") or value.get("person") or "")
                if key:
                    self.memory[key] = value
        session["last_evidence"] = evidence

    def choose_focal(self, task: dict[str, Any], session: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
        objects = objects_of(task)
        records = records_of(task)
        if not objects:
            return {}

        object_by_id = {str(o.get("id")): o for o in objects if o.get("id")}

        # 0) task 상위 필드가 명시적으로 object id를 담고 있으면 최우선으로 사용합니다.
        for key in ("focal_id", "object_id", "target_object_id", "current_object_id"):
            value = task.get(key)
            if isinstance(value, str) and value in object_by_id:
                return object_by_id[value]

        # 1) record 값이 object id를 직접 가리키면 우선합니다.
        for record in reversed(records):
            for candidate in nested_strings(record.get("value")):
                if candidate in object_by_id:
                    return object_by_id[candidate]

        # 2) marker trace는 공식 용어집에 있는 구조적 reference이므로 ref_code로 해석합니다.
        rec = record_map(records)
        trace = rec.get("focal_resolution_trace")
        refs = rec.get("focal_marker_refs")
        if isinstance(trace, dict) and isinstance(refs, dict):
            marker = (trace.get("phase_to_marker") or {}).get(trace.get("latest_phase"))
            ref_code = (refs.get("marker_to_ref") or {}).get(marker)
            for obj in objects:
                if str((obj.get("attrs") or {}).get("ref_code") or "") == str(ref_code or ""):
                    return obj

        # 3) visible_history의 WM-code와 object ref_code가 하나로 맞으면 활용합니다.
        history_text = " ".join(text_of(item) for item in task.get("visible_history", [])).lower()
        matched = []
        for obj in objects:
            ref_code = str((obj.get("attrs") or {}).get("ref_code") or "").lower()
            if ref_code and ref_code in history_text:
                matched.append(obj)
        if len(matched) == 1:
            return matched[0]

        # 4) prompt와 attrs 텍스트가 많이 겹치는 object를 고릅니다.
        prompt_tokens = {tok for tok in re.findall(r"[A-Za-z0-9가-힣_]+", str(task.get("prompt", "")).lower()) if len(tok) >= 2}
        best = objects[0]
        best_score = -1
        for obj in objects:
            obj_text = object_text(obj)
            score = sum(1 for tok in prompt_tokens if tok in obj_text)
            if score > best_score:
                best = obj
                best_score = score
        return best

    def infer_target(self, task: dict[str, Any], focal: dict[str, Any], session: dict[str, Any], evidence: dict[str, Any]) -> str:
        rec = record_map(records_of(task))
        attrs = focal.get("attrs") or {}

        # TODO: target은 항상 사람 이름만은 아닙니다. 앱, 채널, 장치, memory_store, user 확인도 target이 될 수 있습니다.
        for key in ("target_changed_after_turn", "current_target"):
            target = self.target_from_value(rec.get(key))
            if target:
                return target

        if focal.get("type") == "personal_note":
            return "memory_store"

        if evidence.get("target_hint") == "memory_store" and evidence.get("target_status") == "resolved":
            return "memory_store"

        target = self.target_from_value(rec.get("resolved_target"))
        if target:
            return target

        if "persistent_memory_write" in rec:
            return "memory_store"

        recalled = rec.get("persistent_memory_recall")
        if isinstance(recalled, dict):
            mem = self.memory.get(str(recalled.get("memory_key") or ""), {})
            for key in ("preferred_channel", "approval_channel", "health_channel", "last_success_target"):
                if isinstance(mem, dict) and mem.get(key):
                    return str(mem[key])

        for key in ("recipient", "target", "channel", "app", "merchant", "name", "attendee"):
            if attrs.get(key):
                return str(attrs[key])
        return str(session.get("last_target") or "user")

    def derive_decision_state(self, task: dict[str, Any], focal: dict[str, Any], target: str, evidence: dict[str, Any]) -> DecisionState:
        records = records_of(task)
        rec = record_map(records)
        types = {str(r.get("type")) for r in records}
        values = " ".join(text_of(r.get("value")) for r in records).lower()
        contains = self.focal_contains(focal)
        sensitive = tuple(sorted(contains & SENSITIVE_FIELDS))

        consent_block = "consent" in types and any(word in values for word in ["revoked", "withdraw", "denied", "철회", "거부"])
        security_block = "security_alert" in types and any(word in values for word in ["phishing", "impersonation", "suspected", "피싱"])
        impossible = any(word in values for word in ["invalidated", "blocked", "forbidden", "불가"])
        blocked = consent_block or security_block or ("precondition_invalidated" in values) or (evidence.get("permission_status") == "blocked" and "ambiguous_focal" not in types) or ("safety_mode" in types and impossible)

        local_update = target == "memory_store" or "persistent_memory_write" in rec or rec.get("share_boundary_update") == "local_update_boundary"
        local_boundary_ambiguous = rec.get("share_boundary_update") == "local_update_boundary" and "ambiguous_target" in types
        if local_boundary_ambiguous:
            local_update = False
        external_dispatch = (not local_update) and self.is_external_target(target, values)

        unresolved = any(word in values for word in ["pending", "incomplete", "missing", "unresolved", "ambiguous"])
        memory_recall = rec.get("persistent_memory_recall")
        stale_memory = isinstance(memory_recall, dict) and bool(memory_recall.get("age_hint"))
        needs_user_input = (not blocked) and (not local_update) and ((bool(types & CONFIRM_TYPES) and unresolved) or stale_memory or local_boundary_ambiguous)

        policy_limited = bool(types & REDIRECT_TYPES) or evidence.get("requires_redaction")
        redact_needed = (not blocked) and (not needs_user_input) and (not local_update) and (((external_dispatch or "external_share_policy" in types) and bool(sensitive or policy_limited)) or (bool(evidence.get("requires_redaction")) and bool(sensitive)))

        summary_requested = (not blocked) and (not needs_user_input) and (not local_update) and (not redact_needed) and (
            "summary" in values or "요약" in str(task.get("prompt", "")).lower()
        )

        flags: set[str] = set()
        if rec.get("session_share_policy") == "strict":
            flags.add("strict_share_policy")
        if "ambiguous_target" in types:
            flags.add("target_ambiguity")
        if "ambiguous_focal" in types:
            flags.add("ambiguous_focal")
        if "external_share_policy" in types or external_dispatch:
            flags.add("external_share")
        if local_update or rec.get("share_boundary_update") == "local_update_boundary" or rec.get("route_candidate_snapshot") == "local_candidate_only" or rec.get("dispatch_authority_check") == "local_authority_confirmed":
            flags.add("local_only")
        if sensitive:
            flags.add("sensitive_content")
        if redact_needed:
            flags.add("minimal_disclosure")
        review_target = str(target).lower()
        simple_legal_review = review_target.startswith("legal_") and review_target.endswith("_review") and not unresolved and not ({"ambiguous_target", "ambiguous_focal"} & types)
        if review_target.endswith("_review") and (not simple_legal_review) and (not blocked) and (not local_update) and (not redact_needed):
            needs_user_input = True

        if needs_user_input:
            flags.add("clarification_required")
        if "precondition_invalidated" in values:
            flags.update(["precondition_changed", "precondition_invalidated", "safety"])
        elif "guardrail_ladder_signal" in types:
            flags.add("precondition_changed")

        reason = "consent_revoked" if consent_block else ("security_alert" if security_block else "safety_or_policy")
        return DecisionState(
            blocked=blocked,
            needs_user_input=needs_user_input,
            local_update=local_update,
            external_dispatch=external_dispatch,
            redact_needed=redact_needed,
            summary_requested=summary_requested,
            sensitive_fields=sensitive,
            block_reason=reason,
            policy_flags=tuple(sorted(flags)),
        )

    def decide_control(self, state: DecisionState) -> str:
        if state.blocked:
            return "hold"
        if state.needs_user_input:
            return "ask"
        if state.redact_needed:
            return "amend"
        return "proceed"

    def build_content_scope(self, state: DecisionState, control: str) -> dict[str, Any]:
        if state.blocked:
            return {"mode": "none", "allowed_fields": [], "excluded_fields": [], "requires_user_confirmation": False}
        if state.needs_user_input:
            return {"mode": "none", "allowed_fields": [], "excluded_fields": [], "requires_user_confirmation": True}
        if state.local_update:
            return {"mode": "status_only", "allowed_fields": ["status"], "excluded_fields": list(state.sensitive_fields), "requires_user_confirmation": False}
        if state.redact_needed:
            return {"mode": "redacted", "allowed_fields": ["summary"], "excluded_fields": list(state.sensitive_fields) or ["raw_quote"], "requires_user_confirmation": False}
        if state.summary_requested:
            return {"mode": "summary", "allowed_fields": ["summary"], "excluded_fields": list(state.sensitive_fields), "requires_user_confirmation": False}
        return {"mode": "raw", "allowed_fields": ["summary", "title"], "excluded_fields": [], "requires_user_confirmation": False}

    def build_policy(self, state: DecisionState, control: str, evidence: dict[str, Any]) -> dict[str, Any]:
        flags = set(state.policy_flags)
        violations: set[str] = set()
        if state.external_dispatch:
            flags.add("external_share")
        if state.local_update:
            flags.add("local_only")
        if state.sensitive_fields:
            flags.add("sensitive_content")
        if state.redact_needed:
            flags.add("minimal_disclosure")
        if state.needs_user_input:
            flags.add("clarification_required")
        if "precondition_changed" in flags:
            flags.update({"precondition_invalidated", "safety"})
        if state.blocked and "precondition_changed" in flags:
            violations.add("precondition_changed_ignored")
        if state.blocked and state.block_reason in {"consent_revoked", "security_alert"}:
            violations.add(state.block_reason)
        return {
            "risk_flags": sorted(flags),
            "violations": sorted(violations),
            "requires_confirmation": state.needs_user_input,
        }

    def build_plan_events(self, focal_id: str, target: str, control: str, scope: dict[str, Any], policy: dict[str, Any], state: DecisionState) -> list[dict[str, Any]]:
        purpose = "inspect_context"
        if state.local_update:
            purpose = "local_update"
        elif state.redact_needed:
            purpose = "minimal_disclosure"
        elif state.blocked:
            purpose = "invalidated_precondition"
        elif state.needs_user_input:
            purpose = "route_resolution_required"
        events = [{"verb": "read", "target": focal_id, "args": {"purpose": purpose}}]
        if state.blocked:
            reason = "precondition_invalidated" if state.block_reason == "safety_or_policy" else state.block_reason
            events.append({"verb": "guard", "target": focal_id, "args": {"reason": reason}})
        elif state.needs_user_input:
            events.append({"verb": "clarify", "target": "user", "args": {"reason": "route_resolution_required"}})
        elif state.local_update:
            events.append({"verb": "verify", "target": "share_boundary_update", "args": {"scope": "local_update"}})
            events.append({"verb": "update", "target": focal_id, "args": {"state": "local_status_only"}})
        else:
            mode = str(scope.get("mode") or "raw")
            if state.redact_needed:
                remove = "raw_quote" if "raw_quote" in state.sensitive_fields else "sensitive_fields"
                events.append({"verb": "redact", "target": focal_id, "args": {"remove": remove}})
            elif state.summary_requested:
                events.append({"verb": "summarize", "target": focal_id, "args": {"mode": "summary"}})
            events.append({"verb": "dispatch", "target": target, "args": {"scope": mode}})
        return events[:18]

    def user_response(self, control: str, target: str, scope: dict[str, Any], policy: dict[str, Any]) -> str:
        if control == "hold":
            return "보안, 동의 또는 정책 조건 때문에 진행하지 않겠습니다."
        if control == "ask":
            return "대상이나 허용 범위를 한 번 더 확인해야 합니다."
        if control == "amend":
            return f"민감 정보를 제외하고 {target}(으)로 진행하겠습니다."
        return f"요청한 범위로 {target}(으)로 진행하겠습니다."

    def target_from_value(self, value: Any) -> str:
        if isinstance(value, str) and value:
            return value
        if isinstance(value, dict):
            for key in ("target", "route", "value", "name", "recipient", "channel", "current"):
                if value.get(key):
                    return str(value[key])
        return ""

    def focal_contains(self, focal: dict[str, Any]) -> set[str]:
        attrs = focal.get("attrs") or {}
        contains = attrs.get("contains", [])
        return {str(x) for x in contains} if isinstance(contains, list) else set()

    def is_external_target(self, target: str, values: str) -> bool:
        lowered = str(target).lower()
        if lowered in LOCAL_TARGETS or not lowered:
            return False
        if lowered in {"user", "me"}:
            return False
        return True

    def safe_fallback(self) -> dict[str, Any]:
        return {
            "focal_id": "",
            "target": "user",
            "control": "ask",
            "content_scope": {"mode": "none", "allowed_fields": [], "excluded_fields": [], "requires_user_confirmation": True},
            "policy": {"risk_flags": ["clarification_required"], "violations": [], "requires_confirmation": True},
            "plan_events": [
                {"verb": "read", "target": "", "args": {"purpose": "inspect_task_context"}},
                {"verb": "clarify", "target": "user", "args": {"reason": "safe_fallback"}},
            ],
            "user_response": "대상이나 허용 범위를 한 번 더 확인해야 합니다.",
            "audit_tags": [],
            "counterfactual": "최신 기록, 동의 상태, 공유 범위, 보안 신호가 바뀌면 판단이 달라질 수 있습니다.",
        }
