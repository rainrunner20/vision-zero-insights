import { useState } from "react"

export default function PredictionPanel() {
  const [formData, setFormData] = useState({
    borough: "MANHATTAN",
    crash_date: "2024-01-01",
    contributing_factor_vehicle_1: "Driver Inattention/Distraction"
  })
  const [prediction, setPrediction] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData({ ...formData, [name]: value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setPrediction(null)
    try {
      const res = await fetch((import.meta.env.VITE_API_URL || 'http://localhost:5000').replace(/\/+$/, '') + '/api/predict', {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      })
      const data = await res.json()
      setPrediction(res.ok ? data.predicted_severity : 'Unavailable')
    } catch (err) {
      console.error("Prediction failed", err)
      setPrediction("❌ Prediction failed")
    }
    setLoading(false)
  }

  return (
    <div className="fixed top-16 right-0 w-full max-w-md bg-white shadow-lg p-6 z-50">
      <h2 className="text-xl font-bold mb-4">Traffic crash severity (research demo)</h2>
      <p className="my-3 text-sm text-gray-600">
        An experimental low/high classification based on limited historical inputs.
        Not a forecast of actual injuries, clinical evidence, or safety advice.
      </p>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="date"
          name="crash_date"
          value={formData.crash_date}
          onChange={handleChange}
          className="w-full border p-2 rounded"
        />
        <select
          name="borough"
          value={formData.borough}
          onChange={handleChange}
          className="w-full border p-2 rounded"
        >
          <option>MANHATTAN</option>
          <option>QUEENS</option>
          <option>BROOKLYN</option>
          <option>BRONX</option>
          <option>STATEN ISLAND</option>
        </select>
        <input
          type="text"
          name="contributing_factor_vehicle_1"
          value={formData.contributing_factor_vehicle_1}
          onChange={handleChange}
          placeholder="Contributing Factor"
          className="w-full border p-2 rounded"
        />
        <button
          type="submit"
          className="bg-blue-600 text-white px-4 py-2 rounded"
        >
          {loading ? "Predicting..." : "Predict"}
        </button>
      </form>
      {prediction !== null && (
        <div className="mt-4 text-lg">
          Experimental category: <b>{prediction}</b>
        </div>
      )}
    </div>
  )
}
