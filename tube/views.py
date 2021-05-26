from rest_framework import status,views,response

from django.shortcuts import render, redirect

from django.db.models import Q

from django.http.response import JsonResponse

from django.template.loader import render_to_string

from django.core.paginator import Paginator

from django.conf import settings

#TIPS:ログイン状態かチェックする。ビュークラスに継承元として指定する(多重継承なので順番に注意)。未ログインであればログインページへリダイレクト。
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone

from .models import Video,Category,VideoComment,MyList,History,GoodVideo,BadVideo
from .forms import VideoEditForm
from .serializer import VideoSerializer,VideoCommentSerializer,MyListSerializer,HistorySerializer,RateSerializer,GoodSerializer,BadSerializer

DEFAULT_VIDEO_AMOUNT = 7

#python-magicで受け取ったファイルのMIMEをチェックする。
#MIMEについては https://developer.mozilla.org/ja/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types を参照。

import magic
ALLOWED_MIME   = ["video/mp4", "image/vnd.adobe.photoshop", "application/postscript", "image/jpeg", "image/png"]

# アップロードの上限
LIMIT_SIZE     = 200 * 1000 * 1000

SEARCH_AMOUNT_PAGE  = 20

#トップページ
class IndexView(views.APIView):

    def get(self, request, *args, **kwargs):

        latests = Video.objects.all().order_by("-dt")[:DEFAULT_VIDEO_AMOUNT]

        if request.user.is_authenticated:
            histories   = History.objects.filter(user=request.user.id).order_by("?")[:DEFAULT_VIDEO_AMOUNT]
        else:
            histories   = False
        '''
        paginator  = Paginator(latests,7)
        

        if "page" in request.GET:
            latests    = paginator.get_page(request.GET["page"])
        else:
            latests    = paginator.get_page(1)
        '''
        context = {"latests": latests,
                   "histories":histories,}

        return render(request, "tube/index.html", context)

index = IndexView.as_view()

#アップロードページ
class UploadView(LoginRequiredMixin,views.APIView):

    def get(self,request, *args, **kwargs):

        categories = Category.objects.all()
        context = {"categories": categories}

        return render(request, "tube/upload.html", context)


    def post(self, request, *args, **kwargs):

        print(request.data)

        request.data["user"]    = request.user.id
        serializer              = VideoSerializer(data=request.data)
        mime_type               = magic.from_buffer(request.FILES["movie"].read(1024), mime=True)

        print(request.data["movie"].size)
        print(type(request.data["movie"].size))

        if request.FILES["movie"].size >= LIMIT_SIZE:
            mb = str(LIMIT_SIZE / 1000000)

            json = {"error": True,
                    "message": "The maximum file size is " + mb + "MB"}

            return JsonResponse(json)

        if mime_type not in ALLOWED_MIME:
            mime = str(ALLOWED_MIME)
            json = {"error": True,
                    "message": "The file you can post is " + mime + "."}

            return JsonResponse(json)

        if serializer.is_valid():
            serializer.save()
        else:
            json    = { "error":True,
                        "message":"入力内容に誤りがあります。" }
            return JsonResponse(json)

        json    = { "error":False,
                    "message":"アップロード完了しました。" }

        return JsonResponse(json)


upload = UploadView.as_view()



#検索結果表示ページ
class SearchView(views.APIView):

    def get(self, request, *args, **kwargs):

        query = Q()
        page = 1

        if "word" in request.GET:

            word_list = request.GET["word"].replace("　", " ").split(" ")
            for w in word_list:
                query &= Q(Q(title__icontains=w) | Q(description__icontains=w))

        if "page" in request.GET:
            page = request.GET["page"]

        videos = Video.objects.filter(query).order_by("-dt")
        amount = len(videos)

        videos_paginator = Paginator(videos, SEARCH_AMOUNT_PAGE)
        videos           = videos_paginator.get_page(page)

        context = {"videos": videos,
                   "amount": amount}

        return render(request, "tube/search.html", context)

search = SearchView.as_view()


