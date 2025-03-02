// src/pages/MessagesPage.jsx
import React, { useState, useEffect } from "react";
import MessageCard from "../components/MessageCard";
import "./MessagesPage.css";

function MessagesPage() {
  const [alerts, setAlerts] = useState([]);
  const [header, setHeader] = useState("");
  const [description, setDescription] = useState("");
  // State for message status from the main modal ("actif" or "programme")
  const [messageStatus, setMessageStatus] = useState("actif");
  const [editingIndex, setEditingIndex] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  // State for the dropdown in the main modal
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  // NEW: state for calendar modal
  const [isCalendarOpen, setIsCalendarOpen] = useState(false);
  const [scheduledTime, setScheduledTime] = useState("");

  // Track which tab is active: "actifs", "programme", or "favoris"
  const [activeTab, setActiveTab] = useState("actifs");

  // Fetch alerts from the backend on mount
  useEffect(() => {
    fetch("/api/messages")
      .then((response) => response.json())
      .then((data) => setAlerts(data))
      .catch((error) => console.error("Error fetching alerts:", error));
  }, []);

  // Save updated alerts to the backend
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
    // Reset status to default ("actif")
    setMessageStatus("actif");
    // Close dropdown if open
    setIsDropdownOpen(false);
  };

  const addAlert = () => {
    openModal();
  };

  // Handles adding/editing an alert from the main modal.
  // (This is used if the user is not scheduling via the calendar.)
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
        severity: "alert",
        liked: false,
        status: messageStatus,
        // If no scheduledTime is set, this alert is immediate.
      };
      updatedAlerts = [...alerts, newAlert];
    } else {
      updatedAlerts = alerts.map((alert, i) => {
        if (i === editingIndex) {
          return { 
            ...alert, 
            header: header.trim(), 
            description: description.trim(),
            status: messageStatus 
          };
        }
        return alert;
      });
    }
    setAlerts(updatedAlerts);
    saveAlerts(updatedAlerts);
    closeModal();
  };

  // When editing, load the message details into the main modal.
  const startEditing = (index) => {
    setEditingIndex(index);
    setHeader(alerts[index].header);
    setDescription(alerts[index].description);
    setMessageStatus(alerts[index].status || "actif");
    openModal();
  };

  const removeAlert = (index) => {
    const updatedAlerts = alerts.filter((_, i) => i !== index);
    setAlerts(updatedAlerts);
    saveAlerts(updatedAlerts);
  };

  // Toggle like status for an alert.
  const toggleLike = (index) => {
    const updatedAlerts = alerts.map((alert, i) => {
      if (i === index) {
        return { ...alert, liked: !alert.liked };
      }
      return alert;
    });
    setAlerts(updatedAlerts);
    saveAlerts(updatedAlerts);
  };

  // Filter alerts based on the active tab.
  const getFilteredAlerts = () => {
    if (activeTab === "favoris") {
      return alerts.filter((alert) => alert.liked);
    } else if (activeTab === "actifs") {
      return alerts.filter((alert) => alert.status === "actif");
    } else if (activeTab === "programme") {
      return alerts.filter((alert) => alert.status === "programme");
    }
    return alerts;
  };

  // When the user chooses "Planifier l'envoi", close the main modal and open the calendar modal.
  const openCalendarModal = () => {
    setIsModalOpen(false);
    // Optionally, you could keep header/description in state to be re-used.
    setIsCalendarOpen(true);
  };

  // Handle scheduling: update alert with scheduledTime and status "programme".
  const handleScheduleConfirm = () => {
    if (!scheduledTime) {
      alert("Veuillez sélectionner une date et une heure.");
      return;
    }
    let updatedAlerts;
    // For new alert scheduling:
    if (editingIndex === null) {
      const newAlert = {
        header: header.trim(),
        description: description.trim(),
        severity: "alert",
        liked: false,
        status: "programme", // forced scheduled status
        scheduledTime: scheduledTime
      };
      updatedAlerts = [...alerts, newAlert];
    } else {
      // For editing an existing alert.
      updatedAlerts = alerts.map((alert, i) => {
        if (i === editingIndex) {
          return {
            ...alert,
            header: header.trim(),
            description: description.trim(),
            status: "programme",
            scheduledTime: scheduledTime
          };
        }
        return alert;
      });
    }
    setAlerts(updatedAlerts);
    saveAlerts(updatedAlerts);
    // Close the calendar modal and reset states.
    setIsCalendarOpen(false);
    setScheduledTime("");
    // Optionally, you can also reset header/description if desired.
  };

  return (
    <div className="messages-page">
      {/* Header container with title, description, and button */}
      <div className="header">
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

      {/* TABS ROW */}
      <div className="tabs-container">
        <div
          className={activeTab === "actifs" ? "tab active" : "tab"}
          onClick={() => setActiveTab("actifs")}
        >
          Messages actifs
        </div>
        <div
          className={activeTab === "programme" ? "tab active" : "tab"}
          onClick={() => setActiveTab("programme")}
        >
          Programmé
        </div>
        <div
          className={activeTab === "favoris" ? "tab active" : "tab"}
          onClick={() => setActiveTab("favoris")}
        >
          Favoris
        </div>
      </div>

      {/* Modal for adding/editing a message */}
      {isModalOpen && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h2>{editingIndex === null ? "Création du message" : "Modifier le message"}</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label htmlFor="title">Titre du message</label>
                <input
                  id="title"
                  type="text"
                  value={header}
                  onChange={(e) => setHeader(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label htmlFor="message">Message</label>
                <textarea
                  id="message"
                  rows="4"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label htmlFor="status">Statut</label>
                <select
                  id="status"
                  value={messageStatus}
                  onChange={(e) => setMessageStatus(e.target.value)}
                >
                  <option value="actif">Messages actifs</option>
                  <option value="programme">Programmé</option>
                </select>
              </div>
              <div className="modal-footer">
                <button type="button" className="cancel-btn" onClick={closeModal}>
                  Annuler
                </button>
                <div className="btn-group">
                  <button type="submit" className="continue-btn">
                    Enregistrer
                  </button>
                  <button
                    type="button"
                    className="dropdown-toggle"
                    onClick={() => {
                      setIsDropdownOpen(!isDropdownOpen);
                    }}
                  >
                    <img src="/src/assets/arrow_down.png" alt="Options" />
                  </button>
                  {isDropdownOpen && (
                    <div className="dropdown-menu">
                      <div
                        className="dropdown-item"
                        onClick={() => {
                          // When "Planifier l'envoi" is selected,
                          // close dropdown and open the calendar modal.
                          setIsDropdownOpen(false);
                          openCalendarModal();
                        }}
                      >
                        Planifier l'envoi
                      </div>
                      {/* Add more dropdown items as needed */}
                    </div>
                  )}
                </div>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Calendar Modal for scheduling */}
      {isCalendarOpen && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h2>Planifier l'envoi</h2>
            <div className="form-group">
              <label htmlFor="scheduledTime">Date et heure</label>
              <input
                type="datetime-local"
                id="scheduledTime"
                value={scheduledTime}
                onChange={(e) => setScheduledTime(e.target.value)}
              />
            </div>
            <div className="modal-footer">
              <button
                type="button"
                className="cancel-btn"
                onClick={() => {
                  // If cancel, close calendar modal and reopen main modal
                  setIsCalendarOpen(false);
                  openModal();
                }}
              >
                Annuler
              </button>
              <button
                type="button"
                className="continue-btn"
                onClick={handleScheduleConfirm}
              >
                Confirmer
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Display list of alerts filtered by the active tab */}
      <div className="messages-list">
        {getFilteredAlerts().map((alert, index) => (
          <MessageCard
            key={index}
            header={alert.header}
            description={alert.description}
            liked={alert.liked || false}
            onLikeToggle={() => toggleLike(index)}
            onEdit={() => startEditing(index)}
            onRemove={() => removeAlert(index)}
          />
        ))}
      </div>
    </div>
  );
}

export default MessagesPage;
