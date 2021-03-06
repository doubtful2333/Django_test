from django.shortcuts import render, redirect, HttpResponse
from app01 import models


URL = {'index': 'index.html',
       'login': 'login.html',
       'ajax1': 'ajax1.html',
       'm2m': 'm2m.html',
       'option': 'option.html',
       'table': 'dict_in_table.html',

       'block': 'block-1.html',
       'simple tag': 'simple_tag.html',
       'page': 'page-1.html',

       'app01-m-app': 'app01-m/1',
       'app01-n-app': 'app01-n/1',
       'session': 'session.html',
       'csrf': 'csrf.html',
       }


# 验证是否登录的装饰器，在需要应用的函数前加：@auth
def auth(func):
    def inner(request, *args, **kwargs):
        username = request.COOKIES.get('username')
        if not username:
            return redirect('/index.html')
        res = func(request, *args, **kwargs)
        return res

    return inner


def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    if request.method == 'POST':
        user = request.POST.get('username', None)
        print('sth post')
        print(user)
        request.session['username'] = user
        request.session['is_login'] = True
    return redirect('session.html')


def index(request):
    return render(request, 'index.html', {'url': URL})


# ajax基础
# @auth
def ajax1(request):
    user = models.User.objects.all().values('id', 'name', 'age', 'gender', 'school__s_name')
    school = models.School.objects.all().values('id', 's_name')
    if request.method == 'GET':
        return render(request, 'ajax1.html', {'url': URL, 'user_list': user, 'school_list': school})
    elif request.method == 'POST':
        name = request.POST.get('name', None)
        age = request.POST.get('age', None)
        gender = request.POST.get('gender', None)
        school = request.POST.get('school', None)
        method = request.POST.get('method', None)
        if method == 'del':
            u_id = request.POST.get('id', None)
            models.User.objects.filter(id=u_id).delete()
            return HttpResponse('Done')
        elif len(name) < 1:
            return HttpResponse('please input the name')
        elif len(age) < 1:
            return HttpResponse('please input the age')
        elif len(gender) < 1:
            return HttpResponse('please choose the gender')
        elif len(school) < 1:
            return HttpResponse('please choose the school')
        elif method == 'add':
            school_obj = models.School.objects.filter(s_name=school).first()
            models.User.objects.create(name=name, age=age, gender=gender, school=school_obj)
            return HttpResponse('Done')
        elif method == 'edit':
            u_id = request.POST.get('id', None)
            school_obj = models.School.objects.filter(s_name=school).first()
            models.User.objects.filter(id=u_id).update(name=name, age=age, gender=gender, school=school_obj)
            return HttpResponse('Done')


# Django orm 多对多操作(ajax传列表，获取JSON)
def m2m(request):
    if request.method == 'GET':
        choose_list = models.Course.objects.all()
        student_list = models.User.objects.all()
        int('qwe')  # error test
        return render(request, 'm2m.html', {'choose_list': choose_list, 'student_list': student_list})
    elif request.method == 'POST':
        c_id = request.POST.get('c_id', None)
        student = request.POST.getlist('student', None)
        course_name = request.POST.get('course', None)
        method = request.POST.get('method', None)
        if method == 'del':
            obj = models.Course.objects.filter(id=c_id).first()
            obj.r.clear()
            obj.delete()
            return HttpResponse('Done')
        elif method == 'edit':
            id_list = []
            models.Course.objects.filter(id=c_id).update(c_name=course_name)
            obj = models.Course.objects.filter(id=c_id).first()
            for i in student:
                temp = models.User.objects.filter(name=i).first().id
                id_list.append(temp)
            obj.r.set(id_list)
            return HttpResponse('Done')
        elif method == 'add':
            id_list = []
            obj = models.Course.objects.create(c_name=course_name)
            for i in student:
                temp = models.User.objects.filter(name=i).first().id
                id_list.append(temp)
            obj.r.add(*id_list)  # 注意传列表的方式
            return HttpResponse('Done')


# Django 模版 母版
def block(request, **kwargs):
    if request.method == 'GET':
        page = kwargs.get('page', None)
        url = 'block' + str(page) + '.html'
    return render(request, url)


# simple tag
def simple_tag(request):
    if request.method == 'GET':
        name = 'Name'
        return render(request, 'simple_tag.html', {'name': name})


# 分页
def page(request, **kwargs):
    from utils import paginations
    print(request.environ)
    if request.method == 'GET':
        # 生成数据
        data_list = []
        for i in range(1024):
            data_list.append(i)
        total_data = len(data_list)  # 总数据
        # 获取当前页
        current_page = kwargs.get('page', 1)
        current_page = int(current_page)
        # 分页
        page_obj = paginations.Page(current_page, total_data, 'page')
        if current_page > page_obj.total_page_num:
            return HttpResponse('Page not found')
        page_str = page_obj.page_str
        data = data_list[page_obj.start_data: page_obj.end_data]
        return render(request, 'page.html', {'data': data, 'page_list': page_str})


# session
def session(request):
    if request.session.get('is_login'):
        # request.session[''] 如果不存在key会报错
        return HttpResponse(request.session['username'])
    else:
        return redirect('/login.html')


# csrf
def csrf(request):
    if request.method == 'GET':
        return render(request, 'csrf.html')
    elif request.method == 'POST':
        print('sth post')
        username = request.POST.get('username', None)
        print(username)
        return HttpResponse(username)


# 获取数据库数据方法
def dict_in_table(request):
    v1 = models.User.objects.all()
    # 对象列表
    v2 = models.User.objects.all().values('id', 'name', 'age', 'gender', 'school__s_name')
    # 字典列表 'school__s_name': 'A school'
    v25 = models.User.objects.all().values()
    # 字典列表 'school_id': 1
    v3 = models.User.objects.all().values_list('id', 'name', 'age', 'gender', 'school__s_name')
    # 元祖列表 'A school'
    v35 = models.User.objects.all().values_list()
    # 元祖列表 1
    print(v1)
    print(v2)
    print(v25)
    print(v3)
    print(v35)
    return HttpResponse('Print Done')


# 数据库添加数据
def option(request):
    if request.method == 'GET':
        # 为id=1的课程添加学生
        # obj1 = models.Course.objects.filter(id=1).first()
        # obj1.r.add(3, 4, 5, 6)
        # obj2 = models.Course.objects.filter(id=2).first()
        # obj2.r.add(3, 5, 6)
        # obj3 = models.Course.objects.filter(id=3).first()
        # obj3.r.add(6)
        # obj4 = models.Course.objects.filter(id=4).first()
        # obj4.r.add(4, 5)
        # 添加课程
        # models.Course.objects.create(c_name='Chinese')
        # models.Course.objects.create(c_name='math')
        # models.Course.objects.create(c_name='English')
        # models.Course.objects.create(c_name='history')
        # 添加学校
        # models.School.objects.create(s_name='A school')
        # models.School.objects.create(s_name='B school')
        # 添加学生
        # models.User.objects.create(name='bob', age=3, gender='M', school_id=1)
        # models.User.objects.create(name='jack', age=4, gender='M', school_id=2)
        # models.User.objects.create(name='alice', age=3, gender='F', school_id=1)
        # models.User.objects.create(name='lucy', age=5, gender='F', school_id=2)
        return HttpResponse('done')
