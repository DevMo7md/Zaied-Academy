from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from django.contrib import messages
from django.http import JsonResponse
from .models import MonthlySubscription
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth import update_session_auth_hash
from .decorators import subscription_required
from django.contrib.auth.decorators import login_required
from Subscription.models import *
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from .models import Grade, Student, EmailVerification
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.views.decorators.http import require_POST
import os
from django.core.files.base import ContentFile
import subprocess
import uuid


# Create your views here.
def landing(request):
    return render(request, 'LP_app/landing.html')


def home(request):
    if request.user.is_anonymous:
        return redirect('landing')
    try:
        videos = Lesson.objects.all()
        categories = Category.objects.all()
        # dashboard 
        context = {
            'videos': videos,
            'categories': categories,
        }
        return render(request, 'LP_app/home.html', context)
    except:
        messages.error(request, "الفيديو المطلوب غير موجود!")
        return redirect('home')  # Redirect to main page if video doesn't exist


def lesson (request, foo):
    if request.user.is_anonymous:
        return redirect('landing')
    foo = foo.replace('-', ' ')
    try:
        if request.user.is_superuser or request.user.is_staff:
            category = Category.objects.get(name=foo)
            lessons = Lesson.objects.filter(category=category)
            categories = Category.objects.all()
            if 'search-bar' in request.GET:
                searched = request.GET['search-bar']
                if searched:
                    # Filter products based on the search query
                    lessons = lessons.filter(Q(title__icontains=searched) | Q(discrebtion__icontains=searched) | Q(grade__grade__icontains=searched))
                    if not lessons:
                        err = f'No results for {searched} \n Try checking your spelling or use more general terms'
        
            context = {
                'lessons': lessons,
                'categories': categories,
                'category': category,
            }
        else: 
            student = Student.objects.get(user=request.user)
            grade = student.alsaf
            category = Category.objects.get(name=foo)
            lessons = Lesson.objects.filter(Q(category=category) & Q(grade=grade))
            categories = Category.objects.all()
            if 'search-bar' in request.GET:
                searched = request.GET['search-bar']
                if searched:
                    # Filter products based on the search query
                    lessons = lessons.filter(Q(title__icontains=searched) | Q(discrebtion__icontains=searched))
                    if not lessons:
                        err = f'No results for {searched} \n Try checking your spelling or use more general terms'        
            context = {
                'lessons': lessons,
                'categories': categories,
                'category': category,
                
            }

        return render(request, 'LP_app/lessons.html', context)
    except Student.DoesNotExist:
        messages.error(request, "الطالب غير موجود.")
        return redirect('home')
    except Category.DoesNotExist:
        messages.error(request, "التصنيف المطلوب غير موجود.")
        return redirect('home')
    except Lesson.DoesNotExist:
        messages.error(request, "الدروس غير موجودة.")
        return redirect('home')
    except Exception as e:
        messages.error(request, f"حدث خطأ غير متوقع: {str(e)}")
        return redirect('home')
    

@subscription_required
def video(request, pk):
    if request.user.is_anonymous:
        return redirect('landing')
    
    lesson = Lesson.objects.get(id=pk)
    cat = lesson.category.id
    categories = Category.objects.all()
    grade = lesson.grade.id
    lessons = Lesson.objects.filter(Q(category=cat)&Q(grade=grade)).exclude(id=lesson.id)[:8]

    video = get_object_or_404(Lesson, id=pk)
    video.views += 1  # زيادة عدد المشاهدات
    video.save()

    
    
    context = {
        'lesson':lesson,
        'categories': categories,
        'video':video,
        'lessons':lessons
    }
    return render(request, 'LP_app/video.html', context)



    
