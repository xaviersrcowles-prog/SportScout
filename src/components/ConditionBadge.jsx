const LABELS = {
  excellent: "Excellent",
  good: "Good",
  fair: "Fair",
  poor: "Poor",
  unknown: "Condition unknown",
};

export default function ConditionBadge({ condition }) {
  const status = condition?.status || "unknown";

  return (
    <span className={`badge badge-condition-${status}`}>
      {LABELS[status] || "Unknown"}
      {typeof condition?.score === "number" ? ` · ${Math.round(condition.score)}` : ""}
    </span>
  );
}
