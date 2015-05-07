#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import HttpResponse, Http404
from django.views.generic import View
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib import messages

import markdown2

from . import models, forms

# Create your views here.

class Index(View):
    template_name = 'main/index.html'
    def get(self, request):
        data = {}
        posts = models.Post.objects.filter(is_draft=False).order_by('-id')
        pages = models.Page.objects.all()
        data['posts'] = posts
        data['pages'] = pages
        return render(request, self.template_name, data)

class Post(View):
    template_name = 'main/post.html'
    def get(self, request, pk):
        try:
            pk = int(pk)
            post = models.Post.objects.get(pk=pk)
        except models.Post.DoesNotExist:
            raise Http404
        data = {'post':post}
        return render(request, self.template_name, data)

class Page(View):
    template_name = 'main/page.html'
    def get(self, request, pk):
        try:
            pk = int(pk)
            page = models.Page.objects.get(pk=pk)
        except page.DoesNotExist:
            raise Http404
        data = {'page':page}
        return render(request, self.template_name, data)

class AdminIndex(View):
    template_name = 'blog_admin/index.html'
    def get(self, request):
        data = {}
        return render(request, self.template_name, data)

class AdminPosts(View):
    template_name = 'blog_admin/posts.html'
    def get(self, request):
        data = {}
        draft = request.GET.get('draft')
        if draft and draft.lower()=='true':
            flag = True
        else:
            flag = False
        posts = models.Post.objects.filter(is_draft=flag).order_by('-pub_date')
        data['posts'] = posts
        return render(request, self.template_name, data)

class AdminPost(View):
    template_name = 'blog_admin/post.html'
    def get(self, request, pk=0, form=None):
        data = {}
        form_data = {}
        if pk:
            try:
                pk = int(pk)
                post = models.Post.objects.get(pk=pk)
                form_data['title'] = post.title
                form_data['content'] = post.raw
                form_data['abstract'] = post.abstract
                data['edit_flag'] = True
            except models.Post.DoesNotExist:
                raise Http404
        if not form:
            form = forms.NewPost(initial=form_data)
        data['form'] = form
        return render(request, self.template_name, data)

    def post(self, request, pk=0, form=None):
        form = forms.NewPost(request.POST)
        if form.is_valid():
            if not pk:
                cur_post = models.Post()
            else:
                try:
                    pk = int(pk)
                    cur_post = models.Post.objects.get(pk=pk)
                except models.Post.DoesNotExist:
                    raise Http404
            cur_post.title = form.cleaned_data['title']
            cur_post.raw = form.cleaned_data['content']
            cur_post.abstract = form.cleaned_data['abstract']
            html = markdown2.markdown(cur_post.raw, extras=['code-friendly', 'fenced-code-blocks'])
            cur_post.content_html = html
            cur_post.author = request.user
            if request.POST.get('publish'):
                cur_post.is_draft = False
                cur_post.save()
                # return HttpResponse('Post has been pulished!')
                # return redirect('/admin/posts')
                # return redirect(reverse('main:admin_edit_post', kwargs={'pk':cur_post.id}))
                msg = 'Post has been pulished!'
                messages.add_message(request, messages.SUCCESS, msg)
                return redirect(reverse('main:admin_posts'))
            else:
                cur_post.is_draft=True
                cur_post.save()
                msg = 'Draft has been saved!'
                messages.add_message(request, messages.SUCCESS, msg)
                url = '{0}?draft=true'.format(reverse('main:admin_posts'))
                return redirect(url)

        return self.get(request, form)

class DeletePost(View):
    def get(self, request, pk):
        try:
            pk = int(pk)
            cur_post = models.Post.objects.get(pk=pk)
            is_draft = cur_post.is_draft
            url = reverse('main:admin_posts')
            if is_draft:
                url = '{0}?draft=true'.format(url)    
            cur_post.delete()
        except models.Post.DoesNotExist:
            raise Http404

        return redirect(url)

        




