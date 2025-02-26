import React from "react";
import "./MessageCard.css";

function MessageCard({ header, description, onEdit, onRemove }) {
  return (
    <div className="alert-box">
      {/* 1) Green bar on the left */}
      <div className="alert-bar"></div>

      {/* 2) Middle content (title + description) */}
      <div className="alert-content">
        <h2 className="alert-title">{header}</h2>
        <p className="alert-description">{description}</p>
      </div>

      {/* 3) Buttons on the far right */}
      <div className="alert-actions">
        <button className="like-btn">
          <img src="/src/assets/heart_empty.png" alt="Like" />
        </button>
        <button className="edit-btn" onClick={onEdit}>
        <img src="/src/assets/edit.png" alt="Edit" />Modifier</button>
        <button className="delete-btn" onClick={onRemove}>
        <img src="/src/assets/delete.png" alt="Edit" />Supprimer</button>
      </div>
    </div>
  );
}

export default MessageCard;
