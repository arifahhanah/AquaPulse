import { useEffect, useState } from "react";

export default function Header() {
  return (
    <div style={{
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
      marginBottom: 30
    }}>
      
      {/* LEFT */}
      <div>
        <h3 style={{ color: "#1e5b84", margin: 0 }}>
          Welcome, {localStorage.getItem("userName") || "User"}!
        </h3>
      </div>

      {/* RIGHT */}
      <div style={{ display: "flex", gap: 15, alignItems: "center" }}>
        
        <input
          placeholder="Search..."
          style={{
            padding: 10,
            borderRadius: 20,
            border: "1px solid #ccc",
            width: 200
          }}
        />

        <span style={{ fontSize: 20 }}>🔔</span>
        <span style={{ fontSize: 20 }}>👤</span>

      </div>
    </div>
  );
}