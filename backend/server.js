console.log("🔥 SERVER INI YANG DIPAKAI");

import express from "express";
import axios from "axios";
import dotenv from "dotenv";
import cors from "cors";
import nodemailer from "nodemailer";
import mysql from "mysql2/promise";

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

// ================================
// ✅ CONFIG
// ================================
const PORT = process.env.PORT || 5001;
const ML_URL = process.env.ML_SERVICE_URL;

// ================================
// ✅ DATABASE
// ================================
const db = mysql.createPool({
  host: "localhost",
  user: "root",
  password: "",
  database: "water_levels",
});

// 🔥 TEST DB CONNECTION
(async () => {
  try {
    const conn = await db.getConnection();
    console.log("✅ MySQL Connected");
    conn.release();
  } catch (err) {
    console.error("❌ DB ERROR:", err);
  }
})();

// ================================
// 🔥 DEBUG ENV
// ================================
console.log("EMAIL_USER:", process.env.EMAIL_USER);
console.log("EMAIL_PASS:", process.env.EMAIL_PASS);

// ================================
// 🔥 IOT ENDPOINT (SUDAH TERHUBUNG ML)
// ================================
app.post("/api/iot", async (req, res) => {
  try {
    const { water_level, distance, water_raw, status, timestamp } = req.body;

    // 🔥 VALIDASI
    if (
      water_level === undefined ||
      distance === undefined ||
      water_raw === undefined ||
      !status ||
      !timestamp
    ) {
      return res.status(400).json({ error: "Payload tidak lengkap" });
    }

    console.log("📡 DATA IOT MASUK:", water_level, distance, water_raw, status);
    console.log("🔥 MAU KIRIM KE ML:", ML_URL);

    let mlData = {};

    try {
      // 🔥 ambil data histori dari DB
      const [rows] = await db.query(
        "SELECT * FROM water_levels ORDER BY timestamp DESC LIMIT 20"
      );

      const readings = rows.map(r => ({
        timestamp: r.timestamp,
        water_level: r.water_level,
        distance: r.distance,
        water_raw: r.water_raw,
        status: r.status
      }));

      // 🔥 kirim ke ML (endpoint "/")
      const response = await axios.post(`${ML_URL}/insight/`, {
        period: "realtime",
        readings: readings,
        date: timestamp
      });

      mlData = response.data;

      console.log("🤖 ML RESULT:", mlData);

    } catch (err) {
      console.error("❌ ML ERROR FULL:", err);
    }

    // =========================
    // 💾 SIMPAN KE DATABASE
    // =========================
    await db.query(
      `INSERT INTO water_levels 
       (timestamp, water_level, distance, water_raw, status,
        trend, warning, danger, water_level_change, avg_height,
        cm_to_overflow, estimated_overflow, summary, recommendation)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [
        timestamp,
        water_level,
        distance,
        water_raw,
        status,

        mlData.trend || null,
        mlData.warning || null,
        mlData.danger || null,
        mlData.water_level_change || null,
        mlData.avg_height || null,
        mlData.cm_to_overflow || null,
        mlData.estimated_overflow || null,
        mlData.summary || null,
        mlData.recommendation || null
      ]
    );

    res.json({
      message: "OK",
      ml: mlData
    });

  } catch (error) {
    console.error("❌ DB ERROR:", error);
    res.status(500).json({ error: "Gagal simpan data" });
  }
});

// ================================
// 📊 GET DATA UNTUK FRONTEND
// ================================
app.get("/api/data", async (req, res) => {
  try {
    const [rows] = await db.query(
      "SELECT * FROM water_levels ORDER BY timestamp DESC LIMIT 20"
    );

    res.json(rows);

  } catch (error) {
    console.error("❌ GET DATA ERROR:", error);
    res.status(500).json({ error: "Gagal ambil data" });
  }
});

// ================================
// 🤖 ML SERVICE (manual test)
/// ================================
app.get("/api/predict", async (req, res) => {
  try {
    const level = req.query.level || 120;

    const response = await axios.post(`${ML_URL}/predict`, { level });

    res.json({
      level,
      ...response.data
    });

  } catch (error) {
    console.error("❌ ML ERROR:", error.message);
    res.status(500).json({ error: "Gagal ambil data dari ML" });
  }
});

// ================================
// 📧 EMAIL NOTIFICATION
// ================================
app.post("/send-email", async (req, res) => {
  const { email, level } = req.body;

  if (!email || !level) {
    return res.status(400).json({ error: "Email atau level kosong" });
  }

  try {
    const transporter = nodemailer.createTransport({
      service: "gmail",
      auth: {
        user: process.env.EMAIL_USER,
        pass: process.env.EMAIL_PASS
      }
    });

    const info = await transporter.sendMail({
      from: `"AquaPulse" <${process.env.EMAIL_USER}>`,
      to: email,
      subject: "🚨 DANGER AIR",
      text: `Ketinggian air mencapai ${level} cm`
    });

    console.log("✅ EMAIL SUCCESS:", info.response);

    res.json({ success: true });

  } catch (err) {
    console.error("❌ EMAIL ERROR:", err.message);
    res.status(500).json({ error: "Gagal kirim email" });
  }
});

// ================================
// 🚀 START SERVER
// ================================
app.listen(PORT, () => {
  console.log(`🚀 Server running on http://localhost:${5001}`);
});