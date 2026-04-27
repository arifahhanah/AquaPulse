import { useEffect, useState } from "react";

export default function StatusCard({ title, value = 0 }) {
  const [warning, setWarning] = useState(50);
  const [danger, setDanger] = useState(80);

  // ambil dari localStorage
  useEffect(() => {
    const w = localStorage.getItem("warning");
    const d = localStorage.getItem("danger");

    if (w) setWarning(Number(w));
    if (d) setDanger(Number(d));
  }, []);

  let status = "NORMAL";
  let color = "#4caf50";

  if (value >= danger) {
    status = "DANGER";
    color = "#e53935";
  } else if (value >= warning) {
    status = "WARNING";
    color = "#fb8c00";
  }

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        borderRadius: 20,
        background: "#fff",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        gap: 6,
        boxShadow: "0 4px 12px rgba(0,0,0,0.06)",
        border: "1px solid #eee"
      }}
    >
      <b style={{ margin: 0 }}>{title}</b>

      <h2 style={{ margin: 0 }}>{value} cm</h2>

      <span style={{ margin: 0, color }}>{status}</span>
    </div>
  );
}