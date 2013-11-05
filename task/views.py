import datetime
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.timezone import utc

import task.models as TaskModels
import task.forms as TaskForms

@login_required
def list_tasks(request):
    tasklists = request.user.tasklists.all()
    for tasklist in tasklists:
        tasklist.completed = tasklist.tasks.filter(completed=True).count()
        tasklist.uncompleted = tasklist.tasks.filter(completed=False).count()
    return render(request, "task/list.html", {"tasklists": tasklists})

@login_required
def add_tasklist(request):
    # Permissions
    return edit_tasklist(request)

@login_required
def edit_tasklist(request, tasklist_id=None):
    # Permissions
    try:
        tasklist = TaskModels.TaskList.objects.get(pk=tasklist_id)
    except TaskModels.TaskList.DoesNotExist:
        tasklist = None

    form = TaskForms.TaskListForm(request.POST or None, instance=tasklist)
    if form.is_valid():
        tasklist = form.save(commit=False)
        if not form.instance.pk:
            # New list, attach user
            tasklist.user = request.user
        tasklist.save()
        return HttpResponseRedirect(reverse('home'))
    return render(request, "task/changelist.html", {"form": form, "tasklist": tasklist})

@login_required
def complete_task(request, task_id):
    # Permissions
    try:
        task = get_object_or_404(TaskModels.Task, pk=task_id)
        task.completed = True
        task.completed_date = datetime.datetime.utcnow().replace(tzinfo=utc)
        task.save()
    except:
        #TODO Return error message
        pass
    return HttpResponseRedirect(reverse('home'))

@login_required
def add_task(request, tasklist_id=None):
    # Permissions
    if tasklist_id:
        tasklist = get_object_or_404(TaskModels.TaskList, pk=tasklist_id)
    return edit_task(request, None, tasklist_id)

@login_required
def edit_task(request, task_id, tasklist_id=None):
    # Permissions
    task = None
    due = None
    if task_id:
        try:
            task = TaskModels.Task.objects.get(pk=task_id)
            tasklist_id = task.tasklist_id
            if task.modified_date != task.due_date:
                due = task.due_date
        except TaskModels.Task.DoesNotExist:
            pass

    form = TaskForms.TaskForm(request.POST or None,
            initial={'tasklist': tasklist_id, 'due_date': due},
            instance=task)
    if form.is_valid():
        task = form.save(commit=False)
        if not form.instance.pk:
            # New instance, attach tasklist id
            task.tasklist_id = tasklist_id
        task.save()
        return HttpResponseRedirect(reverse('home'))
    return render(request, "task/changetask.html", {"form": form, "task": task})

@login_required
def list_triage_category(request):
    # Permissions
    triages = request.user.triages.all()
    return render(request, "task/triages.html", {"triages": triages})

@login_required
def add_triage_category(request):
    # Permissions
    return edit_triage_category(request, None)

@login_required
def edit_triage_category(request, triage_category_id=None):
    # Permissions
    triage = None
    if triage_category_id:
        try:
            triage = TaskModels.TaskTriageCategory.objects.get(pk=triage_category_id)
        except TaskModels.TaskTriageCategory.DoesNotExist:
            pass

    form = TaskForms.TaskTriageCategoryForm(request.POST or None, instance=triage)
    if form.is_valid():
        triage = form.save(commit=False)
        if not form.instance.pk:
            # New instance, attach user
            triage.user = request.user
        triage.save()
        return HttpResponseRedirect(reverse('task:list_triage_category'))
    return render(request, "task/changetriage.html", {"form": form, "triage": triage})
