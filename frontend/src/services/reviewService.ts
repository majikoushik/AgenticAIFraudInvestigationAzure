import { apiClient } from "@/services/apiClient";
import type { HumanReviewRequest, HumanReviewResponse, ReviewOptions, ReviewerRole } from "@/types/review.types";

export function submitHumanReview(caseId: string, review: HumanReviewRequest): Promise<HumanReviewResponse> {
  return apiClient<HumanReviewResponse>(`/api/v1/cases/${caseId}/review`, {
    method: "POST",
    body: JSON.stringify(review)
  });
}

export function getReviewOptions(caseId: string, reviewerRole: ReviewerRole): Promise<ReviewOptions> {
  return apiClient<ReviewOptions>(`/api/v1/cases/${caseId}/review-options?reviewer_role=${reviewerRole}`);
}
