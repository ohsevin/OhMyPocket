import random

from django.shortcuts import redirect
from django.http import Http404
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from article.models import Article, UserPostArticle
from utils import q, to_json, redis_conn, required_login
from exceptions import APIException, ParseError

@to_json
@required_login
@require_http_methods(["POST"])
def add_article(request):
    url = request.POST.get("url") or None
    if(url is None):
        raise ParseError("require url parameter")

    article, _ = Article.objects.get_or_create(original_url=url)
    upa, created = UserPostArticle.objects.get_or_create(article=article, user=request.user)
    # post process in rq worker
    if created:
        q.enqueue(upa.defer_process)

    return {}

def random_article(request):
    ''' put all primary article id to the redis
        redis[all] = set(1,2,3)
        put all user read in redis
        redis[user] = set(1,2, 3)

        consider use sdiff: r.sdiff(keys=('local', 'mythtv'))
    '''

    # use request.user 
    # if we need to collect anonymous user data
    if request.user.is_authenticated(): 
        article_id_sets = redis_conn.sdiff((Article.ALL_PRIMARY_IDS_KEY, request.user.id)) or 0
        if article_id_sets == 0:
            raise Http404
        article_id = random.sample(article_id_sets, 1)[0]
        redis_conn.sadd(request.user.id, article_id)
        # save to user read


    else:
        article_id = redis_conn.srandmember(Article.ALL_PRIMARY_IDS_KEY) or 0

    return redirect("/api/article/%s/"%article_id)


@to_json
def get_article_by_id(request, articleid):
    article = Article.objects.filter(id=articleid).first()
    if article is None:
        raise Http404

    return article.to_dict()





