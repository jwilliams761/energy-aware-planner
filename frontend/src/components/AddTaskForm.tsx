import { useState, type FormEvent } from 'react'

function AddTaskForm() {
  const [title, setTitle] = useState('')
  const [category, setCategory] = useState('')
  const [description, setDescription] = useState('')
  const [dueAt, setDueAt] = useState('')
  const [estimatedMinutes, setEstimatedMinutes] = useState<number | null>(null)
  const[cognitiveDemand, setCognitiveDemand] = useState<number | null>(null)

async function handleSubmit(event: FormEvent<HTMLFormElement>) {
  event.preventDefault()

  console.log('1: submit function started')

  console.log({
    title,
    description,
    category,
    dueAt,
    estimatedMinutes,
    cognitiveDemand
  })

  if (
    !title ||
    !description ||
    !category ||
    !dueAt ||
    estimatedMinutes === null ||
    cognitiveDemand === null
  ) {
    return
  }

  const response = await fetch('http://127.0.0.1:8000/tasks', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      title: title,
      description: description,
      category: category,
      due_at: dueAt,
      estimated_minutes: estimatedMinutes,
      cognitive_demand: cognitiveDemand,
      completed: false,
    }),
  })

  if (response.ok) {
    setTitle('')
    setDescription('')
    setCategory('')
    setDueAt('')
    setEstimatedMinutes(null)
    setCognitiveDemand(null)
  }
}

  return (
    <section>
      <h2>Add Task</h2>

      <form onSubmit={handleSubmit}>
        <label>
          Task title:
        </label>
        <input
        type = "text"
        value = {title}
        onChange={(event) => setTitle(event.target.value)}
        />
      <label>
        Category:
  <select
  value={category}
  onChange={(event) => setCategory(event.target.value)}>
    <option value="">Select category</option>
    <option value="school">School</option>
    <option value="career">Career</option>
    <option value="personal">Personal</option>
  </select>
        </label>
        <textarea
  value={description}
  onChange={(event) => setDescription(event.target.value)}
/>
        <label>
  Due date:
  <input
    type="datetime-local"
    value={dueAt}
    onChange={(event) => setDueAt(event.target.value)}
  />
</label>
<label>
  Estimated time (minutes):
  <input
    type="number"
    min="1"
    value = {estimatedMinutes ?? ''}
    onChange = {(event) => setEstimatedMinutes(Number(event.target.value))}
  />
</label>
<label>
  Cognitive demand:
  <select
    value={cognitiveDemand ?? ''}
    onChange = {(event) => setCognitiveDemand(Number(event.target.value))}
  >
    <option value="">Select demand</option>
    <option value="1">1 - Very light</option>
    <option value="2">2 - Light</option>
    <option value="3">3 - Moderate</option>
    <option value="4">4 - Demanding</option>
    <option value="5">5 - Very demanding</option>
  </select>
</label>
<button type="submit">
  Add Task
</button>
</form>

      <p>Current title: {title}</p>
    </section>
  )
}



export default AddTaskForm
