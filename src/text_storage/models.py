from django.db import models


class Text(models.Model):
    EXCERPT_LENGTH_CHARS = 100

    content = models.TextField()
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        db_index=True,
    )

    def __str__(self):
        if len(self.content) > self.EXCERPT_LENGTH_CHARS:
            return '{} ...'.format(self.content[:self.EXCERPT_LENGTH_CHARS])
        else:
            return self.content