#動画個別ページ
class SingleView(views.APIView):

    def get(self,request, video_pk, *args, **kwargs):

        video = Video.objects.filter(id=video_pk).first()

        #Todo:F5で再生回数水増し可能。
        video.views = video.views + 1
        video.save()

        if request.user.is_authenticated:
            print("認証済みユーザーです")

            history = History.objects.filter(user=request.user.id, target=video_pk).first()

            if history:
                print("存在する場合の処理")
                history.views   = history.views + 1
                history.dt      = timezone.now()
                history.save()
            else:
                print("履歴に存在しない場合の処理")
                data        = { "target":video_pk,
                                "user":request.user.id,}
                serializer  = HistorySerializer(data=data)

                if serializer.is_valid():
                    serializer.save()

        comments    = VideoComment.objects.filter(target=video_pk).order_by("-dt")
        good        = GoodVideo.objects.filter(target=video_pk)
        bad         = BadVideo.objects.filter(target=video_pk)

        already_good    = GoodVideo.objects.filter(target=video_pk, user=request.user.id)
        already_bad     = BadVideo.objects.filter(target=video_pk, user=request.user.id)
        relates         = Video.objects.filter(category=video.category).order_by("-dt")


        paginator = Paginator(comments, 5)

        if "page" in request.GET:
            comments = paginator.get_page(request.GET["page"])
        else:
            comments = paginator.get_page(1)

        context = {"video": video,
                   "comments": comments,
                   "good": good,
                   "bad": bad,
                   "already_good": already_good,
                   "already_bad": already_bad,
                   "relates": relates,
                   }

        return render(request, "tube/single.html", context)

    def post(self,request,video_pk,*args,**kwargs):

        return JsonResponse(json)

        # return redirect("tube:videos",video_pk=video_pk)

single = SingleView.as_view()


class SingleModView(LoginRequiredMixin,views.APIView):

    def post(self, request, video_pk, *args, **kwargs):


        copied   = request.POST.copy()

        copied["target"]  = video_pk
        copied["user"]    = request.user.id

        serializer  = VideoCommentSerializer(data=copied)
        json        = {}

        if serializer.is_valid():
            print("コメントバリデーションOK")
            serializer.save()

            comments    = VideoComment.objects.filter(target=video_pk).order_by("-dt")
            context     = { "comments": comments }

            content     = render_to_string('tube/comments.html', context, request)

            json        = { "error":False,
                            "message":"投稿完了",
                            "content":content,
                            }

        else:
            print("コメントバリデーションNG")
            json        = {"error":True,
                           "message":"入力内容に誤りがあります。",
                           "content":"",
                           }


        return JsonResponse(json)

    def patch(self,request,video_pk,*args,**kwargs):

        serializer  = RateSerializer(data=request.data)

        if serializer.is_valid():

            validated_data  = serializer.validated_data

            if validated_data["flag"]:

                data    = GoodVideo.objects.filter(user=request.user.id, target=video_pk).first()

                if data:
                    data.delete()
                    print("削除")
                else:
                    data    = { "user":request.user.id,
                                "target":video_pk,
                                }
                    serializer  = GoodSerializer(data=data)

                    if serializer.is_valid():
                        print("セーブ")
                        serializer.save()
                    else:
                        print("バリデーションエラー")

            else:

                data    = BadVideo.objects.filter(user=request.user.id, target=video_pk).first()

                if data:
                    data.delete()
                    print("削除")
                else:
                    data = {"user": request.user.id,
                            "target": video_pk,
                            }
                    serializer = BadSerializer(data=data)

                    if serializer.is_valid():
                        print("セーブ")
                        serializer.save()
                    else:
                        print("バリデーションエラー")

            good         = GoodVideo.objects.filter(target=video_pk)
            bad          = BadVideo.objects.filter(target=video_pk)
            already_good = GoodVideo.objects.filter(target=video_pk, user=request.user.id)
            already_bad  = BadVideo.objects.filter(target=video_pk, user=request.user.id)
            video        = Video.objects.filter(id=video_pk).first()

            context = {"good": good,
                       "bad": bad,
                       "already_good": already_good,
                       "already_bad": already_bad,
                       "video": video,
                       }

            content = render_to_string('tube/rate.html', context, request)

            json = {"error": False,
                    "message": "投稿完了",
                    "content": content,
                    }
        else:

            json = {"error": True,
                    "message": "入力内容に誤りがあります。",
                    "content": "",
                    }

        return JsonResponse(json)


