import { BrowserRouter, Routes, Route } from "react-router-dom";

import Dashboard from "./pages/Dashboard";
import History from "./pages/History";
import Insight from "./pages/Insight";
import Control from "./pages/Control";
import Setting from "./pages/Setting";
import UserSetup from "./components/UserSetup";

export default function MainApp() {
  const name = localStorage.getItem("userName");

  return (
    <BrowserRouter>
      <Routes>
        {!name ? (
          <Route path="*" element={<UserSetup />} />
        ) : (
          <>
            <Route path="/" element={<Dashboard />} />
            <Route path="/history" element={<History />} />
            <Route path="/insight" element={<Insight />} />
            <Route path="/control" element={<Control />} />
            <Route path="/setting" element={<Setting />} />
          </>
        )}
      </Routes>
    </BrowserRouter>
  );
}