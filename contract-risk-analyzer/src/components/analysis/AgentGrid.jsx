import { BadgeDollarSign, Database, Scale, ShieldCheck } from "lucide-react";
import AgentCard from "./AgentCard";

export default function AgentGrid() { return <div className="grid gap-3 sm:grid-cols-2"><AgentCard icon={Scale} title="Legal review" detail="Identifying obligations and exceptions" done /><AgentCard icon={BadgeDollarSign} title="Commercial review" detail="Checking fees, renewals, and liability" done /><AgentCard icon={ShieldCheck} title="Privacy review" detail="Looking for data and security exposure" done /><AgentCard icon={Database} title="Operations review" detail="Mapping delivery and exit dependencies" done /></div>; }