single_mod = SingleModView.as_view()


class RankingView(views.APIView):

    def get(self,request,*args,**kwargs):

        return render(request,"tube/rank.html")

rank    = RankingView.as_view()


class MyPageView(LoginRequiredMixin, views.APIView):

    def get(self, request, *args, **kwargs):
        videos = Video.objects.filter(user=request.user.id).order_by("-dt")
        good_videos = GoodVideo.objects.filter(user=request.user.id).order_by("-dt")
        context = {"videos": videos,
                   "good_videos": good_videos}

        return render(request, "tube/mypage.html", context)


mypage = MyPageView.as_view()


# 閲覧履歴表示
class HistoryView(LoginRequiredMixin, views.APIView):

    def get(self, request, *args, **kwargs):
        histories = History.objects.filter(user=request.user.id).order_by("-dt")

        context = {"histories": histories}

        return render(request, "tube/history.html", context)


history = HistoryView.as_view()


# おすすめ動画
class RecommendView(LoginRequiredMixin,views.APIView):

    def get(self,request,*args,**kwargs):

        return render(request, "tube/recommend.html")

recommend = RecommendView.as_view()


#通知
class NotifyView(views.APIView):

    def get(self,request,*args,**kwargs):

        return render(request, "tube/notify.html")

notify = NotifyView.as_view()



#マイリスト
class MyListView(LoginRequiredMixin,views.APIView):

    def get(self,request,*args,**kwargs):

        mylists = MyList.objects.filter(user=request.user.id).order_by("-dt")

        context = {"mylists":mylists}

        return render(request,"tube/mylist.html",context)

    def post(self,request,*args,**kwargs):

        copied          = request.POST.copy()
        copied["user"]  = request.user.id

        serializer      = MyListSerializer(data=copied)
        if serializer.is_valid():

            mylist      = MyList.objects.filter(user=request.user.id, target=request.POST["target"])
            if not mylist:
                serializer.save()
                error   = False
                message = "マイリスト登録完了"
            else:
                error   = True
                message = "すでにマイリストに登録しています。"

        else:
            error       = True
            message     = "入力内容に誤りがあります。"

        json            = { "error":error,
                            "message":message,
                            }

        return JsonResponse(json)

mylist = MyListView.as_view()


class DeleteView(LoginRequiredMixin,views.APIView):

    def get(self, request, video_pk, *args, **kwargs):

        video   = Video.objects.filter(id=video_pk).first()
        context = { "video":video }

        return render(request, "tube/delete.html", context )


    def post(self, request, video_pk, *args, **kwargs):

        print("削除")

        # .first()で一番上のレコードを1つ取る。
        video    = Video.objects.filter(id=video_pk).first()
        video.delete()

        # TIPS:すでにurls.pyにてpkが数値型であることがわかっているので、バリデーションをする必要はない。

        return redirect("tube:index")

delete = DeleteView.as_view()


class UpdateView(LoginRequiredMixin,views.APIView):

    def get(self, request, video_pk, *args, **kwargs):

        video   = Video.objects.filter(id=video_pk).first()
        context = { "video":video }

        return render(request, "tube/update.html", context )

    def post(self, request, video_pk, *args, **kwargs):

        # まず、編集対象のレコード特定
        instance    = Video.objects.filter(id=video_pk).first()

        # 第2引数にinstanceを指定することで、対象の編集ができる。
        formset     = VideoEditForm(request.POST, instance=instance)

        if formset.is_valid():
            print("バリデーションOK")
            formset.save()
            Video.objects.filter(id=video_pk).update(edited=True)

        else:
            print("バリデーションNG")

        return redirect("tube:index")


update  = UpdateView.as_view()


class ConfigViews(LoginRequiredMixin,views.APIView):

    def get(self, request, *args, **kwargs):

        return render(request, "tube/config.html")

config = ConfigViews.as_view()
