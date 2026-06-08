import type { FeedbackRating } from "@/types/feedback.types";

const ratings: FeedbackRating[] = ["VERY_POOR", "POOR", "ACCEPTABLE", "GOOD", "EXCELLENT"];

export function FeedbackRatingSelector({ value, onChange }: { value: FeedbackRating; onChange: (value: FeedbackRating) => void }) {
  return (
    <select value={value} onChange={(event) => onChange(event.target.value as FeedbackRating)}>
      {ratings.map((rating) => <option key={rating} value={rating}>{rating.replaceAll("_", " ")}</option>)}
    </select>
  );
}
