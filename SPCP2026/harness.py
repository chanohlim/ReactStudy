from __future__ import annotations

import json
import re
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

        return {
            "risk_flags": sorted(flags),
            "requires_redaction": any(k in text for k in ["raw_sensitive_forbidden", "raw_quote_forbidden", "doctor_note_forbidden", "numeric_value_forbidden", "no_location", "원문"]),
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
            control = self.decide_control(task, focal, target, evidence)
            content_scope = self.build_content_scope(task, focal, control, evidence)
            policy = self.build_policy(task, focal, control, evidence)
            plan_events = self.build_plan_events(task, focal_id, target, control, content_scope, policy)

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
        for key in ("current_target", "resolved_target", "target_changed_after_turn"):
            target = self.target_from_value(rec.get(key))
            if target:
                return target

        if "persistent_memory_write" in rec:
            return "memory_store"

        recalled = rec.get("persistent_memory_recall")
        if isinstance(recalled, dict):
            mem = self.memory.get(str(recalled.get("memory_key") or ""), {})
            for key in ("approval_channel", "preferred_channel", "health_channel", "last_success_target"):
                if isinstance(mem, dict) and mem.get(key):
                    return str(mem[key])

        for key in ("recipient", "target", "channel", "app", "merchant", "name", "attendee"):
            if attrs.get(key):
                return str(attrs[key])
        return str(session.get("last_target") or "user")

    def decide_control(self, task: dict[str, Any], focal: dict[str, Any], target: str, evidence: dict[str, Any]) -> str:
        records = records_of(task)
        rec = record_map(records)
        types = {str(r.get("type")) for r in records}
        values = " ".join(text_of(r.get("value")) for r in records).lower()
        flags = set(evidence.get("risk_flags", []))
        contains = self.focal_contains(focal)

        # TODO: 단일 record label만 보지 말고 prompt, focal object, session 상태를 함께 보강하세요.
        if types & BLOCK_TYPES or "phishing" in flags or any(word in values for word in ["revoked", "withdraw", "denied", "철회", "거부", "impersonation"]):
            return "hold"
        if "persistent_memory_write" in rec or target == "memory_store":
            return "proceed"
        if evidence.get("requires_confirmation") or any(t in types for t in CONFIRM_TYPES):
            return "ask"
        if evidence.get("requires_redaction") or any(t in types for t in REDIRECT_TYPES):
            return "amend"
        if contains & SENSITIVE_FIELDS and self.is_external_target(target, values):
            return "amend"
        return "proceed"

    def build_content_scope(self, task: dict[str, Any], focal: dict[str, Any], control: str, evidence: dict[str, Any]) -> dict[str, Any]:
        contains = self.focal_contains(focal)
        sensitive = sorted(contains & SENSITIVE_FIELDS)
        prompt_and_records = (str(task.get("prompt", "")) + " " + " ".join(text_of(r.get("value")) for r in records_of(task))).lower()

        if control == "hold":
            return {"mode": "none", "allowed_fields": [], "excluded_fields": [], "requires_user_confirmation": False}
        if control == "ask":
            return {"mode": "none", "allowed_fields": [], "excluded_fields": [], "requires_user_confirmation": True}
        if control == "amend" or evidence.get("requires_redaction"):
            excluded = sensitive or ["raw_quote"]
            return {"mode": "redacted", "allowed_fields": ["summary", "title", "status"], "excluded_fields": excluded, "requires_user_confirmation": False}
        if "persistent_memory_write" in record_map(records_of(task)) or self.infer_target(task, focal, {}, evidence) == "memory_store":
            return {"mode": "status_only", "allowed_fields": ["status"], "excluded_fields": sorted(sensitive), "requires_user_confirmation": False}
        if "summary" in prompt_and_records or "요약" in prompt_and_records:
            return {"mode": "summary", "allowed_fields": ["summary", "title", "status"], "excluded_fields": sorted(sensitive), "requires_user_confirmation": False}
        return {"mode": "raw", "allowed_fields": ["raw"], "excluded_fields": [], "requires_user_confirmation": False}

    def build_policy(self, task: dict[str, Any], focal: dict[str, Any], control: str, evidence: dict[str, Any]) -> dict[str, Any]:
        flags = set(evidence.get("risk_flags", []))
        violations: set[str] = set()
        values = " ".join(text_of(r.get("value")) for r in records_of(task)).lower()
        contains = self.focal_contains(focal)
        target = self.infer_target(task, focal, {}, evidence)
        if self.is_external_target(target, values):
            flags.add("external_share")
        if target == "memory_store" or "persistent_memory_write" in record_map(records_of(task)):
            flags.add("local_only")
        if contains & SENSITIVE_FIELDS:
            flags.add("sensitive_content")
        if control == "amend":
            flags.add("minimal_disclosure")
        if control == "ask":
            flags.add("clarification_required")
        if "revoked" in values or "철회" in values:
            violations.add("consent_revoked")
        if "phishing" in values or "피싱" in values or "impersonation" in values:
            violations.add("security_alert_ignored")
        return {
            "risk_flags": sorted(flags),
            "violations": sorted(violations),
            "requires_confirmation": control == "ask",
        }

    def build_plan_events(self, task: dict[str, Any], focal_id: str, target: str, control: str, scope: dict[str, Any], policy: dict[str, Any]) -> list[dict[str, Any]]:
        events = [{"verb": "read", "target": focal_id, "args": {"purpose": "inspect_task_context"}}]
        mode = scope.get("mode")
        if control == "hold":
            reason = policy.get("violations", ["safety_or_policy"])[0] if policy.get("violations") else "safety_or_policy"
            events.append({"verb": "guard", "target": focal_id, "args": {"reason": reason}})
        elif control == "ask":
            events.append({"verb": "clarify", "target": "user", "args": {"reason": "confirmation_required"}})
        elif mode == "status_only" or target == "memory_store":
            events.append({"verb": "verify", "target": "share_boundary_update", "args": {"scope": "local_update"}})
            events.append({"verb": "update", "target": focal_id, "args": {"state": "local_status_only"}})
        else:
            if mode == "redacted":
                events.append({"verb": "redact", "target": focal_id, "args": {"remove": "sensitive_fields"}})
            elif mode == "summary":
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
        if "external" in values or "외부" in values or "vendor" in values or "vendor" in lowered:
            return True
        if any(word in lowered for word in INTERNAL_WORDS):
            return False
        return lowered not in {"user", "me"}

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
