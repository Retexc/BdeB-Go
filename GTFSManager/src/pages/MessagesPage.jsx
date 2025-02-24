// src/pages/MessagesPage.jsx
import React, { useState, useEffect } from "react";
import MessageCard from "../components/MessageCard";

function MessagesPage() {
  // State to store alerts and form fields.
  const [alerts, setAlerts] = useState([]);
  const [header, setHeader] = useState("");
  const [description, setDescription] = useState("");
  const [editingIndex, setEditingIndex] = useState(null);

  // Fetch alerts from custom_messages.json on mount.
  useEffect(() => {
    fetch("/custom_messages.json")
      .then((response) => response.json())
      .then((data) => setAlerts(data))
      .catch((error) => console.error("Error fetching alerts:", error));
  }, []);

  // Add a new alert.
  const addAlert = () => {
    if (!header.trim() || !description.trim()) {
      alert("Veuillez remplir le titre et la description.");
      return;
    }
    const newAlert = {
      header: header.trim(),
      description: description.trim(),
      severity: "alert",
    };
    setAlerts([...alerts, newAlert]);
    setHeader("");
    setDescription("");
  };

  // Remove an alert.
  const removeAlert = (index) => {
    const newAlerts = alerts.filter((_, i) => i !== index);
    setAlerts(newAlerts);
  };

  // Begin editing an alert.
  const startEditing = (index) => {
    setEditingIndex(index);
    setHeader(alerts[index].header);
    setDescription(alerts[index].description);
  };

  // Save modifications.
  const saveEdit = () => {
    if (editingIndex === null) return;
    if (!header.trim() || !description.trim()) {
      alert("Veuillez remplir le titre et la description.");
      return;
    }
    const newAlerts = alerts.map((alert, i) => {
      if (i === editingIndex) {
        return { ...alert, header: header.trim(), description: description.trim() };
      }
      return alert;
    });
    setAlerts(newAlerts);
    setEditingIndex(null);
    setHeader("");
    setDescription("");
  };

  return (
    <div style={{ padding: "20px" }}>
      {/* Top bar with title and dynamic button */}
      <div className="messages-topbar" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h1>Messages</h1>
        {editingIndex === null ? (
          <button className="add-btn" onClick={addAlert}>+ Ajouter un message</button>
        ) : (
          <button className="add-btn" onClick={saveEdit}>Enregistrer Modification</button>
        )}
      </div>

      {/* Input form */}
      <div style={{ marginBottom: "1rem" }}>
        <input
          type="text"
          placeholder="Titre"
          value={header}
          onChange={(e) => setHeader(e.target.value)}
          style={{ width: "300px", marginRight: "1rem" }}
        />
        <textarea
          placeholder="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          style={{ width: "300px", height: "100px", verticalAlign: "top" }}
        />
      </div>

      <p>Ajouter, modifier et supprimer les messages qui s'afficheront sur la bannière</p>

      {/* Optional tabs (you can style these as needed) */}
      <div className="messages-tabs" style={{ display: "flex", gap: "10px", marginBottom: "1rem" }}>
        <button className="active">Messages actifs</button>
        <button>Programmé</button>
        <button>Fermé</button>
      </div>

      {/* Messages list */}
      <div className="messages-list">
        {alerts.map((alert, index) => (
          <div key={index} style={{ marginBottom: "10px" }}>
            <MessageCard header={alert.header} description={alert.description} />
            <div style={{ marginTop: "5px" }}>
              <button onClick={() => startEditing(index)} style={{ marginRight: "5px" }}>Modifier</button>
              <button onClick={() => removeAlert(index)}>Supprimer</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default MessagesPage;
