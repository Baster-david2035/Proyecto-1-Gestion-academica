from django.db import models
from django.contrib.auth.models import User

# Definición del modelo Carrera para representar las carreras o programas académicos de la institución
class Carrera(models.Model):
    
    # Código único que identifica a la carrera (Ej: ISC-01, MED-02). unique=True evita duplicados.
    codigo = models.CharField(max_length=10, unique=True)
    
    # Nombre oficial de la carrera (Ej: Ingeniería en Sistemas de Computación).
    nombre = models.CharField(max_length=100)
    
    # Descripción detallada opcional de la carrera (puede quedar en blanco o nula).
    descripcion = models.TextField(blank=True, null=True)

    # Método especial para definir cómo se representará el objeto en texto (por ejemplo, en el panel de administración)
    def __str__(self):
        return self.nombre


# Definición del modelo Curso para representar las asignaturas o materias que pertenecen a una carrera
class Curso(models.Model):
    
    # Código único del curso (Ej: MAT-101).
    codigo = models.CharField(max_length=10, unique=True)
    
    # Nombre del curso (Ej: Cálculo Diferencial).
    nombre = models.CharField(max_length=100)
    
    # Número de créditos académicos que otorga el curso (utiliza PositiveIntegerField para aceptar solo enteros positivos).
    creditos = models.PositiveIntegerField()
    
    # Relación de muchos a uno (ForeignKey) con el modelo Carrera. 
    # on_delete=models.CASCADE borra los cursos si se elimina la carrera. 
    # related_name='cursos' permite acceder a todos los cursos de una carrera (ej: carrera.cursos.all()).
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE, related_name='cursos')
    
    # Relación de muchos a muchos recursiva ('self') para definir los prerrequisitos de un curso.
    # blank=True permite que un curso no tenga prerrequisitos. symmetrical=False indica que si A es prerrequisito de B, B no es automáticamente prerrequisito de A.
    prerrequisitos = models.ManyToManyField('self', blank=True, symmetrical=False)

    # Método especial para definir la representación en texto del curso
    def __str__(self):
        return f'{self.codigo} - {self.nombre}'


# Definición del modelo PeriodoLectivo para estructurar el año académico en ciclos o periodos (Ej: Ciclo I - 2026)
class PeriodoLectivo(models.Model):
    
    # Nombre del periodo (Ej: Ciclo I - 2026).
    nombre = models.CharField(max_length=50)  
    
    # Fecha de inicio oficial del periodo lectivo.
    fecha_inicio = models.DateField()
    
    # Fecha de finalización del periodo lectivo.
    fecha_fin = models.DateField()
    
    # Indicador booleano para saber si el periodo se encuentra activo actualmente (por defecto True).
    activo = models.BooleanField(default=True)

    # Método especial para definir la representación en texto del periodo
    def __str__(self):
        return self.nombre


# Definición del modelo Grupo para asociar un curso a un periodo lectivo específico, un profesor y un cupo de estudiantes
class Grupo(models.Model):
    
    # Relación con el curso que se imparte en este grupo.
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    
    # Relación con el periodo lectivo en el que se abre el grupo.
    periodo = models.ForeignKey(PeriodoLectivo, on_delete=models.CASCADE)
    
    # Número identificador del grupo (Ej: Grupo 1, Grupo 2). Por defecto es 1.
    numero_grupo = models.PositiveIntegerField(default=1)
    
    # Relación de muchos a uno con el modelo User de Django para asignar al profesor.
    # on_delete=models.SET_NULL deja el campo en null si se elimina el usuario profesor.
    # limit_choices_to restringe las opciones en el admin de Django para que solo se puedan seleccionar usuarios cuyo perfil tenga el rol 'PROFESOR'.
    profesor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'perfilusuario__rol': 'PROFESOR'},
    )
    
    # Capacidad máxima de estudiantes permitidos en el grupo (por defecto 30).
    cupo_maximo = models.PositiveIntegerField(default=30)

    class Meta:
        # Restricción única compuesta para evitar que exista más de un grupo con el mismo número 
        # para un mismo curso dentro del mismo periodo lectivo.
        unique_together = ('curso', 'periodo', 'numero_grupo')

    # Método especial para definir la representación en texto del grupo
    def __str__(self):
        return (f'{self.curso.codigo} - Grupo {self.numero_grupo} ({self.periodo})')