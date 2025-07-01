import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import Podcast from './podcast'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <Podcast/>
    </>
  )
}

export default App
