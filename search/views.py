from django.shortcuts import render

# Create your views here.
import json
from django.shortcuts import render
from django.views.generic.base import View
from search.models import ArticleType
from django.http import HttpResponse
from elasticsearch import Elasticsearch
from datetime import datetime
import redis

client = Elasticsearch(hosts=["127.0.0.1"])
redis_cli = redis.StrictRedis()


class IndexView(View):
    # 首页
    def get(self, request):
        topn_search = redis_cli.zrevrangebyscore("search_keywords_set", "+inf", "-inf", start=0, num=5)
        return render(request, "index.html", {"topn_search": topn_search})


class SearchSuggest(View):
    def get(self, request):
        key_words = request.GET.get('s', '')
        s_type = request.GET.get("s_type", 'article')
        if s_type == "article":
            s = ArticleType.search()

        re_datas = []
        if key_words:
            s = s.suggest('my_suggest', key_words, completion={
                "field": "suggest", "fuzzy": {
                    "fuzziness": 2
                },
                "size": 10
            })
            suggestions = s.execute_suggest()
            for match in suggestions.my_suggest[0].options:
                source = match._source
                re_datas.append(source["title"])
        return HttpResponse(json.dumps(re_datas), content_type="application/json")


class SearchView(View):
    def get(self, request):
        key_words = request.GET.get("q", "")
        s_type = request.GET.get("s_type", "article")
        jobbole_count = redis_cli.get("jobbole_count")
        start_time = datetime.now()
        hit_list = []
        # global response
        if s_type == "article":
            redis_cli.zincrby("search_keywords_set", 1, key_words)
            topn_search = redis_cli.zrevrangebyscore("search_keywords_set", "+inf", "-inf", start=0, num=5)
            page = request.GET.get("p","")
            try:
                page = int(page)
            except:
                page = 1
            response = client.search(
                index="pdfocr",
                body={
                    "query": {
                        "multi_match": {
                            "query": key_words,
                            "fields": ["tags", "pdfURL", "ocrText","jpgpath"]
                        }
                    },
                    "from": (page - 1) * 10,
                    "size": 10,
                    "highlight": {
                        "pre_tags": ['<span class="keyWord">'],
                        "post_tags": ['</span>'],
                        "fields": {
                            "pdfURL": {},
                            "ocrText": {},
                            "jpgpath": {},
                        }
                    }
                }
            )
            for hit in response["hits"]["hits"]:
                hit_dict = {}
                if "pdfURL" in hit["highlight"]:
                    hit_dict["pdfURL"] = "".join(hit["highlight"]["pdfURL"])
                else:
                    hit_dict["pdfURL"] = hit["_source"]["pdfURL"]
                if "ocrText" in hit["highlight"]:
                    hit_dict["ocrText"] = "".join(hit["highlight"]["ocrText"])
                else:
                    hit_dict["ocrText"] = hit["_source"]["ocrText"]

                if "jpgpath" in hit["highlight"]:
                    hit_dict["jpgpath"] = "".join(hit["highlight"]["jpgpath"])
                else:
                    hit_dict["jpgpath"] = hit["_source"]["jpgpath"]

                hit_dict["score"] = hit["_score"]
                hit_dict["id"] = hit["_id"]



                hit_list.append(hit_dict)

        end_time = datetime.now()
        last_seconds = (end_time - start_time).total_seconds()
        total_nums = response["hits"]["total"]['value']
        print(total_nums)
        if (page % 10) > 0:
            page_nums = int(total_nums / 10) + 1
        else:
            page_nums = int(total_nums / 10)

        return render(request, "result.html", {"page": page,
                                               "all_hits": hit_list,
                                               "key_words": key_words,
                                               "total_nums": total_nums,
                                               "page_nums": page_nums,
                                               "last_seconds": last_seconds,
                                               "jobbole_count": jobbole_count,
                                               "topn_search": topn_search
                                               })
class DetailView(View):
    # 首页
    def get(self, request):
        ocrText = request.GET.get("ocrText", "")
        jpgpath = request.GET.get("jpgpath","")


        return render(request, "detail.html", {"ocrText": ocrText,"jpgpath":jpgpath})
