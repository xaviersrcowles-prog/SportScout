const LABELS = {
  public: "Public",
  restricted: "Restricted",
  members_only: "Members only",
  private: "Private",
  unknown: "Access unknown",
};

export default function AccessBadge({ access }) {
  const classification = access?.classification || "unknown";
  const confidence = access?.confidence;

  return (
    <span className={`badge badge-access-${classification}`} title={access?.evidence || ""}>
      {LABELS[classification] || "Unknown"}
      {typeof confidence === "number" && confidence > 0 ? ` · ${Math.round(confidence * 100)}%` : ""}
    </span>
  );
}
