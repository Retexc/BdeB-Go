// src/pages/BackgroundPage.jsx
import React from "react";
import "./BackgroundPage.css";

function BackgroundPage() {
  return (
    <div className="background-page">
      {/* Header container (similar to MessagesPage) */}
      <div className="header">
        <div className="Title">
          <h1>Fond d'écran</h1>
          <p>Modifier l'arrière-plan du tableau d'affichage</p>
        </div>
        <button className="add-btn">Importer une image</button>
      </div>

      {/* THEME SECTION */}
      <div className="theme-section">
        <h2>Thème</h2>
        <p>
          Modifier le thème de l'application entre noir et blanc. Vous pouvez
          aussi appliquer d'autres thèmes créés par le Collège.
        </p>
        <div className="theme-options">
          {/* Example: Two theme "cards" or buttons */}
          <div className="theme-card dark-theme">
            <span>Thème sombre</span>
          </div>
          <div className="theme-card light-theme">
            <span>Thème clair</span>
          </div>
        </div>
      </div>

      {/* RECENT IMAGES SECTION */}
      <div className="recent-images">
        <h2>Images récentes</h2>
        <div className="images-grid">
          {/* Example placeholders: repeat as needed */}
          <div className="image-card">
            <img src="/static/assets/images/example1.png" alt="Example 1" />
          </div>
          <div className="image-card">
            <img src="/static/assets/images/example2.png" alt="Example 2" />
          </div>
          <div className="image-card">
            <img src="/static/assets/images/example3.png" alt="Example 3" />
          </div>
          <div className="image-card">
            <img src="/static/assets/images/example4.png" alt="Example 4" />
          </div>
        </div>
      </div>
    </div>
  );
}

export default BackgroundPage;
