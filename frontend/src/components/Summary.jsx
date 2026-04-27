export default function Summary({ waterLevel }) {
  let text = "Ketinggian air stabil";
  let recommendation = "Pompa standby";

  if (waterLevel > 80) {
    text = "Air sangat tinggi";
    recommendation = "Matikan Pompa";
  } else if (waterLevel > 50) {
    text = "Air mulai naik";
    recommendation = "Monitor kondisi";
  } else {
    text = "Air stabil";
    recommendation = "Nyalakan Pompa";
  }

  return (
    <div
      style={{
        width: "93%",
        minHeight: 100,
        borderRadius: 20,
        background: "#ffffff",
        padding: 20,
        boxShadow: "0 2px 6px rgba(0,0,0,0.05)",
        border: "1px solid #eee",
        marginBottom: 10
      }}
    >
      <b>SUMMARY DAN REQ</b>

      <p style={{ marginTop: 10 }}>{text}</p>

      <b>Rekomendasi: {recommendation}</b>
    </div>
  );
}