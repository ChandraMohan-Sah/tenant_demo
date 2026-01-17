from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from users.models import CustomUser

class BaseModel(models.Model):
    created_at = models.DateTimeField(db_index=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

 
class Task(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=500)  
    completed = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)

     
    #------validation------------
    '''
        mentality: what rules must be true for this object to be valid ?
        example: published_at should not be in the future, or title shouldn't be empty.
    '''
    def clean(self):
        if self.title is None :
            raise ValidationError({'title':'title cannot be empty'})
        if self.published_at and self.published_at > timezone.now():
            raise ValidationError({'published_at':'published_at cannot be in the future'})
        if len(self.description) < 5:
            raise ValidationError({'description':'description should be at least 5 characters long'})        
    
    
    #--------properties------------
    '''
        mentality : what extra info can I calculate on the fly, without saving to DB?
        is_overdue: check if task is past deadline.
        summary:    maybe return title + short description.
    '''
    @property
    def is_overdue(self):
        if self.published_at and not self.completed:
            return True
        return False
        

    @property
    def summary(self):
        short_decription = (self.description[:47] + '...') if len(self.description) > 50 else self.description
        return f"{self.title} : {short_decription}"
        

    #----------methods : changes state of an object ------------
    '''
        simple business logic 
        mentality : what actions can I perform on this object that change its state ?
        - mark_complete: set completed to True, update updated_at.
        - mark_incomplete: set completed to False, update updated_at.
        - don't call .save() here, let the caller decide when to save.
    '''
    def mark_complete(self):
        self.completed = True 
        self.updated_at = timezone.now()
        return self
        

    def mark_incomplete(self):
        self.completed = False
        self.updated_at = timezone.now()
        return self
    

    #-----------Meta---------------
    '''
        mentality : how should this model behave in the DB ?
        - ordering: default ordering by created_at descending.
        - verbose_name: human readable name for admin.
        - unique constraint: description must be unique.
        - index: index on completed for faster queries.
    '''
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Task'
        constraints = [
            models.UniqueConstraint(fields=['description'], name='unique_task_description')
        ]
        indexes = [
            models.Index(fields=['completed']),
        ]
    
    def __str__(self):
        return self.title
    
