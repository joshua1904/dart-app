from django.views import View
from django.http import JsonResponse
from main.business_logic.utils import get_checkout_suggestion

class CheckoutHintView(View):

    def get(self, request, left_score: int, throws_left: int) -> JsonResponse:
        checkout_suggestion = get_checkout_suggestion(left_score, throws_left)
        return JsonResponse({"checkout_suggestion": checkout_suggestion})