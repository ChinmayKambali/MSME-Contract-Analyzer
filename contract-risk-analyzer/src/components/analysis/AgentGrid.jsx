import { BadgeDollarSign, Database, Scale, ShieldCheck } from "lucide-react";
import AgentCard from "./AgentCard";

export default function AgentGrid({ agentStates = {}, isFailed = false }) {
  const isLegalDone = agentStates.dispute_resolution === "done";
  const isLegalFailed = agentStates.dispute_resolution === "failed";
  const legalState = isLegalDone ? "done" : (isFailed || isLegalFailed ? "failed" : "working");

  const isCommercialDone = agentStates.payment_terms === "done" && agentStates.penalty_ld === "done";
  const isCommercialFailed = agentStates.payment_terms === "failed" || agentStates.penalty_ld === "failed";
  const commercialState = isCommercialDone ? "done" : (isFailed || isCommercialFailed ? "failed" : "working");

  const isPrivacyDone = agentStates.ip_ownership === "done";
  const isPrivacyFailed = agentStates.ip_ownership === "failed";
  const privacyState = isPrivacyDone ? "done" : (isFailed || isPrivacyFailed ? "failed" : "working");

  const isOpsDone = agentStates.termination === "done" && agentStates.liability === "done";
  const isOpsFailed = agentStates.termination === "failed" || agentStates.liability === "failed";
  const opsState = isOpsDone ? "done" : (isFailed || isOpsFailed ? "failed" : "working");

  return (
    <div className="grid gap-3 sm:grid-cols-2">
      <AgentCard
        icon={Scale}
        title="Legal review"
        detail="Identifying obligations and dispute terms"
        state={legalState}
      />
      <AgentCard
        icon={BadgeDollarSign}
        title="Commercial review"
        detail="Checking payment credit terms and penalties"
        state={commercialState}
      />
      <AgentCard
        icon={ShieldCheck}
        title="Privacy review"
        detail="Looking for data and IP ownership exposure"
        state={privacyState}
      />
      <AgentCard
        icon={Database}
        title="Operations review"
        detail="Mapping liability and termination dependencies"
        state={opsState}
      />
    </div>
  );
}
