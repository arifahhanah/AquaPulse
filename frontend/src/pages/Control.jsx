import Sidebar from "../components/Sidebar";
import Header from "../components/Header";
import PumpControl from "../components/PumpControl";

export default function Control() {
  return (
    <div style={{ display: "flex" }}>
      <Sidebar />

      <div style={{ flex: 1, padding: 20, background: "#f5f6fa" }}>
        <Header />

        <h1>Control Page</h1>

        {/* 🔥 TAMBAH INI */}
        <div style={{ marginTop: 20, maxWidth: 300 }}>
          <PumpControl />
        </div>
      </div>
    </div>
  );
}