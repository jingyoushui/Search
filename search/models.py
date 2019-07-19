from django.db import models

# Create your models here.
# -*- coding: utf-8 -*-

from datetime import datetime
from elasticsearch_dsl import DocType,  Nested, Boolean, \
    analyzer, InnerObjectWrapper, Completion, Keyword, Text, Integer,Object,GeoPoint

from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer

from elasticsearch_dsl.connections import connections
connections.create_connection(hosts=["localhost"])

class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}


ik_analyzer = CustomAnalyzer("ik_max_word", filter=["lowercase"])

class ArticleType(DocType):
    suggest = Completion(analyzer=ik_analyzer)
    orcText = Text(analyzer="ik_max_word")
    pdfUrl = Keyword()
    textResult = [Object]
    text = Text(analyzer="ik_max_word")
    charNum = Integer()
    isHandwritten = Boolean
    leftTop = GeoPoint
    rightTop = GeoPoint
    leftBottom = GeoPoint
    rightBottom = GeoPoint
    class Meta:
        index = "test"
        doc_type = "article"
