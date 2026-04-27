import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid
} from "recharts";

export default function Chart({ data = [] }) {
  return (
    <div
      style={{
        width: "93%",
        height: 300,
        borderRadius: 20,
        background: "#ffffff",
        padding: 20,
        marginTop: 10,
        boxShadow: "0 2px 6px rgba(0,0,0,0.05)",
        border: "1px solid #eee"
      }}
    >
      <b>GRAFIK LEVEL AIR</b>

      <div style={{ width: "100%", height: "80%", marginTop: 10 }}>
        <ResponsiveContainer>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="level" stroke="#1e5b84" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}