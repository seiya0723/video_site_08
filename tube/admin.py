from django.contrib import admin
from .models import Video,Category,VideoComment,MyList,History

admin.site.register(Video)
admin.site.register(Category)
admin.site.register(VideoComment)
admin.site.register(MyList)
admin.site.register(History)