export default function Toast({ message, type }) {
  const bg =
    type === "danger"
      ? "#e53935"
      : type === "warning"
      ? "#fb8c00"
      : "#4caf50";

  return (
    <div
      style={{
        position: "fixed",
        top: 20,
        right: 20,
        background: bg,
        color: "white",
        padding: "12px 18px",
        borderRadius: 12,
        boxShadow: "0 4px 12px rgba(0,0,0,0.2)",
        fontWeight: "bold",
        zIndex: 9999
      }}
    >
      {message}
    </div>
  );
}