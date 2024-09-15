from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from .models import Question, Choice, UserAnswer
from django.contrib.auth.decorators import login_required
from LP_app.models import *
from django.contrib import messages
from django.db.models import Q
from LP_app.decorators import subscription_required

# Create your views here.
import logging


def quizs_home(request):
    if request.user.is_anonymous:
        return redirect('landing')
    else:
        try:
            quizs = Question.objects.all()
            categories = Category.objects.all()
            
            context = {
                'quizs': quizs,
                'categories': categories,
            }
            return render(request, 'Quizs/quizs_home.html', context)
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            messages.error(request, "الامتحان المطلوب غير موجود!")
            return redirect('home')


def take_quiz_home(request, foo):
    if request.user.is_anonymous:
        return redirect('landing')
    else:
        foo = foo.replace('-', ' ')
        context = {}  # Initialize context dictionary
        category = get_object_or_404(Category, name=foo)


        if request.user.is_superuser or request.user.is_staff:
                
            lessons = Lesson.objects.filter(category=category)
            categories = Category.objects.all()
            if 'search-bar' in request.GET:
                    searched = request.GET['search-bar']
                    if searched:
                        # Filter products based on the search query
                        lessons = lessons.filter(Q(title__icontains=searched) | Q(discrebtion__icontains=searched))
                        if not lessons:
                            err = f'No results for {searched} \n Try checking your spelling or use more general terms'

            context.update({
                'category': category,
                'lessons': lessons,
                'categories': categories,
            })
        else:
            student = get_object_or_404(Student, user=request.user)
            category = get_object_or_404(Category, name=foo)
            grade = student.alsaf
            lessons = Lesson.objects.filter(Q(category=category) & Q(grade=grade))
            categories = Category.objects.all()  # Define categories here as well
            if 'search-bar' in request.GET:
                    searched = request.GET['search-bar']
                    if searched:
                        # Filter products based on the search query
                        lessons = lessons.filter(Q(title__icontains=searched) | Q(discrebtion__icontains=searched))
                        if not lessons:
                            err = f'No results for {searched} \n Try checking your spelling or use more general terms'

            context.update({
                'category': category,
                'lessons': lessons,
                'categories': categories,
            })

        return render(request, 'Quizs/take_quiz_home.html', context)


@login_required
@subscription_required
def take_quiz(request, pk):
    if request.user.is_anonymous:
        return redirect('landing')
    else:

        context = {}  # Initialize context dictionary
        lesson = get_object_or_404(Lesson, id=pk)

        if request.user.is_superuser or request.user.is_staff:
                
            questions = Question.objects.filter(lesson=lesson)
            categories = Category.objects.all()

            if request.method == "POST":
                for question in questions:
                    selected_choice_id = request.POST.get(str(question.id))
                    if selected_choice_id:
                        selected_choice = get_object_or_404(Choice, id=selected_choice_id)
                        UserAnswer.objects.create(user=request.user, question=question, selected_choice=selected_choice)
                return redirect('quiz_results', pk)
            
            context.update({
                'lesson': lesson,
                'questions': questions,
                'categories': categories,
            })
        else:
            student = get_object_or_404(Student, user=request.user)
            lesson = get_object_or_404(Lesson, id=pk)
            grade = student.alsaf
            questions = Question.objects.filter(Q(lesson=lesson) & Q(grade=grade))
            categories = Category.objects.all()  # Define categories here as well

            if request.method == "POST":
                for question in questions:
                    selected_choice_id = request.POST.get(str(question.id))
                    if selected_choice_id:
                        selected_choice = get_object_or_404(Choice, id=selected_choice_id)
                        UserAnswer.objects.create(user=request.user, question=question, selected_choice=selected_choice)
                return redirect('quiz_results', pk)
            
            context.update({
                'lesson': lesson,
                'questions': questions,
                'categories': categories,
            })
            print(questions)
        return render(request, 'Quizs/take_quiz.html', context)



def quiz_results(request, pk):
    if request.user.is_anonymous:
        return redirect('landing')
    else:
        # Retrieve the specific category (quiz) by name
        lesson = get_object_or_404(Lesson, id=pk)
        
        # Filter user answers by the specific category
        user_answers = UserAnswer.objects.filter(user=request.user, question__lesson=lesson)
        
        total_questions = user_answers.count()
        correct_answers = user_answers.filter(selected_choice__is_correct=True).count()
        score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        
        return render(request, 'Quizs/quiz_results.html', {
            'score': score,
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'lesson': lesson,  # Pass category to the template for additional context
        })



