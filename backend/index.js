const express = require("express");
const cors = require("cors");
const mysql = require("mysql2/promise"); // ✅ pakai promise version

const app = express();

app.use(cors());
app.use(express.json());

// ✅ BUAT CONNECTION POOL (STABIL)
const db = mysql.createPool({
  host: "localhost",
  user: "root",
  password: "",
  database: "water_monitor",
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0,
});

// TEST DB
(async () => {
  try {
    const conn = await db.getConnection();
    console.log("MySQL Connected ✅");
    conn.release();
  } catch (err) {
    console.error("DB Error:", err);
  }
})();

// TEST ROUTE
app.get("/", (req, res) => {
  res.send("API Running 🚀");
});

// ==========================
// 📡 POST DATA DARI IOT
// ==========================
app.post("/api/water-level", async (req, res) => {
  const { level } = req.body;

  if (level === undefined) {
    return res.status(400).json({ message: "Level is required" });
  }

  try {
    await db.query("INSERT INTO water_levels (level) VALUES (?)", [level]);
    res.json({ message: "Data saved ✅" });
  } catch (err) {
    console.error("POST ERROR:", err);
    res.status(500).json({ message: "DB Error" });
  }
});

// ==========================
// 📊 GET DATA UNTUK DASHBOARD
// ==========================
app.get("/api/water-level", async (req, res) => {
  try {
    const [rows] = await db.query(
      "SELECT * FROM water_levels ORDER BY created_at DESC LIMIT 20"
    );

    res.json(rows);
  } catch (err) {
    console.error("GET ERROR:", err);
    res.status(500).send(err.message);
  }
});

// START SERVER
app.listen(5001, () => {
  console.log("Server running on http://localhost:5001");
});