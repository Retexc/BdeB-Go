// src/layouts/MainLayout.jsx
import React from "react";
import "./layout.css"; // We'll define styles here

function MainLayout({ children }) {
  return (
    <div className="layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="logo">
          <img src="/your-logo.png" alt="Logo" />
        </div>
        <nav className="nav">
          <ul>
            <li>Accueil</li>
            <li className="active">Messages</li>
            <li>Alertes</li>
            <li>Fond d'écran</li>
            <li>Paramètres</li>
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
