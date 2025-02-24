// src/components/MessageCard.jsx
import React from "react";
import "./MessageCard.css";

function MessageCard({ header, description }) {
  return (
    <div className="message-card">
      {/* Left color bar */}
      <div className="left-bar"></div>

      {/* Main content */}
      <div className="message-content">
        <h2>{header}</h2>
        <p>{description}</p>
      </div>

      {/* Action buttons */}
      <div className="message-actions">
        <button className="edit-btn">Modifier</button>
        <button className="delete-btn">Supprimer</button>
      </div>
    </div>
  );
}

export default MessageCard;
