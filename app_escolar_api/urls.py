from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views.bootstrap import VersionView
from app_escolar_api.views import bootstrap
from app_escolar_api.views import users
from app_escolar_api.views import alumnos
from app_escolar_api.views import maestros
from app_escolar_api.views import materias
from app_escolar_api.views import auth


urlpatterns = [
    #Create Admin
        path('admin/', users.AdminView.as_view()),
    #Admin Data
        path('lista-admins/', users.AdminAll.as_view()),
    #Edit Admin
        #path('admins-edit/', users.AdminsViewEdit.as_view())
     #Create Alumno
        path('alumnos/', alumnos.AlumnosView.as_view()),
    #Create Maestro
        path('maestros/', maestros.MaestrosView.as_view()),
    #Listar Maestros
        path('lista-maestros/', maestros.MaestrosAll.as_view()),
    #Listar Alumnos
        path('lista-alumnos/', alumnos.AlumnosAll.as_view()),
    #Create Materia
        path('materias/', materias.MateriasView.as_view()),
    #Listar Materias
        path('lista-materias/', materias.MateriasAll.as_view()),
    #Total de usuarios
        path('total-usuarios/', users.TotalUsers.as_view()),
    #Total de materias
        path('total-materias/', materias.TotalMaterias.as_view()),
    #Login
        path('login/', auth.CustomAuthToken.as_view()),
    #Logout
        path('logout/', auth.Logout.as_view())
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
