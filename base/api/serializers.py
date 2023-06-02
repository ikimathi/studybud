# from django.http import JsonResponse

# def getRoutes(request):
#     routes = [
#         'GET /api',
#         'GET /api/rooms',
#         'GET /api/rooms/:id'
#     ]
#     # 'safe=False' MEANS WE CAN USE MORE THAN JUST PYTHON DICTIONARIES. CONVERTS THE ROUTES LIST INTO JSON DATA
#     return JsonResponse(routes, safe=False)