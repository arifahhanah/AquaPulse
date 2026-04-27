import { Link, useLocation } from "react-router-dom";

export default function Sidebar() {
  const location = useLocation();

  const menus = [
    { name: "Dashboard", path: "/" },
    { name: "History", path: "/history" },
    { name: "Insight", path: "/insight" },
    { name: "Control", path: "/control" },
    { name: "Setting", path: "/setting" },
  ];

  return (
    <div style={{
      width: 160,
      height: "100vh",
      backgroundColor: "#1e5b84",
      color: "white",
      padding: "20px 15px"
    }}>
      <h2 style={{ marginBottom: 30 }}>AquaPulse.</h2>

      {menus.map((item, i) => {
        const isActive = location.pathname === item.path;

        return (
          <Link
            key={i}
            to={item.path}
            style={{
              display: "block",
              padding: "12px",
              borderRadius: 10,
              marginBottom: 10,
              textDecoration: "none",
              background: isActive ? "white" : "transparent",
              color: isActive ? "#1e5b84" : "white",
              fontWeight: isActive ? "bold" : "normal"
            }}
          >
            {item.name}
          </Link>
        );
      })}
    </div>
  );
}