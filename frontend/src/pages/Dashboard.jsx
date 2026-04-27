import { useEffect, useState, useRef } from "react";

import Sidebar from "../components/Sidebar";
import Header from "../components/Header";
import StatusCard from "../components/StatusCard";
import PumpControl from "../components/PumpControl";
import HistoryContent from "../components/HistoryContent";
import Summary from "../components/Summary";
import Chart from "../components/Chart";
import Toast from "../components/Toast";

export default function Dashboard() {
  const [waterLevel, setWaterLevel] = useState(0);
  const [historyData, setHistoryData] = useState([]);
  const lastStatus = useRef("");
  const [toast, setToast] = useState(null);

  // 🔥 FIX: ambil dari /api/data + mapping
  useEffect(() => {
    const fetchData = () => {
      fetch("http://localhost:5001/api/data")
        .then((res) => res.json())
        .then((data) => {

          if (!data || data.length === 0) return;

          // ambil data terbaru
          const latest = data[0];

          setWaterLevel(latest.water_level || 0);

          // 🔥 mapping ke format lama (biar komponen kamu tidak berubah)
          const mapped = data.map((item, i) => {
            const prev = data[i + 1];
            const change = prev
              ? item.water_level - prev.water_level
              : 0;

            return {
              time: item.timestamp,
              level: item.water_level,
              status: change >= 0 ? "Naik" : "Turun",
              change: change >= 0 ? `+${change}` : `${change}`
            };
          });

          setHistoryData(mapped);
        })
        .catch((err) => console.error(err));
    };

    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  // 🔥 NOTIFICATION (TIDAK DIUBAH)
  useEffect(() => {
    const notifActive = localStorage.getItem("notifActive") === "true";
    const warning = Number(localStorage.getItem("warning")) || 50;
    const danger = Number(localStorage.getItem("danger")) || 80;
    const email = localStorage.getItem("userEmail");

    if (!notifActive) return;

    let status = "NORMAL";

    if (waterLevel >= danger) status = "DANGER";
    else if (waterLevel >= warning) status = "WARNING";

    if (lastStatus.current === "") {
      lastStatus.current = status;

      if (status !== "NORMAL") {
        triggerNotification(status);
      }
      return;
    }

    if (lastStatus.current !== status) {
      lastStatus.current = status;
      triggerNotification(status);
    }

    function triggerNotification(currentStatus) {
      if (currentStatus === "DANGER") {
        setToast({
          message: "🚨 Air dalam kondisi DANGER!",
          type: "danger"
        });

        if (email) {
          fetch("http://localhost:5001/send-email", {
            method: "POST",
            headers: {
              "Content-Type": "application/json"
            },
            body: JSON.stringify({
              email,
              level: waterLevel
            })
          }).catch((err) => console.error(err));
        }
      }

      if (currentStatus === "WARNING") {
        setToast({
          message: "⚠️ Air mulai naik (WARNING)",
          type: "warning"
        });
      }

      setTimeout(() => setToast(null), 3000);
    }
  }, [waterLevel]);

  return (
    <div style={{ display: "flex" }}>
      <Sidebar />

      <div style={{ flex: 1, padding: 20, background: "#f5f6fa" }}>
        <Header />

        <h1>Dashboard</h1>

    

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: 20,
            marginTop: 20
          }}
        >
          <div
            style={{
              display: "grid",
              gridTemplateRows: "auto auto auto",
              gap: 20
            }}
          >
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: 20
              }}
            >
              <StatusCard title="STATUS ALARM" value={waterLevel} />
              <PumpControl />
            </div>

            <Summary waterLevel={waterLevel} />
            <Chart data={historyData} />
          </div>

          <div style={{ height: "93%" }}>
            <HistoryContent data={historyData} />
          </div>
        </div>

        {toast && <Toast message={toast.message} type={toast.type} />}
      </div>
    </div>
  );
}