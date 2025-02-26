// src/layouts/MainLayout.jsx
import React from "react";
import "./layout.css";

function MainLayout({ children }) {
  return (
    <div className="layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="logo">
          <img src="/src/assets/bdeb.png" alt="Logo" />
        </div>
        <nav className="nav">
          <ul>
            <li>
              <img src="/src/assets/home.png" alt="Accueil" className="nav-icon" /> Accueil
            </li>
            <li className="active">
              <img src="/src/assets/messages.png" alt="Messages" className="nav-icon" /> Messages
            </li>
            <li>
              <img src="/src/assets/alerts.png" alt="Alertes" className="nav-icon" /> Alertes
            </li>
            <li>
              <img src="/src/assets/wallpaper.png" alt="Fond d'écran" className="nav-icon" /> Fond d'écran
            </li>
            <li>
              <img src="/src/assets/settings.png" alt="Paramètres" className="nav-icon" /> Paramètres
            </li>
          </ul>
        </nav>
      </aside>

      {/* Main Content */}
      <div className="main-content">
        {children}
      </div>
    </div>
  );
}

export default MainLayout;
