import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import AlertsManager from "/components/AlertsManager.jsx";
import MainLayout from "./layouts/MainLayout.jsx";
import MessagesPage from "./pages/MessagesPage.jsx";

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <div>
        
        <div>
      <MainLayout>
      <MessagesPage />
    </MainLayout>
    </div>
      </div>
    </>
  )
}

export default App
