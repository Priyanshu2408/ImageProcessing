from rest_framework.views import APIView
from rest_framework.response import Response
from ImageProcessing.Managers.CsvManager import CsvManager


class HealthCheckView(APIView):
    def get(self, request, version_id):
        '''HEALTH CHECK'''
        data = {"message":"Everything is ok!"}
        data.update({"success":True})
        return Response(
           data
        ,200)

class UploadAPIView(APIView):
    def post(self, request, version_id):
        '''CSV validations and uploading'''
        csv_file = request.FILES.get('file')
        csv_manager = CsvManager()
        return csv_manager.validate_and_process_csv_file(csv_file)
        
        
        


