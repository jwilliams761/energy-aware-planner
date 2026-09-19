import { useEffect, useState } from 'react'


type Task = {
  id: number
  title: string
  description: string
  category: string
  due_at: string
  estimated_minutes: number
  cognitive_demand: number
  completed: boolean
}

function TaskList() {
  const [tasks, setTasks] = useState<Task[]>([])

  useEffect(() => {
    async function fetchTasks() {
      const response = await fetch('http://127.0.0.1:8000/tasks')
      const data = await response.json()
      setTasks(data)
    }

    fetchTasks()
  }, [])

  async function completeTask(taskId: number) {
  await fetch(`http://127.0.0.1:8000/tasks/${taskId}/complete`, {
    method: 'PATCH'
  })

  setTasks((currentTasks) =>
    currentTasks.filter((task) => task.id !== taskId) 
  )
  }
  return (
    <section>
      <h2>Your Tasks</h2>

      {tasks.map((task) => (
        <div key={task.id}>
          <h3>{task.title}</h3>
          <p>{task.description}</p>
          <button onClick={() => completeTask(task.id)}>
            Mark Complete
          </button>
        </div>
      ))}
    </section>
  )
}


export default TaskList