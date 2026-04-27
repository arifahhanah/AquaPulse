import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import Header from "../components/Header";
import HistoryContent from "../components/HistoryContent";

export default function History() {
  const [historyData, setHistoryData] = useState([]);

  useEffect(() => {
    fetch("http://localhost:5001/water-level")
      .then((res) => res.json())
      .then((data) => {
        console.log("HISTORY DATA:", data); // 🔥 DEBUG WAJIB
        setHistoryData(data.history || []);
      })
      .catch((err) => console.error("ERROR FETCH:", err));
  }, []);

  return (
    <div style={{ display: "flex" }}>
      <Sidebar />

      <div style={{ flex: 1, padding: 20, background: "#f5f6fa" }}>
        <Header />

        <h1>History</h1>

        <div style={{ marginTop: 20 }}>
          <HistoryContent data={historyData} />
        </div>
      </div>
    </div>
  );
}