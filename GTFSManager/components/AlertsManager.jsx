// src/components/AlertsManager.jsx
import React, { useState, useEffect } from "react";

function AlertsManager() {
  // State to store alerts and input fields
  const [alerts, setAlerts] = useState([]);
  const [header, setHeader] = useState("");
  const [description, setDescription] = useState("");
  const [editingIndex, setEditingIndex] = useState(null);

  // Fetch alerts from custom_messages.json on component mount
  useEffect(() => {
    fetch("/custom_messages.json")
      .then((response) => response.json())
      .then((data) => setAlerts(data))
      .catch((error) => console.error("Error fetching alerts:", error));
  }, []);

  // Function to refresh alerts (if needed)
  const refreshAlerts = () => {
    fetch("/custom_messages.json")
      .then((response) => response.json())
      .then((data) => setAlerts(data))
      .catch((error) => console.error("Error fetching alerts:", error));
  };

  // Add a new alert
  const addAlert = () => {
    if (!header.trim() || !description.trim()) {
      alert("Please fill in both the header and the description.");
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

  // Remove an alert by its index
  const removeAlert = (index) => {
    const newAlerts = alerts.filter((_, i) => i !== index);
    setAlerts(newAlerts);
  };

  // Start editing an alert (populate input fields)
  const startEditing = (index) => {
    setEditingIndex(index);
    setHeader(alerts[index].header);
    setDescription(alerts[index].description);
  };

  // Save modifications to an alert
  const saveEdit = () => {
    if (editingIndex === null) return;
    if (!header.trim() || !description.trim()) {
      alert("Please fill in both the header and the description.");
      return;
    }
    const newAlerts = alerts.map((alert, index) => {
      if (index === editingIndex) {
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
    <div style={{ padding: "1rem" }}>
      <h1>Custom Alerts Manager</h1>
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
      <ul>
        {alerts.map((alert, index) => (
          <li key={index} style={{ marginBottom: "0.5rem" }}>
            <strong>{alert.header}</strong>:{" "}
            {alert.description.length > 50
              ? alert.description.substring(0, 50) + "..."
              : alert.description}
            <button onClick={() => startEditing(index)} style={{ marginLeft: "1rem" }}>
              Modify
            </button>
            <button onClick={() => removeAlert(index)} style={{ marginLeft: "0.5rem" }}>
              Remove
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default AlertsManager;