def teacher_quiz(request):
    if request.user.is_anonymous:
        return redirect('landing')
    else:
        if request.user.is_superuser or request.user.is_staff:
            questions = Question.objects.all()
            answers = Choice.objects.all()
            categories = Category.objects.all()
            grades = Grade.objects.all()
            lessons = Lesson.objects.all()

            if request.method == 'POST' and 'btn-question' in request.POST :
                #Question
                question = request.POST.get('question')
                lesson_id = request.POST.get('lesson')
                grade_id = request.POST.get('grade')

                try:
                    grade = Grade.objects.get(id=grade_id)
                    lesson = Lesson.objects.get(id=lesson_id)
                    cate = lesson.category

                except:
                    messages.error(request, "التصنيف او الصف او الحصة المحدد غير موجود.")
                    return redirect('dashboard')
                
                Question.objects.create(
                    text=question,
                    category=cate,
                    lesson=lesson,
                    grade=grade
                )
                messages.success(request, 'تم حفظ السؤال بنجاح')
                return redirect('teacher_quiz')
            
            if request.method == 'POST' and 'btn-answer' in request.POST:
                # Choice
                questions_ch_id = request.POST.get('questions-ch')
                choice = request.POST.get('choice')
                is_correct = request.POST.get('is_correct') == 'on'

                try:
                    question_ch = Question.objects.get(id=questions_ch_id)
                except:
                    messages.error(request, "السؤال المحدد غير موجود.")

                Choice.objects.create(
                    question=question_ch,
                    text=choice,
                    is_correct=is_correct
                )    
                messages.success(request, 'تم حفظ الإجابة بنجاح')
                return redirect('teacher_quiz')
            
            if 'search-bar' in request.GET:
                searched = request.GET['search-bar']
                if searched:
                    # Filter products based on the search query
                    questions = questions.filter(Q(lesson__title__icontains=searched) | Q(grade__grade__icontains=searched) | Q(category__name__icontains=searched) | Q(text__icontains=searched))
                    if not questions:
                        err = f'No results for {searched} \n Try checking your spelling or use more general terms'

            context = {
                'lessons':lessons,
                'grades':grades,
                'categories':categories,
                'answers':answers,
                'questions':questions,
            }
            return render(request, 'Quizs/teacher_quiz.html', context)


    
def edit_quiz (request, pk):
    if request.user.is_anonymous:
        return redirect('landing')
    else:
        if not request.user.is_staff:
            messages.error(request, 'عذراً, انت هذه الصفحة للمدرس فقط')
            return redirect('home')
        else:    
            quiz_question = Question.objects.get(id=pk)
            quiz_answers = Choice.objects.filter(question=quiz_question)

            if request.method == 'POST' and 'edited-btn' in request.POST :
                #Question
                question = request.POST.get('question')
                lesson_id = request.POST.get('lesson')
                grade_id = request.POST.get('grade')

                #Coices

                try:
                    grade = Grade.objects.get(id=grade_id)
                    lesson = Lesson.objects.get(id=lesson_id)
                except:
                    messages.error(request, "التصنيف او الصف او الحصة المحددة غير موجود.")
                    return redirect('teacher_quiz')
                
                quiz_question.text = question
                quiz_question.category = lesson.category           
                quiz_question.lesson = lesson
                quiz_question.grade = grade
                quiz_question.save()
                # success message
                messages.success(request, 'تم تعديل السؤال بنجاح')
                return redirect('teacher_quiz')

                    # إذا كان الطلب GET، املأ النموذج بالبيانات الحالية
            categories = Category.objects.all()
            grades = Grade.objects.all()
            lessons = Lesson.objects.all()
            
            context = {
            'lessons':lessons,
            'grades':grades,
            'categories':categories,
            'questions':quiz_question,
            'quiz_answers':quiz_answers,
            'cat':quiz_question.category,
            }
            return render(request, 'Quizs/quiz_edit.html', context)


def edit_choice(request, pk):
    if request.user.is_anonymous:
        return redirect('landing')
    else:
        if not request.user.is_staff:
            messages.error(request, 'عذراً, انت هذه الصفحة للمدرس فقط')
            return redirect('home')
        else:    
            choice = Choice.objects.get(id=pk)
            if request.method == 'POST':
                answer = request.POST.get('choice')
                question_id = request.POST.get('question')
                is_correct = request.POST.get('is_correct') == 'on'

                try:
                    question = Question.objects.get(id=question_id)
                except:
                    messages.error(request, "السؤال المحدد غير موجود.")

                choice.text = answer
                choice.question = question
                choice.is_correct = is_correct
                choice.save()
                # success message
                messages.success(request, 'تم تعديل الخيار بنجاح')
                return redirect('teacher_quiz')
            questions = Question.objects.all()
            context = {
                'choice':choice,
                'questions':questions,
            }
            return render(request, 'Quizs/edit_choice.html', context)


@login_required
def delete_quiz(request, pk):
    if request.user.is_anonymous:
        return redirect('landing')
    else:
        if not request.user.is_staff:
            messages.error(request, 'عذراً, انت هذه الصفحة للمدرس فقط')
            return redirect('home')
        else:    
            question = get_object_or_404(Question, id=pk)
            if request.method == 'POST':
                question.delete()
                messages.success(request, 'تم حذف الامتحان بنجاح')
                return redirect('teacher_quiz')
            return render(request, 'Quizs/delete_quiz.html')