def login_page(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # تحقق إذا كان المدخل بريد إلكتروني أو اسم مستخدم
        users = CustomUser.objects.filter(Q(username=username) | Q(email=username))
        if users.exists():
            if users.count() == 1:
                # الحصول على المستخدم الفردي
                user = users.first()
                if not user.is_active:
                    messages.warning(request, "روح على تطبيق ال Gmail هتلاقي لينك دوس عليه علشان تفعل حسابك .")
                    return redirect('login')
            else:
                messages.warning(request, "هناك أكثر من حساب مرتبط بهذه البيانات.")
                return redirect('login')
        else:
            messages.warning(request, "المستخدم غير موجود")
            return redirect('login')

        user = authenticate(request, username=user.username, password=password)
        if user is not None:
            if user.session_token:
                messages.error(request, 'هذا الحساب مسجل الدخول بالفعل على جهاز آخر.')
                return redirect('login')  # أو أعد التوجيه إلى صفحة أخرى حسب الحاجة
            else:
                # إنشاء رمز جلسة جديد
                session_token = uuid.uuid4().hex
                user.session_token = session_token
                user.save()
                
                # تسجيل دخول المستخدم
                login(request, user)
                request.session['session_token'] = session_token
                messages.success(request, "تم تسجيل الدخول بنجاح")
                return redirect('home')  # أعد التوجيه إلى الصفحة الرئيسية بعد تسجيل الدخول بنجاح

        else:
            messages.warning(request, "كلمة المرور خاطئة , يرجى كتابتها صحيحة .")
            return redirect('login')
        
    return render(request, 'LP_app/login.html', {})


def register(request):
    grade = Grade.objects.all()
    if request.method == 'POST':
        username = request.POST['username']
        first_name = request.POST['first_name']
        second_name = request.POST['second_name']
        third_name = request.POST['third_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        phone_num = request.POST['phone_num']
        dad_num = request.POST['dad_num']
        mom_num = request.POST['mom_num']
        school = request.POST['school']
        dad_job = request.POST['dad_job']
        government = request.POST['government']
        alsaf = request.POST['alsaf']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            if CustomUser.objects.filter(Q(username=username) | Q(email=email)).exists():
                messages.error(request, 'عذراً اسم المستخدم او البريد الالكتروتي مستخدم من قبل')
            
            else:
                user = CustomUser.objects.create_user(username=username, email=email, password=password1, first_name=first_name, last_name=last_name)
                user.is_active = False  
                user.save()
                
                # Generate a verification code
                verification_code = get_random_string(length=32)
                EmailVerification.objects.create(user=user, code=verification_code)

                # Send verification email
                verification_link = request.build_absolute_uri(f'/verify-email/?code={verification_code}')
                send_mail(
                    'تأكيد البريد الإلكتروني',
                    f'يرجى تأكيد بريدك الإلكتروني عبر هذا الرابط: {verification_link}',
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                )

                if alsaf:
                    try:
                        grade_instance = Grade.objects.get(id=alsaf)
                    except Grade.DoesNotExist:
                        grade_instance = None
                else:
                    grade_instance = None

                student = Student.objects.create(
                        user=user,
                        first_name=first_name,
                        second_name=second_name,
                        third_name=third_name,
                        last_name=last_name,
                        phone_num=phone_num,
                        dad_num=dad_num,
                        mom_num=mom_num,
                        school=school,
                        dad_job=dad_job,
                        government=government,
                        alsaf=grade_instance,)
                student.save()
                messages.success(request, 'لقد تم انشاء حسابك بنجاح. روح بقا على تطبيق ال Gmail هتلاقي لينك دوس عليه علشان تفعل حسابك .')
                return redirect('login')
        else:
            messages.error(request, 'عذراً كلمة المرور غير متوافقة')
    return render(request, 'LP_app/register.html', {'grade':grade})

def verify_email(request):
    code = request.GET.get('code')
    try:
        verification = EmailVerification.objects.get(code=code)
        user = verification.user
        user.is_active = True
        user.save()
        verification.delete()  # Remove the verification code
        messages.success(request, 'تم تفعيل حسابك بنجاح. يمكنك الآن تسجيل الدخول.')
        return redirect('login')
    except EmailVerification.DoesNotExist:
        messages.error(request, 'رمز التحقق غير صالح أو منتهي الصلاحية.')
        return redirect('login')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        user = CustomUser.objects.filter(email=email).first()
        if user:
            # Generate a verification code
            verification_code = get_random_string(length=32)
            EmailVerification.objects.update_or_create(user=user, code=verification_code)

            # Send verification email
            verification_link = request.build_absolute_uri(f'/reset-password/{verification_code}')
            send_mail(
                'إعادة تعيين كلمة المرور',
                f'استخدم الرابط التالي لإعادة تعيين كلمة المرور: {verification_link}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
            )
            messages.success(request, 'تم إرسال رابط إعادة تعيين كلمة المرور إلى بريدك الإلكتروني.')
            return redirect('login')
        else:
            messages.error(request, 'البريد الإلكتروني غير مسجل.')
    return render(request, 'LP_app/forgot_password.html')

def reset_password(request, code):
    verification = EmailVerification.objects.filter(code=code, is_used=False).first()
    if not verification or (timezone.now() - verification.created_at).days > 1:
        messages.error(request, 'الرابط غير صالح أو قد تم استخدامه.')
        return redirect('forgot_password')

    if request.method == 'POST':
        new_password = request.POST['password1']
        confirm_password = request.POST['password2']
        if new_password == confirm_password:
            verification.user.password = make_password(new_password)
            verification.user.save()
            verification.is_used = True
            verification.save()
            messages.success(request, 'تم إعادة تعيين كلمة المرور بنجاح.')
            return redirect('login')
        else:
            messages.error(request, 'كلمات المرور غير متطابقة.')
    
    return render(request, 'LP_app/reset_password.html', {'code': code})


def logout_user (request):
    user = request.user
    user.session_token = None
    user.save()
    logout(request)
    return redirect('/')



def dashboard(request):
    if request.user.is_anonymous:
        return redirect('landing')
    elif request.user.is_staff :
        if request.method == 'POST' and 'share' in request.POST:
            title = request.POST.get('title')
            lesson_file = request.FILES.get('lesson')
            category_id = request.POST.get('category')
            grade_id = request.POST.get('grade')
            thumnale_image = request.FILES.get('thumnale_image')
            discrebtion = request.POST.get('discrebtion')
            pdf = request.FILES.get('bdf')

            if not title or not lesson_file or not category_id or not thumnale_image or not discrebtion or not grade_id:
                messages.error(request, "يرجى ملء جميع الحقول.")
                return redirect('dashboard')

            try:
                category = Category.objects.get(id=category_id)
                grade = Grade.objects.get(id=grade_id)
            except Category.DoesNotExist:
                messages.error(request, "التصنيف المحدد غير موجود.")
                return redirect('dashboard')

            Lesson.objects.create(
                title=title,
                lesson=lesson_file,
                category=category,
                grade=grade,
                thumnale_image=thumnale_image,
                discrebtion=discrebtion,
                bdf=pdf,
            )

            messages.success(request, 'تم حفظ الدرس بنجاح')
            return redirect('dashboard')

        # الحصول على فيديوهات المدرس المحدد
        lessons = Lesson.objects.all()
        lesson_titles = [lesson.title for lesson in lessons]
        lesson_views = sum([lesson.views for lesson in lessons])  # افترض أن لديك حقل views في نموذج Lesson
        lesson_num = len(lessons)
        categories = Category.objects.all()
        grades = Grade.objects.all()
        students_num = Subscription.objects.filter(end_date__gte=timezone.now() + timedelta(hours=2)).count()

        context = {
            'lesson_titles': lesson_titles,
            'lesson_views': lesson_views,
            'lesson_num': lesson_num,
            'categories': categories,
            'lessonss':lessons,
            'grades':grades,
            'students_num':students_num,
        }
        return render(request, 'LP_app/dashboard.html', context)
    else:
        messages.error(request, 'عذراً, انت هذه الصفحة للمدرس فقط')
        return redirect('home')
    

def stat_dashboard(request):
    if request.user.is_anonymous:
        return redirect('landing')
    if not request.user.is_staff:
        messages.error(request, 'عذراً, انت هذه الصفحة للمدرس فقط')
        return redirect('home')
    else:    
        if request.method == 'POST' and request.user.is_staff and 'update' in request.POST:
            current_month = (timezone.now()+ timedelta(hours=2)).strftime("%d %B %Y")  # الحصول على الشهر الحالي
            new_subscribers = Subscription.objects.filter(end_date__gte=timezone.now() + timedelta(hours=2)).count()  # حساب المشتركين الجدد

            # تحديث الإحصائيات في قاعدة البيانات
            MonthlySubscription.objects.create(
                month=current_month,
                new_subscribers=new_subscribers
            )

        return render(request, 'LP_app/statstic.html')


def get_and_update_subscription_stats(request):
        # جلب بيانات الاشتراكات من قاعدة البيانات
    stats = MonthlySubscription.objects.all().values('month', 'new_subscribers')
    
    # إعداد البيانات للإرجاع كـ JSON
    data = {
        'labels': [item['month'] for item in stats],
        'datasets': [{
            'label': 'عدد المشتركين الجدد',
            'data': [item['new_subscribers'] for item in stats],
            'backgroundColor': "#eeb5ff",
            'borderColor': "#c507ff",
            'borderWidth': 0.5,
        }]
    }
    
    # إعادة البيانات كـ JSON
    return JsonResponse(data)




def edit_lesson(request, pk):
    if request.user.is_anonymous:
        return redirect('landing')
    if not request.user.is_staff:
        messages.error(request, 'عذراً, انت هذه الصفحة للمدرس فقط')
        return redirect('home')
    else:    
        lesson = get_object_or_404(Lesson, pk=pk)
        if request.method == 'POST':
            title = request.POST.get('title')
            lesson_file = request.FILES.get('lesson')
            category_id = request.POST.get('category')
            grade_id = request.POST.get('grade')
            thumnale_image = request.FILES.get('thumnale_image')
            discrebtion = request.POST.get('discrebtion')
            pdf = request.FILES.get('bdf')

            # التحقق من أن جميع الحقول قد تم ملؤها
            if not title or not discrebtion or not category_id:
                messages.error(request, "يرجى ملء جميع الحقول.")
                return redirect('edit_lesson', pk=pk)
            try:
                category = Category.objects.get(id=category_id)
                grade = Grade.objects.get(id=grade_id)
            except Category.DoesNotExist:
                messages.error(request, "التصنيف المحدد غير موجود.")
                return redirect('dashboard')
            

            # تحديث الدرس
            lesson.title = title
            lesson.lesson = lesson_file if lesson_file else lesson.lesson
            lesson.category = category
            lesson.thumnale_image = thumnale_image if thumnale_image else lesson.thumnale_image
            lesson.discrebtion = discrebtion
            lesson.grade = grade
            lesson.bdf = pdf
            lesson.save()

            messages.success(request, 'تم تعديل الفيديو بنجاح')
            return redirect('dashboard')

        # إذا كان الطلب GET، املأ النموذج بالبيانات الحالية
        categories = Category.objects.all()
        grades = Grade.objects.all()

        context = {
            'lesson': lesson,
            'categories': categories,
            'grades':grades,
        }
        return render(request, 'LP_app/edit_lesson.html', context)


def delete_lesson(request, pk):
    if request.user.is_anonymous:
        return redirect('landing')
    if not request.user.is_staff:
        messages.error(request, 'عذراً, انت هذه الصفحة للمدرس فقط')
        return redirect('home')
    else:    
        lesson = get_object_or_404(Lesson, pk=pk)
        
        if request.method == 'POST':
            lesson.delete()
            messages.success(request, 'تم حذف الفيديو بنجاح')
            return redirect('dashboard')

        return render(request, 'LP_app/delete_lesson.html', {'lesson' : lesson})


def teacher_video(request):
    if request.user.is_anonymous:
        return redirect('landing')
    if not request.user.is_staff:
        messages.error(request, 'عذراً, انت هذه الصفحة للمدرس فقط')
        return redirect('home')
    else:    
        categories = Category.objects.all()
        lessons = Lesson.objects.all()
        grades = Grade.objects.all()
        if request.method == 'POST':
            title = request.POST.get('title')
            lesson_file = request.FILES.get('lesson')
            category_id = request.POST.get('category')
            grade_id = request.POST.get('grade')
            thumnale_image = request.FILES.get('thumnale_image')
            discrebtion = request.POST.get('discrebtion')
            pdf = request.FILES.get('pdf')

            if not title or not lesson_file or not category_id or not thumnale_image or not discrebtion:
                messages.error(request, "يرجى ملء جميع الحقول.")
                return redirect('dashboard')

            try:
                category = Category.objects.get(id=category_id)
                grade = Grade.objects.get(id=grade_id)
            except Category.DoesNotExist:
                messages.error(request, "التصنيف المحدد غير موجود.")
                return redirect('dashboard')
            
            lesson = Lesson.objects.create(
                title=title,
                lesson=lesson_file,
                category=category,
                grade=grade,
                thumnale_image=thumnale_image,
                discrebtion=discrebtion,
                bdf=pdf,
            )
            
            lesson.save()
            messages.success(request, 'تم حفظ الدرس بنجاح')
            return redirect('teacher_video')

        context = {
            'lessons':lessons,
            'categories':categories,
            'grades':grades,
        }
        
        return render(request, 'LP_app/teachers_videos.html', context)



def teacher_pdfs(request):
    if request.user.is_anonymous:
        return redirect('landing')
    if not request.user.is_staff:
        messages.error(request, 'عذراً, انت هذه الصفحة للمدرس فقط')
        return redirect('home')
    else:    
        grade = Grade.objects.all()
        pdfs = Pdfs.objects.all()

        if request.method == 'POST':
            title = request.POST.get('title')
            grade_id = request.POST.get('grade')
            thumnale_image = request.FILES.get('thumnale_image')
            pdf = request.FILES.get('pdf')

            if not title or not  thumnale_image or not pdf or not grade_id:
                messages.error(request, "يرجى ملء جميع الحقول.")
                return redirect('dashboard')

            try:
                grade = Grade.objects.get(id=grade_id)
            except Category.DoesNotExist:
                messages.error(request, "التصنيف المحدد غير موجود.")
                return redirect('dashboard')
            
            Pdfs.objects.create(
                name=title,
                grade=grade,
                image=thumnale_image,
                pdf=pdf,
            )
            messages.success(request, 'تم حفظ PDF بنجاح')
            return redirect('teacher_pdf')
            
        context = {
            'grades':grade,
            'pdfs':pdfs,
        }
        
        return render(request, 'LP_app/teacher_pdf.html', context)



def edit_pdf(request, pk):
    if request.user.is_anonymous:
        return redirect('landing')
    if not request.user.is_staff:
        messages.error(request, 'عذراً, انت هذه الصفحة للمدرس فقط')
        return redirect('home')
    else:    
        pdf = get_object_or_404(Pdfs, pk=pk)
        if request.method == 'POST':
            title = request.POST.get('title')
            grade_id = request.POST.get('grade')
            thumnale_image = request.FILES.get('thumnale_image')
            new_pdf = request.FILES.get('bdf')

            # التحقق من أن جميع الحقول قد تم ملؤها
            if not title or not grade_id:
                messages.error(request, "يرجى ملء جميع الحقول.")
                return redirect('edit_pdf', pk=pk)
            try:
                grade = Grade.objects.get(id=grade_id)
            except Grade.DoesNotExist:
                messages.error(request, "التصنيف المحدد غير موجود.")
                return redirect('dashboard')
            

            # تحديث الدرس
            pdf.name = title
            pdf.image = thumnale_image if thumnale_image else pdf.image
            pdf.grade = grade 
            pdf.pdf = new_pdf if new_pdf else pdf.pdf
            pdf.save()

            messages.success(request, 'تم تعديل pdf بنجاح')
            return redirect('dashboard')

        # إذا كان الطلب GET، املأ النموذج بالبيانات الحالية
        grades = Grade.objects.all()

        context = {
            'pdf': pdf,
            'grades':grades,
        }
        return render(request, 'LP_app/edit_pdf.html', context)



def delete_pdf(request, pk):
    if request.user.is_anonymous:
        return redirect('landing')
    if not request.user.is_staff:
        messages.error(request, 'عذراً, انت هذه الصفحة للمدرس فقط')
        return redirect('home')
    else:    
        pdf = get_object_or_404(Pdfs, pk=pk)
        
        if request.method == 'POST':
            pdf.delete()
            messages.success(request, 'تم حذف PDF بنجاح')
            return redirect('dashboard')

        return render(request, 'LP_app/delete_pdf.html', {'pdf' : pdf})


def profile(request, pk):
    # تأكد من أن المستخدم يشاهد ملفه الشخصي فقط
    if request.user.is_anonymous:
        return redirect('landing')
    else:
        if not request.user.is_staff and request.user.id != pk:
            return redirect('home')  # إعادة التوجيه إلى الصفحة الرئيسية إذا حاول المستخدم الوصول إلى ملف شخصي آخر
        else:
            student = get_object_or_404(Student, user__id=pk)
            categories = Category.objects.all()
            try:
                status = Subscription.objects.get(user=student.user)
            except:
                status = False     

        context = {
            'student': student,
            'categories':categories,
            'status':status,
        }
        return render(request, 'LP_app/profile.html', context)
    



def edit_profile(request):
    if request.user.is_anonymous:
        return redirect('landing')
    else:
        if request.method == 'POST':
            # معالجة البيانات المقدمة وتحديث معلومات المستخدم
            
            username = request.POST.get('username')
            email = request.POST.get('email')
            first_name = request.POST.get('first_name')
            second_name = request.POST.get('second_name')
            third_name = request.POST.get('third_name')
            last_name = request.POST.get('last_name')
            phone_num = request.POST.get('phone_num')
            dad_num = request.POST.get('dad_num')
            mom_num = request.POST.get('mom_num')
            school = request.POST.get('school')
            dad_job = request.POST.get('dad_job')
            government = request.POST.get('government')
            alsaf_id = request.POST.get('alsaf')

            # الحصول على المستخدم الحالي
            student = Student.objects.get(user=request.user)

            # تحديث معلومات المستخدم
            user = request.user
            user.username = username
            user.email = email
            user.save()
            

            try:
                alsaf = Grade.objects.get(id=alsaf_id)
            except Grade.DoesNotExist:
                alsaf = None  # أو التعامل مع الحالة حسب الحاجة

            student.first_name = first_name
            student.second_name = second_name
            student.third_name = third_name
            student.last_name = last_name
            student.phone_num = phone_num
            student.dad_num = dad_num
            student.mom_num = mom_num
            student.school = school
            student.dad_job = dad_job
            student.government = government
            student.alsaf = alsaf
            student.save()

            messages.success(request, 'تم تحديث البيانات بنجاح!')
            return redirect('profile', pk=request.user.id)

        # إذا كان الطلب GET، قم بتحميل البيانات الحالية لعرضها في النموذج
        student = Student.objects.get(user=request.user)
        grade = Grade.objects.all()
        context = {
            'student': student,
            'grade': grade,
        }

        return render(request, 'LP_app/edit_user.html', context)

@login_required
@require_POST

def update_profile_picture(request, pk):
    user = request.user
    if request.user.id == pk:
        student = get_object_or_404(Student, user__id=pk)

        # تحقق مما إذا كان هناك صورة مقصوصة مرفوعة
        cropped_image = request.FILES.get('cropped_image')

        if cropped_image:
            student.photo.save(f'{user.username}_profile.jpg', cropped_image)
            student.save()
            messages.success(request, 'تم تحديث الصورة الشخصية بنجاح!')
            return JsonResponse({'success': True, 'new_image_url': student.photo.url})
        else:
            return JsonResponse({'success': False})
    else:
        messages.error(request, "فقط صاحب الملف الشخصي يمكنه تعديل صورته")
        return redirect('home')



def edit_ps(request):
    if request.user.is_anonymous:
        return redirect('landing')
    else:
        if request.method == 'POST':
            old_passw = request.POST.get('old-password')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            if request.user.check_password(old_passw):
                if password1 == password2 :
                    request.user.set_password(password1)
                    request.user.save()

                    # تحديث الجلسة لضمان بقاء المستخدم مسجلاً بعد تغيير كلمة المرور
                    update_session_auth_hash(request, request.user)
                    messages.success(request, "تم تغيير كلمة المرور بنجاح!")
                    return redirect('profile', pk=request.user.id)
                else:
                    messages.error(request, "عذراً. يرجى التأكد من ان حقلا كلمة المرور الجديده متماثلان")
            else:
                messages.error(request, "عذراً. كلمة المرور القديمة غير صحيحة")            

        return render(request, 'LP_app/edit_ps.html')



@subscription_required
def pdfs(request):
    if request.user.is_anonymous:
        return redirect('landing')
    else:
        err = None
        if request.user.is_staff:
            pdfs = Pdfs.objects.all()
            if 'search-bar' in request.GET:
                searched = request.GET['search-bar']
                if searched:
                    # Filter products based on the search query
                    pdfs = pdfs.filter(Q(name__icontains=searched) | Q(grade__grade__icontains=searched))
                    if not pdfs:
                        err = f'للأسف لا يوجد ملف بإسم {searched} يرجى المحاوله بكلمة بحث اقرب'        
        else:
            student = get_object_or_404(Student, user__id=request.user.id)
            student_grade = student.alsaf
            pdfs = Pdfs.objects.filter(grade=student_grade)
            if 'search-bar' in request.GET:
                searched = request.GET['search-bar']
                if searched:
                    # Filter products based on the search query
                    pdfs = pdfs.filter(Q(name__icontains=searched))
                    if not pdfs:
                        err = f'للأسف لا يوجد ملف بإسم {searched} يرجى المحاوله بكلمة بحث اقرب' 

        context =  {
                'pdfs': pdfs,
                'err':err
                }
        return render(request, 'LP_app/books.html',context)
    
def student_teacher(request):
    if request.user.is_anonymous:
        return redirect('landing')
    else:
        if request.user.is_staff :

            subscriped_students = Student.objects.all()
            if 'search-bar' in request.GET:
                searched = request.GET['search-bar']
                if searched:
                    # Filter products based on the search query
                    subscriped_students = subscriped_students.filter(Q(user__username__icontains=searched) | Q(first_name__icontains=searched) | Q(alsaf__grade__icontains=searched) | Q(second_name__icontains=searched) | Q(third_name__icontains=searched) | Q(last_name__icontains=searched) | Q(phone_num__icontains=searched) | Q(dad_num__icontains=searched) | Q(mom_num__icontains=searched) | Q(government__icontains=searched) | Q(school__icontains=searched))
                    if not subscriped_students:
                        err = f'No results for {searched} \n Try checking your spelling or use more general terms'
        
        else:
            messages.warning(request, "هذه الصفحة للمدرس فقط")

        context = {
            'students':subscriped_students,
        }
        return render(request, 'LP_app/student_teacher.html', context)
    