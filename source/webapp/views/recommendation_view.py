from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse
from django.http import HttpResponseRedirect

from webapp.forms import RecommendationForm
from webapp.models import Recommendation, Player


class RecommendationCreateView(LoginRequiredMixin, CreateView):
    template_name = 'recommendation/recommendation_create.html'
    model = Recommendation
    form_class = RecommendationForm

    def get_success_url(self):
        return reverse('webapp:player_detail', kwargs={'pk': self.object.player.pk})

    def form_valid(self, form):
        args = {}
        player_clubs = get_object_or_404(Player, pk=self.kwargs.get('pk')).clubs.all()
        coach_clubs = self.request.user.clubs.all()
        if list(set(player_clubs) & set(coach_clubs)):
            form.instance.player = get_object_or_404(Player, pk=self.kwargs.get('pk'))
            form.instance.author = self.request.user
            return super().form_valid(form)
        else:
            form = RecommendationForm()
        args['form'] = form
        args['message'] = 'You can add recommendation only for your students!'
        return render(self.request, 'recommendation/recommendation_create.html', args)


class RecommendationUpdateView(PermissionRequiredMixin, UpdateView):
    model = Recommendation
    template_name = 'recommendation/recommendation_update.html'
    form_class = RecommendationForm
    context_object_name = 'recommendation'

    def has_permission(self):
        return self.request.user.has_perm(
            'webapp.change_recommendation') or self.get_object().author == self.request.user

    def get_success_url(self):
        return reverse('webapp:player_detail', kwargs={'pk': self.object.player.pk})


class RecommendationDeleteView(PermissionRequiredMixin, DeleteView):
    model = Recommendation
    context_object_name = 'recommendation'

    def has_permission(self):
        return self.request.user.has_perm(
            'webapp.delete_recommendation') or self.get_object().author == self.request.user

    def get_success_url(self):
        return reverse('webapp:player_detail', kwargs={'pk': self.object.player.pk})

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)
