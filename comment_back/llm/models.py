from django.db import models
from crawler.models import Comment, Episode


# Create your models here.
class CommentAnalysisResult(models.Model):
    comment = models.OneToOneField(  # 변경: ForeignKey → OneToOneField
        Comment, on_delete=models.CASCADE, related_name="analysis_result"
    )
    content = models.TextField()
    sentiment = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis for Comment {self.comment.id} - Sentiment: {self.sentiment}"


class CommentsSummaryResult(models.Model):
    episode = models.ForeignKey(
        Episode, on_delete=models.CASCADE, related_name="summary_results"
    )
    source_comments = models.JSONField()
    summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Summary for Comment {self.episode.id} - Summary: {self.summary[:50]}"


class GenAICommentSummaryResult(models.Model):
    episode = models.ForeignKey(
        Episode, on_delete=models.CASCADE, related_name="genai_summary_results"
    )
    comments = models.ManyToManyField(
        Comment, related_name="genai_summary_results", blank=True
    )
    summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"GenAI Summary for Episode {self.episode.id} - Summary: {self.summary[:50]}"
