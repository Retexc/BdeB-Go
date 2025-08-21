<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";

const alerts = ref([]);
const allAlertsText = ref('');
const showBanner = ref(false);
let alertInterval = null;

const fetchAlerts = async () => {
  try {
    const response = await fetch('/api/data');
    const data = await response.json();
    
    if (data.alerts && data.alerts.length > 0) {
      // Remove duplicates by creating a unique key for each alert
      const uniqueAlerts = data.alerts.filter((alert, index, arr) => {
        const alertKey = `${alert.header}-${alert.description}-${alert.train_route || alert.routes}`;
        return arr.findIndex(a => `${a.header}-${a.description}-${a.train_route || a.routes}` === alertKey) === index;
      });
      
      alerts.value = uniqueAlerts;
      
      const combinedAlerts = uniqueAlerts
        .map((alert) => {
          if (alert.routes === "Custom" && alert.stop === "Message") {
            return `${alert.header}: ${alert.description}`;
          } else if (alert.routes) {
            // STM alerts
            return `Ligne(s) : ${alert.routes} (${alert.stop}): ${alert.header} - ${alert.description}`;
          } else if (alert.train_route) {
            // EXO alerts
            return `Train ${alert.train_route}: ${alert.header} - ${alert.description}`;
          } else {
            // Fallback for custom alerts
            return `${alert.header}: ${alert.description}`;
          }
        })
        .join(" ••• ");
      
      allAlertsText.value = combinedAlerts;
      showBanner.value = true;
    } else {
      showBanner.value = false;
    }
  } catch (error) {
    console.error('Error fetching alerts:', error);
    showBanner.value = false;
  }
};

onMounted(() => {
  fetchAlerts();
  alertInterval = setInterval(fetchAlerts, 30000); // Update every 30 seconds
});

onBeforeUnmount(() => {
  if (alertInterval) {
    clearInterval(alertInterval);
  }
});
</script>

<template>
  <div 
    v-if="showBanner" 
    class="alert-banner"
  >
    <div class="alert-track">
      <div class="alert-content">
        <svg 
          class="alert-icon" 
          xmlns="http://www.w3.org/2000/svg" 
          width="24" 
          height="24" 
          viewBox="0 0 24 24" 
          fill="none" 
          stroke="currentColor" 
          stroke-width="2" 
          stroke-linecap="round" 
          stroke-linejoin="round"
        >
          <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
          <path d="M12 9v4"/>
          <path d="M12 17h.01"/>
        </svg>
        
        <span class="alert-text">{{ allAlertsText }}</span>
        <span class="alert-text-spacer">•••</span>
      </div>
      <!-- Duplicate content for seamless loop -->
      <div class="alert-content" aria-hidden="true">
        <svg 
          class="alert-icon" 
          xmlns="http://www.w3.org/2000/svg" 
          width="24" 
          height="24" 
          viewBox="0 0 24 24" 
          fill="none" 
          stroke="currentColor" 
          stroke-width="2" 
          stroke-linecap="round" 
          stroke-linejoin="round"
        >
          <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
          <path d="M12 9v4"/>
          <path d="M12 17h.01"/>
        </svg>
        
        <span class="alert-text">{{ allAlertsText }}</span>
        <span class="alert-text-spacer">•••</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.alert-banner {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(135deg, #ff8c00, #ff6b00);
  color: black;
  padding: 12px 0;
  z-index: 1000;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.alert-track {
  display: flex;
  width: fit-content;
  animation: scroll 30s linear infinite;
}

.alert-content {
  display: flex;
  align-items: center;
  white-space: nowrap;
  padding-right: 50px;
}

.alert-icon {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  margin-right: 12px;
  margin-left: 20px;
  color: white;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.3));
}

.alert-text {
  font-size: 22px;
  font-weight: 700;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.alert-text-spacer {
  margin: 0 20px;
  font-weight: 600;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

@keyframes scroll {
  0%, 5% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(-50%);
  }
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .alert-text {
    font-size: 14px;
  }
  
  .alert-icon {
    width: 20px;
    height: 20px;
    margin-left: 15px;
  }
  
  .alert-track {
    animation-duration: 20s;
  }
}
</style>