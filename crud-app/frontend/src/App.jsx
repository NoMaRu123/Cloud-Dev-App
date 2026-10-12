import { useState, useEffect } from 'react' // React tools: useState (remember data), useEffect (run code at load)
import './App.css' // load this component's styles

// Where the API lives: set in .env.development locally, empty (same origin) when built for AWS
const API_URL = import.meta.env.VITE_API_URL ?? '' // read the setting; if missing, use '' (same server)

function App() {
  const [items, setItems] = useState([])             // the list of items from the database, starts empty
  const [name, setName] = useState('')               // what's typed in the Name box
  const [description, setDescription] = useState('') // what's typed in the Description box
  const [error, setError] = useState('')             // error message to show in red ('' = no error)

  // Runs once, when the page first appears
  useEffect(() => {
    async function loadItems() {
      const response = await fetch(`${API_URL}/items/`) // GET /items/ from the backend
      const data = await response.json()                // turn the JSON reply into a JS list
      setItems(data)                                    // save it, React redraws the list
    }
    loadItems()
  }, []) // [] = only once, not on every redraw

  // Runs when the form is submitted (Add button or Enter key)
  async function createItem(event) {
    event.preventDefault() // stop the browser reloading the page (default form behaviour)
    setError('')           // clear any old error message

    const response = await fetch(`${API_URL}/items/`, { // send the new item to the backend
      method: 'POST',                                    // POST = create
      headers: { 'Content-Type': 'application/json' },   // tell the server the body is JSON
      body: JSON.stringify({ name, description }),       // the item, as JSON text
    })
    const data = await response.json() // the reply: the new item (with id) or an error

    if (!response.ok) { // not a 2xx status = something went wrong
      // 409/404 send detail as a string; 422 (validation) sends a list of problems
      setError(typeof data.detail === 'string' ? data.detail : data.detail[0].msg) // show the message
      return // stop here, don't add anything to the list
    }

    setItems([...items, data]) // new list = all old items + the new one, React redraws
    setName('')                // empty the Name box
    setDescription('')         // empty the Description box
  }

  // Runs when a Delete button is clicked
  async function deleteItem(id) {
    setError('') // clear any old error message

    const response = await fetch(`${API_URL}/items/${id}`, { // the URL says WHICH item, e.g. /items/3
      method: 'DELETE',                                      // DELETE = remove it
    })

    if (!response.ok) {                  // e.g. 404 if it was already deleted
      const data = await response.json() // read the error reply
      setError(data.detail)              // show it in red ("Item not found")
      return                             // stop, leave the list as it is
    }

    setItems(items.filter((item) => item.id !== id)) // new list = every item EXCEPT the deleted one
  }

  return (
    <main>
      <h1>My CRUD App</h1>

      {/* The add form: submitting it runs createItem */}
      <form onSubmit={createItem}>
        <input
          placeholder="Name"                                // grey hint text when empty
          value={name}                                      // the box shows what `name` holds
          onChange={(event) => setName(event.target.value)} // every keystroke updates `name`
        />
        <input
          placeholder="Description"
          value={description}                                      // the box shows `description`
          onChange={(event) => setDescription(event.target.value)} // every keystroke updates it
        />
        {/* type="submit" = clicking it submits the form */}
        <button type="submit">Add</button>
      </form>

      {/* Only shows when there is an error message */}
      {error && <p className="error">{error}</p>}

      {/* If the list is empty show a message, otherwise show the list (if / else) */}
      {items.length === 0 ? (
        <p>No items yet.</p>
      ) : (
        <ul>
          {/* For each item, make one <li> (like a for loop) */}
          {items.map((item) => (
            <li
              key={item.id} // unique id so React can tell rows apart
            >
              <strong>{item.name}</strong>: {item.description}
              {/* () => waits for the click, then deletes THIS row's item */}
              <button onClick={() => deleteItem(item.id)}>Delete</button>
            </li>
          ))}
        </ul>
      )}
    </main>
  )
}

export default App // let main.jsx import this component
