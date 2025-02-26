// src/pages/MessagesPage.jsx
import React, { useState, useEffect } from "react";
import MessageCard from "../components/MessageCard";
import "./MessagesPage.css";

function MessagesPage() {
  const [alerts, setAlerts] = useState([]);
  const [header, setHeader] = useState("");
  const [description, setDescription] = useState("");
  const [editingIndex, setEditingIndex] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Fetch alerts from the backend on mount
  useEffect(() => {
    fetch("/api/messages")
      .then((response) => response.json())
      .then((data) => setAlerts(data))
      .catch((error) => console.error("Error fetching alerts:", error));
  }, []);

  // Function to save updated alerts to the backend
  const saveAlerts = (newAlerts) => {
    fetch("/api/messages", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(newAlerts)
    })
      .then((response) => response.json())
      .then((data) => console.log("Alerts saved successfully:", data))
      .catch((error) => console.error("Error saving alerts:", error));
  };

  const openModal = () => {
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setHeader("");
    setDescription("");
    setEditingIndex(null);
  };

  const addAlert = () => {
    openModal();
  };

  // This function handles both adding and editing.
  // It also calls saveAlerts to persist changes.
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!header.trim() || !description.trim()) {
      alert("Veuillez remplir le titre et la description.");
      return;
    }
    let updatedAlerts;
    if (editingIndex === null) {
      const newAlert = {
        header: header.trim(),
        description: description.trim(),
        severity: "alert"
      };
      updatedAlerts = [...alerts, newAlert];
      setAlerts(updatedAlerts);
    } else {
      updatedAlerts = alerts.map((alert, i) => {
        if (i === editingIndex) {
          return { ...alert, header: header.trim(), description: description.trim() };
        }
        return alert;
      });
      setAlerts(updatedAlerts);
    }
    saveAlerts(updatedAlerts);
    closeModal();
  };

  const startEditing = (index) => {
    setEditingIndex(index);
    setHeader(alerts[index].header);
    setDescription(alerts[index].description);
    openModal();
  };

  const removeAlert = (index) => {
    const updatedAlerts = alerts.filter((_, i) => i !== index);
    setAlerts(updatedAlerts);
    saveAlerts(updatedAlerts);
  };

  return (
    <div className="messages-page">
      {/* Header container with title, description, and the button on the right */}
      <div className="header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", margin: "50px 50px 20px" }}>
        <div className="Title">
          <h1>Messages</h1>
          <p>Ajouter, modifier et supprimer les messages qui s'afficheront sur la bannière</p>
        </div>
        {editingIndex === null ? (
          <button className="add-btn" onClick={addAlert}>
            + Ajouter un message
          </button>
        ) : (
          <button className="add-btn" onClick={handleSubmit}>
            Enregistrer Modification
          </button>
        )}
      </div>

      {/* Modal for adding/editing a message */}
      {isModalOpen && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h2>{editingIndex === null ? "Création du message" : "Modifier le message"}</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label htmlFor="title">Titre</label>
                <input
                  id="title"
                  type="text"
                  value={header}
                  onChange={(e) => setHeader(e.target.value)}
                  placeholder="Titre"
                />
              </div>

              <div className="form-group">
                <label htmlFor="message">Message</label>
                <textarea
                  id="message"
                  rows="4"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Message"
                />
              </div>

              <div className="modal-footer">
                <button type="button" className="cancel-btn" onClick={closeModal}>
                  Annuler
                </button>
                <button type="submit" className="continue-btn">
                  Enregistrer
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Existing messages */}
      <div className="messages-list" style={{ margin: "50px" }}>
        {alerts.map((alert, index) => (
          <div key={index} style={{ marginBottom: "10px" }}>
            <MessageCard
              header={alert.header}
              description={alert.description}
              onEdit={() => startEditing(index)}
              onRemove={() => removeAlert(index)}
            />
          </div>
        ))}
      </div>
    </div>
  );
}

export default MessagesPage;
