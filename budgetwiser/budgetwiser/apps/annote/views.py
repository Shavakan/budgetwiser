from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseBadRequest
from django.core.serializers.json import DjangoJSONEncoder
import json

from budgetwiser.apps.annote.models import Article, Range, Paragraph, Comment, Factcheck

def index(request, article_id):
    article = Article.objects.get(id=article_id)
    paragraphs = article.paragraphs.all()

    data = {
        'id': article.id,
        'title': article.title,
        'date': article.date,
        'url': article.s_url,
        'press': article.s_name,
        'paragraphs': [],
    }
    for paragraph in paragraphs:
        p_data = {
            'id': paragraph.id,
            'content': paragraph.content,
            'c_count': paragraph.c_count,
        }
        data['paragraphs'].append(p_data)

    data_json = json.dumps(data, ensure_ascii=False, indent=4, cls=DjangoJSONEncoder)

    response_context = {
        'article': article,
        'paragraphs': paragraphs,
        'data': data_json,
    }

    return render_to_response('index.html', response_context, context_instance=RequestContext(request))

def get_range(request):
    try:
        paragraphs = json.loads(request.GET.get('paragraphs', None))
        range_list = []

        for p_id in paragraphs:
            paragraph = Paragraph.objects.get(id=p_id)
            ranges = paragraph.ranges.all()
            for range in ranges:
                range_obj = {
                    'id': range.id,
                    'parent_elm': range.parent_elm,
                    'start': range.start,
                    'end': range.end,
                    'f_average': range.f_average,
                    'f_count': range.f_count,
                }
                range_list.append(range_obj)

        range_list_json = json.dumps(range_list, ensure_ascii=False, indent=4, cls=DjangoJSONEncoder)

        return HttpResponse(range_list_json)
    except:
        return HttpResponseBadRequest("Something wrong with 'get_range'")

def save_range(request):
    try:
        parent_elm = request.GET.get('parent_elm', None)
        start = request.GET.get('start', None)
        end = request.GET.get('end', None)
        range = Range.objects.filter(parent_elm=parent_elm, start=start, end=end)
        if len(range) == 0:
            paragraph_id = request.GET.get('paragraph_id', None)
            paragraph = Paragraph.objects.get(id=paragraph_id)

            new_range = Range(
                parent_elm=parent_elm,
                start=start,
                end=end,
                paragraph=paragraph,
                f_count=0,
                f_average=0,
            )
            new_range.save()

            range_output = {
                'id': new_range.id,
                'type': 0,
            }
            range_json = json.dumps(range_output, ensure_ascii=False, indent=4, cls=DjangoJSONEncoder)

            return HttpResponse(range_json)
        else:
            range_output = {
                'id': range[0].id,
                'type': 1,
            }
            range_json = json.dumps(range_output, ensure_ascii=False, indent=4, cls=DjangoJSONEncoder)

            return HttpResponse(range_json)
    except:
        return HttpResponseBadRequest("Something wrong with 'save_range'")

def get_factcheck(request):
    try:
        range_id = request.GET.get('range_id', None)
        factchecks = Factcheck.objects.filter(rangeof__id=range_id)
        factcheck_list = []

        for factcheck in factchecks:
            factcheck_obj = {
                'id': factcheck.id,
                'score': factcheck.score,
                'ref': factcheck.ref,
                'ref_score': factcheck.ref_score,
            }
            factcheck_list.append(factcheck_obj)

        factcheck_list_json = json.dumps(factcheck_list, ensure_ascii=False, indent=4, cls=DjangoJSONEncoder)

        return HttpResponse(factcheck_list_json)
    except:
        return HttpResponseBadRequest("Something wrong with 'get_factcheck'")

def save_factcheck(request):
    try:
        range_id = request.GET.get('range_id', None)
        rangeof = Range.objects.get(id=range_id)
        paragraph = rangeof.paragraph
        print paragraph.id, rangeof.id

        score = request.GET.get('score', None)
        ref = request.GET.get('ref', None)
        print score, ref

        new_factcheck = Factcheck(
            score = score,
            ref = ref,
            rangeof = rangeof,
            paragraph = paragraph
        )
        new_factcheck.save()

        return HttpResponse("Factcheck saved")
    except:
        return HttpResponseBadRequest("Something wrong with 'save_factcheck'")

def get_comment(request):
    try:
        paragraph_id = request.GET.get('paragraph_id', None)
        paragraph = Paragraph.objects.get(id=paragraph_id)

        comments = paragraph.comments.all()

        comment_list = {
            'question_list': [],
            'answer_list': []
        }

        for comment in comments:
            comment_obj = {
                'id': comment.id,
                'writer': comment.writer,
                'typeof': comment.typeof,
                'content': comment.content,
                'ref': comment.ref,
                'rangeof': comment.rangeof_id,
                'question': comment.question_id,
                'num_goods': comment.num_goods,
                'num_bads': comment.num_bads,
            }
            if(comment.typeof == 0):
                comment_list['question_list'].append(comment_obj)
            else:
                comment_list['answer_list'].append(comment_obj)


        comment_list_json = json.dumps(comment_list, ensure_ascii=False, indent=4, cls=DjangoJSONEncoder)

        return HttpResponse(comment_list_json)
    except:
        return HttpResponseBadRequest("Something wrong with 'get_comment'")

