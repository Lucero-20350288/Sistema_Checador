class Empleado:
  #Agregar numero de casa
  def __init__(self,rfc,nombre,apellido_p, apellido_m,fecha_de_nac,edad,sexo,edo_civil,curp,telefono,calle,colonia,ciudad,estado,cod_pos,num_creden,tipo_horario,estatus):
    self.rfc = rfc
    self.nombre = nombre
    self.apellido_p = apellido_p
    self.apellido_m = apellido_m
    self.edad = edad
    self.fecha_de_nac = fecha_de_nac
    self.sexo = sexo
    self.edo_civil = edo_civil
    self.curp = curp
    self.telefono = telefono
    self.calle = calle
    #self.num_casa = num_casa
    self.colonia = colonia
    self.ciudad = ciudad
    self.estado = estado
    self.cod_pos = cod_pos
    self.num_creden = num_creden
    self.tipo_horario = tipo_horario
    self.estaus = estatus
  
  def toDB(self):
    return{
      '_id': self.rfc,
      'nombre': self.nombre,
      'apellido_paterno': self.apellido_p,
      'apellido_materno': self.apellido_m,
      'fecha_de_nacimiento': self.edad,
      'edad': self.telefono,
      'sexo': self.sexo,
      'estado_civil': self.edo_civil,
      'CURP': self.curp,
      'telefono': self.telefono,
      'calle': self.calle,
      #'numero_de_casa': self.num_casa,
      'colonia': self.colonia,
      'ciudad': self.ciudad,
      'estado': self.estado,
      'codigo_postal': self.cod_pos,
      'numero_de_credencial': self.num_creden,
      'tipo_de_horario': self.tipo_horario,
      'estatus': self.estaus
    }