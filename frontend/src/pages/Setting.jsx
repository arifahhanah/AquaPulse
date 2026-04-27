import { useState, useEffect } from "react";
import Sidebar from "../components/Sidebar";
import Header from "../components/Header";

export default function Setting() {
  const [warning, setWarning] = useState(50);
  const [danger, setDanger] = useState(80);
  const [notifActive, setNotifActive] = useState(true);

  // load dari localStorage
  useEffect(() => {
    const w = localStorage.getItem("warning");
    const d = localStorage.getItem("danger");
    const n = localStorage.getItem("notifActive");

    if (w) setWarning(Number(w));
    if (d) setDanger(Number(d));
    if (n !== null) setNotifActive(n === "true");
    else setNotifActive(true);
  }, []);

  // simpan ke localStorage
  const saveSetting = () => {
    // 🔥 validasi
    if (danger <= warning) {
      alert("Batas DANGER harus lebih besar dari WARNING");
      return;
    }

    localStorage.setItem("warning", warning);
    localStorage.setItem("danger", danger);
    localStorage.setItem("notifActive", notifActive);

    alert("Setting berhasil disimpan!");
  };

  return (
    <div style={{ display: "flex" }}>
      <Sidebar />

      <div style={{ flex: 1, padding: 20, background: "#f5f6fa" }}>
        <Header />

        <h1>Setting</h1>

        {/* CARD */}
        <div
          style={{
            marginTop: 20,
            maxWidth: 500,
            background: "#fff",
            padding: 20,
            borderRadius: 24,
            boxShadow: "0 4px 12px rgba(0,0,0,0.06)",
            border: "1px solid #eee"
          }}
        >
          <h3>Pengaturan Batas Ketinggian Air</h3>

          {/* WARNING */}
          <div style={{ marginTop: 20 }}>
            <label>Batas WARNING ({warning} %)</label>

            <input
              type="range"
              min="0"
              max="100"
              value={warning}
              onChange={(e) => setWarning(Number(e.target.value))}
              style={{ width: "100%" }}
            />

            <input
              type="number"
              min="0"
              max="100"
              value={warning}
              onChange={(e) => setWarning(Number(e.target.value))}
              style={{
                width: "100%",
                padding: 8,
                borderRadius: 10,
                border: "1px solid #ccc",
                marginTop: 5
              }}
            />
          </div>

          {/* DANGER */}
          <div style={{ marginTop: 20 }}>
            <label>Batas DANGER ({danger} %)</label>

            <input
              type="range"
              min="0"
              max="100"
              value={danger}
              onChange={(e) => setDanger(Number(e.target.value))}
              style={{ width: "100%" }}
            />

            <input
              type="number"
              min="0"
              max="100"
              value={danger}
              onChange={(e) => setDanger(Number(e.target.value))}
              style={{
                width: "100%",
                padding: 8,
                borderRadius: 10,
                border: "1px solid #ccc",
                marginTop: 5
              }}
            />
          </div>

          {/* NOTIFICATION */}
          <div style={{ marginTop: 20 }}>
            <label style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <input
                type="checkbox"
                checked={notifActive}
                onChange={(e) => setNotifActive(e.target.checked)}
              />
              Aktifkan Notifikasi
            </label>
          </div>

          {/* BUTTON */}
          <button
            onClick={saveSetting}
            style={{
              marginTop: 20,
              width: "100%",
              padding: 12,
              borderRadius: 12,
              border: "none",
              background: "#1e5b84",
              color: "white",
              fontWeight: "bold",
              cursor: "pointer"
            }}
          >
            Simpan Setting
          </button>
        </div>
      </div>
    </div>
  );
}