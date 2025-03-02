import React from "react";
import "./MessageCard.css";

function MessageCard({ header, description, liked, onLikeToggle, onEdit, onRemove }) {
  return (
    <div className="alert-box">
      <div className="alert-bar"></div>
      <div className="alert-content">
        <h2 className="alert-title">{header}</h2>
        <p className="alert-description">{description}</p>
      </div>
      <div className="alert-actions">
        <button className="like-btn" onClick={onLikeToggle}>
          <img
            src={liked ? "/src/assets/heart.png" : "/src/assets/heart_empty.png"}
            alt="Like"
          />
        </button>
        <button className="edit-btn" onClick={onEdit}>
          <img src="/src/assets/edit.png" alt="Edit" /> Modifier
        </button>
        <button className="delete-btn" onClick={onRemove}>
          <img src="/src/assets/delete.png" alt="Delete" /> Supprimer
        </button>
      </div>
    </div>
  );
}

export default MessageCard;
