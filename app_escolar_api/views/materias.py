from django.db.models import *
from django.db import transaction
from app_escolar_api.serializers import *
from app_escolar_api.models import *
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import json

class MateriasAll(generics.CreateAPIView):
    # Obtener la lista de todas las materias activas
    # Necesita permisos de autenticación de usuario para poder acceder a la petición
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        materias = Materias.objects.all().order_by("id")
        lista = MateriaSerializer(materias, many=True).data
        for materia in lista:
            if isinstance(materia, dict) and "dias_semana" in materia:
                try:
                    materia["dias_semana"] = json.loads(materia["dias_semana"])
                except Exception:
                    materia["dias_semana"] = []
        return Response(lista, 200)
    
class MateriasView(generics.CreateAPIView):
    # Permisos por método (sobrescribe el comportamiento default)
    # Verifica que el usuario esté autenticado para las peticiones GET, PUT y DELETE
    def get_permissions(self):
        if self.request.method in ['GET', 'PUT', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return []  # POST no requiere autenticación (o puedes requerirla si solo admin puede crear)
    
    #Obtener materia por ID
    def get(self, request, *args, **kwargs):
        materia = get_object_or_404(Materias, id=request.GET.get("id"))
        materia_data = MateriaSerializer(materia, many=False).data
        if isinstance(materia_data, dict) and "dias_semana" in materia_data:
            try:
                materia_data["dias_semana"] = json.loads(materia_data["dias_semana"])
            except Exception:
                materia_data["dias_semana"] = []
        return Response(materia_data, 200)
    
    #Registrar nueva materia
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # Validar que el NRC no exista
        nrc = request.data.get("nrc")
        if Materias.objects.filter(nrc=nrc).exists():
            return Response({"message": "El NRC ya existe en la base de datos"}, 400)
        
        # Validar que hora_inicio sea menor que hora_fin
        hora_inicio = request.data.get("hora_inicio")
        hora_fin = request.data.get("hora_fin")
        if hora_inicio >= hora_fin:
            return Response({"message": "La hora de inicio debe ser menor que la hora de finalización"}, 400)
        
        # Validar que al menos un día esté seleccionado
        dias_semana = request.data.get("dias_semana", [])
        if not dias_semana or len(dias_semana) == 0:
            return Response({"message": "Debe seleccionar al menos un día"}, 400)
        
        materia = Materias.objects.create(
            nrc=request.data["nrc"],
            nombre_materia=request.data["nombre_materia"],
            seccion=request.data["seccion"],
            dias_semana=json.dumps(request.data["dias_semana"]),
            hora_inicio=request.data["hora_inicio"],
            hora_fin=request.data["hora_fin"],
            salon=request.data["salon"],
            programa_educativo=request.data["programa_educativo"],
            profesor_asignado_id=request.data.get("profesor_asignado_id"),
            creditos=request.data["creditos"]
        )
        materia.save()
        return Response({"materia_created_id": materia.id}, 201)
    
    # Actualizar datos de la materia
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        materia = get_object_or_404(Materias, id=request.data["id"])
        
        # Validar que el NRC no exista en otra materia (si se cambió)
        nrc = request.data.get("nrc")
        if nrc != materia.nrc:
            if Materias.objects.filter(nrc=nrc).exists():
                return Response({"message": "El NRC ya existe en la base de datos"}, 400)
        
        # Validar que hora_inicio sea menor que hora_fin
        hora_inicio = request.data.get("hora_inicio")
        hora_fin = request.data.get("hora_fin")
        if hora_inicio >= hora_fin:
            return Response({"message": "La hora de inicio debe ser menor que la hora de finalización"}, 400)
        
        # Validar que al menos un día esté seleccionado
        dias_semana = request.data.get("dias_semana", [])
        if not dias_semana or len(dias_semana) == 0:
            return Response({"message": "Debe seleccionar al menos un día"}, 400)
        
        materia.nrc = request.data["nrc"]
        materia.nombre_materia = request.data["nombre_materia"]
        materia.seccion = request.data["seccion"]
        materia.dias_semana = json.dumps(request.data["dias_semana"])
        materia.hora_inicio = request.data["hora_inicio"]
        materia.hora_fin = request.data["hora_fin"]
        materia.salon = request.data["salon"]
        materia.programa_educativo = request.data["programa_educativo"]
        materia.profesor_asignado_id = request.data.get("profesor_asignado_id")
        materia.creditos = request.data["creditos"]
        materia.save()
        
        return Response({"message": "Materia actualizada correctamente", "materia": MateriaSerializer(materia).data}, 200)
    
    # Eliminar materia con delete (Borrar realmente)
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        materia = get_object_or_404(Materias, id=request.GET.get("id"))
        try:
            materia.delete()
            return Response({"details": "Materia eliminada"}, 200)
        except Exception as e:
            return Response({"details": "Algo pasó al eliminar"}, 400)

class TotalMaterias(generics.CreateAPIView):
    # Contar el total de materias y estadísticas
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request, *args, **kwargs):
        # TOTAL DE MATERIAS
        total_materias = Materias.objects.all().count()
        
        # MATERIAS POR PROGRAMA EDUCATIVO
        programas = [
            'Ingeniería en Ciencias de la Computación',
            'Licenciatura en Ciencias de la Computación',
            'Ingeniería en Tecnologías de la Información'
        ]
        
        materias_por_programa = {}
        for programa in programas:
            count = Materias.objects.filter(programa_educativo=programa).count()
            materias_por_programa[programa] = count
        
        # MATERIAS POR DÍA DE LA SEMANA
        dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        materias_por_dia = {}
        for dia in dias_semana:
            # Contar materias que tienen este día en su array de dias_semana
            count = 0
            materias = Materias.objects.all()
            for materia in materias:
                try:
                    dias = json.loads(materia.dias_semana)
                    if isinstance(dias, list) and dia in dias:
                        count += 1
                except Exception:
                    pass
            materias_por_dia[dia] = count
        
        # Respuesta final
        return Response(
            {
                "total_materias": total_materias,
                "por_programa": materias_por_programa,
                "por_dia": materias_por_dia
            },
            status=200
        )

