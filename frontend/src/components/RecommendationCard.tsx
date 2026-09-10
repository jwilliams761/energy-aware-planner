type Task = {
  title: string
  estimated_minutes: number
  category: string
  due_at: string
}

type Recommendation = {
  recommendation_type: string
  recommended_task: Task | null
  reason: string
  score?: number
}

type RecommendationCardProps = {
  recommendation: Recommendation
}


function RecommendationCard({ recommendation }: RecommendationCardProps) {
  return (
    <section>
      <h2>Recommendation</h2>
      <p>{recommendation.reason}</p>

      {recommendation.recommended_task && (
        <div>
          <h3>{recommendation.recommended_task.title}</h3>

          <p>
            Estimated time: {recommendation.recommended_task.estimated_minutes} minutes
          </p>
          <p>
            Category: 
            {recommendation.recommended_task.category.charAt(0).toUpperCase() + 
            recommendation.recommended_task.category.slice(1)}
          </p>
          <p>
            Due: {new Date(recommendation.recommended_task.due_at
            ).toLocaleDateString()}
          </p>
        </div>
      )}
    </section>
  )
}

export default RecommendationCard