import { useState } from 'react'
import './App.css'
import RecommendationCard from './components/RecommendationCard'
import AddTaskForm from './components/AddTaskForm'
import TaskList from './components/TaskList'
function App() {
  const [wakefulnessLevel, setWakefulnessLevel] = useState<number | null>(null)
  const [availableMinutes, setAvailableMinutes] = useState<number | null>(null)
  const [recommendation, setRecommendation] = useState<any>(null)

  async function handleRecommendation(){
    if (wakefulnessLevel === null || availableMinutes === null) {
    return
    
  }
    const response = await fetch('http://127.0.0.1:8000/recommendations', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        wakefulness_level: wakefulnessLevel,
        available_minutes: availableMinutes,
      }),
    })

    const data = await response.json()
    setRecommendation(data)
    console.log(data)
  }


  return (
    <>
      <header>
        <h1>Energy Aware Planner</h1>
      </header>
      <AddTaskForm />
      <TaskList />
      <main><section><h2> How are you feeling?</h2>
      <button onClick={() => setWakefulnessLevel(1)}>Exhausted</button>
      <button onClick={() => setWakefulnessLevel(2)}>Low Energy</button>
      <button onClick={() => setWakefulnessLevel(3)}>Moderate</button>
      <button onClick={() => setWakefulnessLevel(4)}>Alert</button>
      <button onClick={() => setWakefulnessLevel(5)}>Energized</button>
      <label>Available Minutes:</label>
      <input type="number" min="1" onChange={(event) => setAvailableMinutes(Number(event.target.value))}/>
      {availableMinutes !== null && (<p>Available minutes: {availableMinutes}</p>)}
      <button type="button" onClick={handleRecommendation}>
        Get Recommdenation
        </button>
        {recommendation !== null && (
          
          <RecommendationCard recommendation={recommendation} />
        )}
      {wakefulnessLevel !== null && (<p>Selected wakefulness: {wakefulnessLevel}</p>)}
        </section>
        </main>
    </>
  )
}

export default App

