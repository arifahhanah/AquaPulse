import { useState, useEffect } from "react";

export default function PumpControl() {
  const [on, setOn] = useState(false);

  // 🔥 ambil status awal dari localStorage
  useEffect(() => {
    const saved = localStorage.getItem("pumpStatus");
    if (saved !== null) {
      setOn(saved === "true");
    }
  }, []);

  // 🔥 sync antar halaman (tanpa reload)
  useEffect(() => {
    const sync = () => {
      const saved = localStorage.getItem("pumpStatus");
      if (saved !== null) {
        setOn(saved === "true");
      }
    };

    window.addEventListener("storage", sync);
    return () => window.removeEventListener("storage", sync);
  }, []);

  const togglePump = () => {
    const newState = !on;
    setOn(newState);
    localStorage.setItem("pumpStatus", newState); // 🔥 simpan global
  };

  return (
    <div style={{
      width: "100%",
      height: "100%",
      borderRadius: 20,
      background: "#fff",
      display: "flex",
      flexDirection: "column",
      justifyContent: "center",
      alignItems: "center"
    }}>
      <b>KONTROL POMPA</b>

      <button
        onClick={togglePump}
        style={{
          marginTop: 10,
          padding: "10px 20px",
          borderRadius: 10,
          border: "none",
          background: on ? "#4caf50" : "#ccc",
          color: "white",
          cursor: "pointer"
        }}
      >
        {on ? "ON" : "OFF"}
      </button>
    </div>
  );
}