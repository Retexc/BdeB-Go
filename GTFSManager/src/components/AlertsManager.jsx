// src/components/AlertsManager.jsx
import React, { useState, useEffect } from "react";
import MessageCard from "./MessageCard.jsx";

function AlertsManager() {
  const [alerts, setAlerts] = useState([]);
  const [header, setHeader] = useState("");
  const [description, setDescription] = useState("");
  const [editingIndex, setEditingIndex] = useState(null);

  // Fetch messages from the backend when the component mounts
  useEffect(() => {
    fetch("/api/messages")
      .then((response) => response.json())
      .then((data) => setAlerts(data))
      .catch((error) => console.error("Error fetching alerts:", error));
  }, []);

  // Function to send updated alerts to the backend
  const saveAlerts = (newAlerts) => {
    fetch("/api/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(newAlerts)
    })
      .then((response) => response.json())
      .then((data) => console.log("Alerts saved successfully:", data))
      .catch((error) => console.error("Error saving alerts:", error));
  };

  const addAlert = () => {
    if (!header.trim() || !description.trim()) {
      alert("Please fill in both the header and the description.");
      return;
    }
    const newAlert = {
      header: header.trim(),
      description: description.trim(),
      severity: "alert"
    };
    const updatedAlerts = [...alerts, newAlert];
    setAlerts(updatedAlerts);
    saveAlerts(updatedAlerts); // Save to backend
    setHeader("");
    setDescription("");
  };

  const removeAlert = (index) => {
    const updatedAlerts = alerts.filter((_, i) => i !== index);
    setAlerts(updatedAlerts);
    saveAlerts(updatedAlerts);
  };

  const startEditing = (index) => {
    setEditingIndex(index);
    setHeader(alerts[index].header);
    setDescription(alerts[index].description);
  };

  const saveEdit = () => {
    if (!header.trim() || !description.trim()) {
      alert("Please fill in both the header and the description.");
      return;
    }
    const updatedAlerts = alerts.map((alert, i) => {
      if (i === editingIndex) {
        return { ...alert, header: header.trim(), description: description.trim() };
      }
      return alert;
    });
    setAlerts(updatedAlerts);
    saveAlerts(updatedAlerts); // Persist changes
    setEditingIndex(null);
    setHeader("");
    setDescription("");
  };

  return (
    <div style={{ padding: "1rem" }}>
      <h1>Custom Alerts Manager</h1>
      {/* Input fields for adding/editing alerts */}
      <div style={{ marginBottom: "1rem" }}>
        <input
          type="text"
          placeholder="Header"
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
        <div style={{ marginTop: "0.5rem" }}>
          {editingIndex === null ? (
            <button onClick={addAlert}>Add Alert</button>
          ) : (
            <button onClick={saveEdit}>Save Modification</button>
          )}
        </div>
      </div>
      <hr />
      <h2>Current Alerts</h2>
      <ul style={{ listStyle: "none", padding: 0 }}>
        {alerts.map((alert, index) => (
          <li key={index} style={{ marginBottom: "0.5rem" }}>
            <MessageCard
              header={alert.header}
              description={
                alert.description.length > 50
                  ? alert.description.substring(0, 50) + "..."
                  : alert.description
              }
              onEdit={() => startEditing(index)}
              onRemove={() => removeAlert(index)}
            />
          </li>
        ))}
      </ul>
    </div>
  );
}

export default AlertsManager;
