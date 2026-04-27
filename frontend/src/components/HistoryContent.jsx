export default function HistoryContent({ data = [] }) {
  return (
    <div
      style={{
        width: "93%",
        height: "100%",
        borderRadius: 20,
        background: "#ffffff",
        padding: 20,
        display: "flex",
        flexDirection: "column"
      }}
    >
      <b style={{ marginBottom: 15 }}>RIWAYAT DATA</b>

      <div style={{ overflowY: "auto", flex: 1 }}>
        <table width="100%" style={{ borderCollapse: "collapse" }}>
          <thead>
            <tr>
              <th align="left">Date & Time</th>
              <th align="left">Status</th>
              <th align="left">Perubahan</th>
            </tr>
          </thead>

          <tbody>
            {data.map((item, i) => (
              <tr key={i}>
                <td>{item.time}</td>

                <td
                  style={{
                    color: item.status === "Naik" ? "green" : "red"
                  }}
                >
                  {item.status}
                </td>

                <td
                  style={{
                    color: item.change.includes("+") ? "green" : "red"
                  }}
                >
                  {item.change}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}