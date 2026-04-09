import aiDashboardData from "@/data/ai-dashboard-data.json";
import { AiDashboard } from "@/components/dashboard/ai-dashboard";
import type { AiDashboardData } from "@/types/dashboard";

const aiData = aiDashboardData as AiDashboardData;

export default function AiPage() {
  return <AiDashboard data={aiData} />;
}
