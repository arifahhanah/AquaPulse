import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function UserSetup() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const navigate = useNavigate();

  const handleSubmit = () => {
    console.log("TOMBOL DIKLIK");

    if (!name || !email) {
      alert("Nama dan Email wajib diisi!");
      return;
    }

    localStorage.setItem("userName", name);
    localStorage.setItem("userEmail", email);
    localStorage.setItem("notifActive", "true");

    window.location.href = "/";
  };

  return (
    <div style={{
      height: "100vh",
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      background: "#f5f6fa"
    }}>
      <div style={{
        width: 400,
        background: "#fff",
        padding: 30,
        borderRadius: 24,
        boxShadow: "0 4px 20px rgba(0,0,0,0.08)",
        border: "1px solid #eee"
      }}>
        <h2 style={{ color: "#1e5b84" }}>AquaPulse Setup</h2>

        <input
          placeholder="Nama"
          value={name}
          onChange={(e) => setName(e.target.value)}
          style={{ width: "100%", padding: 10, marginTop: 15 }}
        />

        <input
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          style={{ width: "100%", padding: 10, marginTop: 10 }}
        />

        <button
          onClick={handleSubmit}
          style={{
            marginTop: 20,
            width: "100%",
            padding: 12,
            background: "#1e5b84",
            color: "white",
            border: "none",
            borderRadius: 10
          }}
        >
          Mulai
        </button>
      </div>
    </div>
  );
}