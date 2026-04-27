import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import Header from "../components/Header";

export default function Insight() {
  const [historyData, setHistoryData] = useState([]);

  console.log("HISTORY:", historyData);

  useEffect(() => {
    fetch("http://localhost:5001/water-level")
      .then((res) => res.json())
      .then((data) => {
        setHistoryData(data.history || []);
      })
      .catch((err) => console.error(err));
  }, []);

  // ===============================
  // 🔥 HITUNG INSIGHT
  // ===============================

  // 🔹 TREND
  let trend = "Stabil";
  if (historyData.length >= 2) {
    const last = historyData[historyData.length - 1].level;
    const prev = historyData[historyData.length - 2].level;

    if (last > prev) trend = "Naik";
    else if (last < prev) trend = "Turun";
  }

  // 🔹 TOTAL WARNING & DANGER
  const warningLimit = Number(localStorage.getItem("warning")) || 50;
  const dangerLimit = Number(localStorage.getItem("danger")) || 80;

  let warningCount = 0;
  let dangerCount = 0;

  historyData.forEach((item) => {
    if (item.level >= dangerLimit) dangerCount++;
    else if (item.level >= warningLimit) warningCount++;
  });

  // 🔹 RATA-RATA
  let avg = 0;
  if (historyData.length > 0) {
    const total = historyData.reduce((sum, item) => sum + item.level, 0);
    avg = (total / historyData.length).toFixed(1);
  }

  return (
    <div style={{ display: "flex" }}>
      <Sidebar />

      <div style={{ flex: 1, padding: 20, background: "#f5f6fa" }}>
        <Header />

        <h1>Insight Page</h1>

        {/* =============================== */}
        {/* 🔥 GRID INSIGHT */}
        {/* =============================== */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr 1fr",
            gap: 20,
            marginTop: 20
          }}
        >
          {/* 🔹 TREND */}
          <div style={cardStyle}>
            <h3>Trend</h3>
            <h2
              style={{
                color:
                  trend === "Naik"
                    ? "#4caf50"
                    : trend === "Turun"
                    ? "#e53935"
                    : "#999"
              }}
            >
              {trend}
            </h2>
            <p style={{ color: "#777" }}>Perubahan terakhir</p>
          </div>

          {/* 🔹 TOTAL ALARM */}
          <div style={cardStyle}>
            <h3>Total Alarm</h3>

            <div style={{ marginTop: 10 }}>
              <p style={{ color: "#fb8c00", margin: 0 }}>
                Warning: {warningCount}
              </p>
              <p style={{ color: "#e53935", margin: 0 }}>
                Danger: {dangerCount}
              </p>
            </div>
          </div>

          {/* 🔹 RATA-RATA */}
          <div style={cardStyle}>
            <h3>Rata-rata</h3>
            <h2>{avg} cm</h2>
            <p style={{ color: "#777" }}>
              Dari {historyData.length} data terakhir
            </p>
          </div>
        </div>

        {/* =============================== */}
        {/* 🔥 INSIGHT TAMBAHAN (OPTIONAL UI) */}
        {/* =============================== */}
        <div style={{ ...cardStyle, marginTop: 20 }}>
          <h3>Kesimpulan</h3>

          {trend === "Naik" && (
            <p>Air sedang meningkat, perlu waspada.</p>
          )}

          {trend === "Turun" && (
            <p>Air menurun, kondisi mulai aman.</p>
          )}

          {trend === "Stabil" && (
            <p>Kondisi air stabil.</p>
          )}
        </div>
      </div>
    </div>
  );
}

// ===============================
// 🎨 STYLE (BIAR CONSISTENT)
// ===============================
const cardStyle = {
  background: "#fff",
  borderRadius: 20,
  padding: 20,
  boxShadow: "0 4px 12px rgba(0,0,0,0.06)",
  border: "1px solid #eee"
};